/* Peta isu 3D (WebGL). Dimuat lazy oleh IssueMap; hanya menggambar dan melaporkan interaksi.
 * Hub = bola sebesar volume ulasan, titik kecil = isu terbuka, garis samar = hub berbagi aspek. */
import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef, useState } from "react";
import ForceGraph3D, { type ForceGraphMethods, type LinkObject, type NodeObject } from "react-force-graph-3d";
import * as THREE from "three";
import { clipLabel, groupVolume, hubRadius, type Group, type MapFinding } from "@/lib/insight-model";
import { hubColor, leafColor, openIssue, TOP_LABELS_3D, type MapCanvasHandle, type MapCanvasProps } from "./map-shared";

type HubNode = { id: string; kind: "hub"; key: string; group: Group; radius: number };
type IssueNode = { id: string; kind: "issue"; key: string; finding: MapFinding; radius: number };
type MapNode = NodeObject<HubNode | IssueNode>;
type MapLink = LinkObject<MapNode, { kind: "spoke" | "shared"; a: string; b: string; length: number }>;
type Graph = ForceGraphMethods<MapNode, MapLink>;

interface Orbit {
  autoRotate: boolean;
  autoRotateSpeed: number;
  enableDamping: boolean;
  dampingFactor: number;
  minDistance: number;
  maxDistance: number;
  target: THREE.Vector3;
}

interface Entry {
  key: string; // kunci hub pemilik
  hub: boolean;
  materials: THREE.Material[];
  textures: THREE.Texture[];
  label?: THREE.Sprite;
  /** Lebar/tinggi label dalam piksel layar (sprite berukuran tetap). */
  labelPx?: { w: number; h: number };
  /** Label diminta tampil (sebelum disaring agar tidak bertumpuk). */
  want?: boolean;
  node?: MapNode;
  halo?: THREE.Sprite;
  sphere: THREE.MeshStandardMaterial;
}

const HEIGHT_FALLBACK = 520;
// Radius dunia tempat hub boleh berada sebelum ditarik balik (lihat gaya gravity).
const BOUND = 200;
const IDLE_MS = 6000;
const FLY_MS = 800;

/* --- warna dari CSS ------------------------------------------------------------------------- */

interface Palette {
  dark: boolean;
  resolve(css: string): string;
  ink: string;
  surface: string;
  accent: string;
}

function makePalette(el: HTMLElement): Palette {
  const dark = document.documentElement.dataset.theme === "dark";
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 1;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const cache = new Map<string, string>();
  const raw = (css: string) => {
    const probe = document.createElement("span");
    probe.style.display = "none";
    probe.style.color = css;
    el.appendChild(probe);
    const computed = getComputedStyle(probe).color;
    probe.remove();
    if (!ctx) return "#8a8f9c";
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = "#8a8f9c";
    ctx.fillStyle = computed;
    ctx.fillRect(0, 0, 1, 1);
    const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
    return "#" + [r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("");
  };
  const ink = raw("var(--ink)");
  const surface = raw("var(--map-surface)");
  const accent = raw("var(--blue)");
  const inkColor = new THREE.Color(ink);
  return {
    dark,
    ink,
    surface,
    accent,
    resolve(css: string) {
      let hit = cache.get(css);
      if (!hit) {
        // Di tema terang, gelapkan sedikit supaya bola tetap kontras di atas latar pucat.
        hit = dark ? raw(css) : "#" + new THREE.Color(raw(css)).lerp(inkColor, 0.14).getHexString();
        cache.set(css, hit);
      }
      return hit;
    },
  };
}

function rgba(hex: string, alpha: number) {
  const c = new THREE.Color(hex);
  return `rgba(${Math.round(c.r * 255)},${Math.round(c.g * 255)},${Math.round(c.b * 255)},${alpha})`;
}

const noRaycast = () => {};

/** Ukuran piksel sprite tanpa atenuasi: tinggi layar = scale.y × (1 / tan(fov/2)) × tinggi/2. */
function labelPixels(sprite: THREE.Sprite, viewHeight: number, fov = 50) {
  const k = 1 / Math.tan(((fov / 2) * Math.PI) / 180);
  const h = sprite.scale.y * k * (viewHeight / 2);
  return { w: (h * sprite.scale.x) / sprite.scale.y, h };
}

/* --- tekstur sprite ------------------------------------------------------------------------- */

let haloTexture: THREE.Texture | null = null;
function getHalo() {
  if (haloTexture) return haloTexture;
  const size = 128;
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d")!;
  const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  gradient.addColorStop(0, "rgba(255,255,255,0.9)");
  gradient.addColorStop(0.35, "rgba(255,255,255,0.35)");
  gradient.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);
  haloTexture = new THREE.CanvasTexture(canvas);
  haloTexture.colorSpace = THREE.SRGBColorSpace;
  return haloTexture;
}

function makeLabel(text: string, palette: Palette) {
  const scale = 2;
  const fontSize = 13 * scale;
  const font = `600 ${fontSize}px Geist, system-ui, sans-serif`;
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d")!;
  ctx.font = font;
  const padX = 9 * scale;
  const height = 24 * scale;
  const width = Math.ceil(ctx.measureText(text).width + padX * 2);
  canvas.width = width;
  canvas.height = height;
  ctx.font = font;
  const radius = height / 2;
  ctx.beginPath();
  ctx.moveTo(radius, 0);
  ctx.arcTo(width, 0, width, height, radius);
  ctx.arcTo(width, height, 0, height, radius);
  ctx.arcTo(0, height, 0, 0, radius);
  ctx.arcTo(0, 0, width, 0, radius);
  ctx.closePath();
  ctx.fillStyle = rgba(palette.surface, palette.dark ? 0.82 : 0.9);
  ctx.fill();
  ctx.lineWidth = scale;
  ctx.strokeStyle = rgba(palette.ink, 0.16);
  ctx.stroke();
  ctx.fillStyle = palette.ink;
  ctx.textBaseline = "middle";
  ctx.fillText(text, padX, height / 2 + scale * 0.5);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false, depthWrite: false });
  const sprite = new THREE.Sprite(material);
  // Ukuran tetap di layar (tidak mengecil saat kamera menjauh): ~22px tinggi pada kanvas 520px.
  material.sizeAttenuation = false;
  const screenHeight = 0.042;
  sprite.scale.set((screenHeight * width) / height, screenHeight, 1);
  sprite.center.set(0.5, -0.25);
  sprite.renderOrder = 10;
  sprite.raycast = noRaycast; // label tidak menangkap hover; hanya bola yang interaktif
  return { sprite, material, texture };
}

/* --- komponen ------------------------------------------------------------------------------- */

const IssueMap3D = forwardRef<MapCanvasHandle, MapCanvasProps>(function IssueMap3D(
  { groups, links, colorBy, labels, selected, focusSeq, summary, reducedMotion, onSelect, onHover },
  ref,
) {
  const wrap = useRef<HTMLDivElement>(null);
  const graph = useRef<Graph | undefined>(undefined);
  const [size, setSize] = useState({ w: 0, h: HEIGHT_FALLBACK });
  const [palette, setPalette] = useState<Palette | null>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const registry = useRef(new Map<string, Entry>());
  const positions = useRef(new Map<string, { x: number; y: number; z: number }>());
  const pointer = useRef({ x: 0, y: 0 });
  const hoverNode = useRef<MapNode | null>(null);
  const idle = useRef<number | undefined>(undefined);
  const fitted = useRef(false);
  const state = useRef({ selected, hovered, labels, top: new Set<string>() });

  const top = useMemo(
    () => new Set(groups.filter((g) => g.findings.length > 0).slice(0, TOP_LABELS_3D).map((g) => g.key)),
    [groups],
  );
  state.current = { selected, hovered, labels, top };

  // Ukuran dari wadah.
  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const measure = () => setSize({ w: el.clientWidth, h: el.clientHeight || HEIGHT_FALLBACK });
    measure();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Warna dibaca dari CSS saat mulai dan setiap kali tema berganti.
  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    setPalette(makePalette(el));
    let frame = 0;
    const observer = new MutationObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => setPalette(makePalette(el)));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
    };
  }, []);

  const data = useMemo(() => {
    const maxVolume = groups.reduce((m, g) => Math.max(m, groupVolume(g)), 0);
    const nodes: MapNode[] = [];
    const edges: MapLink[] = [];
    const seed = (id: string) => positions.current.get(id) ?? {};
    for (const group of groups) {
      const n = group.findings.length;
      const radius = hubRadius(groupVolume(group), maxVolume, n ? 6 : 4.5, n ? 18 : 11);
      const hubId = "h:" + group.key;
      nodes.push({ id: hubId, kind: "hub", key: group.key, group, radius, ...seed(hubId) });
      for (const finding of group.findings) {
        const id = "f:" + group.key + ":" + finding.id;
        const r = 1.5 + Math.min(2.2, Math.sqrt(Math.max(0, finding.support)) * 0.45);
        nodes.push({ id, kind: "issue", key: group.key, finding, radius: r, ...seed(id) });
        edges.push({ source: hubId, target: id, kind: "spoke", a: group.key, b: group.key, length: radius + 14 + r * 2 });
      }
    }
    for (const [i, j] of links) {
      const a = groups[i];
      const b = groups[j];
      if (!a || !b) continue;
      edges.push({ source: "h:" + a.key, target: "h:" + b.key, kind: "shared", a: a.key, b: b.key, length: 70 });
    }
    return { nodes, links: edges };
  }, [groups, links]);

  // Terapkan redup/label tanpa membuat ulang objek.
  const apply = useCallback(() => {
    const { selected: sel, hovered: hov, labels: showLabels, top: topSet } = state.current;
    for (const entry of registry.current.values()) {
      const related = !sel || entry.key === sel;
      const opacity = related ? 1 : 0.14;
      for (const material of entry.materials) {
        material.opacity = opacity * ((material.userData.base as number | undefined) ?? 1);
        material.transparent = true;
      }
      if (entry.label) {
        entry.want = entry.key === hov || entry.key === sel || (showLabels && topSet.has(entry.key) && related);
      }
    }
    cull();
    // cull stabil (hanya membaca ref)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Label tidak boleh saling tumpuk di layar: yang paling penting (hover, terpilih, lalu urutan
  // urgensi) menang, sisanya disembunyikan sampai kamera berputar dan ruangnya kosong lagi.
  const cull = useCallback(() => {
    const fg = graph.current;
    const { selected: sel, hovered: hov, top: topSet } = state.current;
    const rank = (key: string) => (key === hov ? -2 : key === sel ? -1 : [...topSet].indexOf(key));
    const wanted = [...registry.current.values()]
      .filter((e) => e.label && e.hub)
      .sort((a, b) => rank(a.key) - rank(b.key));
    const boxes: { x0: number; x1: number; y0: number; y1: number }[] = [];
    for (const entry of wanted) {
      const label = entry.label!;
      const node = entry.node;
      if (!entry.want || !fg || !node || node.x == null || node.y == null || node.z == null || !entry.labelPx) {
        label.visible = !!entry.want && !fg;
        continue;
      }
      const p = fg.graph2ScreenCoords(node.x, node.y, node.z);
      const { w, h } = entry.labelPx;
      const box = { x0: p.x - w / 2 - 4, x1: p.x + w / 2 + 4, y0: p.y - h * 1.6, y1: p.y - h * 0.2 };
      const clash = boxes.some((b) => b.x0 < box.x1 && box.x0 < b.x1 && b.y0 < box.y1 && box.y0 < b.y1);
      const forced = entry.key === hov || entry.key === sel;
      label.visible = forced || !clash;
      if (label.visible) boxes.push(box);
    }
  }, []);

  useEffect(() => {
    const id = window.setInterval(() => {
      if (!document.hidden) cull();
    }, 180);
    return () => window.clearInterval(id);
  }, [cull]);

  useEffect(apply, [apply, selected, hovered, labels, top]);

  const nodeObject = useCallback(
    (node: MapNode) => {
      const prev = registry.current.get(node.id as string);
      if (prev) {
        prev.materials.forEach((m) => m.dispose());
        prev.textures.forEach((t) => t.dispose());
      }
      if (!palette) return new THREE.Object3D();
      const root = new THREE.Group();
      const css = node.kind === "hub" ? hubColor(node.group, colorBy) : leafColor(node.finding, colorBy);
      const color = new THREE.Color(palette.resolve(css));
      const sphere = new THREE.MeshStandardMaterial({
        color,
        emissive: color,
        emissiveIntensity: palette.dark ? (node.kind === "hub" ? 0.5 : 0.7) : node.kind === "hub" ? 0.12 : 0.18,
        roughness: 0.35,
        metalness: 0.1,
        transparent: true,
      });
      sphere.userData.base = 1;
      const mesh = new THREE.Mesh(node.kind === "hub" ? hubGeometry : issueGeometry, sphere);
      mesh.scale.setScalar(node.radius);
      root.add(mesh);
      const entry: Entry = { key: node.key, hub: node.kind === "hub", materials: [sphere], textures: [], sphere, node };
      if (node.kind === "hub" && node.group.findings.length > 0) {
        const haloMaterial = new THREE.SpriteMaterial({
          map: getHalo(),
          color,
          transparent: true,
          depthWrite: false,
          blending: palette.dark ? THREE.AdditiveBlending : THREE.NormalBlending,
        });
        haloMaterial.userData.base = palette.dark ? (node.group.worst === "recurrence" ? 0.55 : 0.38) : 0.2;
        const halo = new THREE.Sprite(haloMaterial);
        halo.raycast = noRaycast;
        halo.scale.setScalar(node.radius * (node.group.worst === "recurrence" ? 3.6 : 3));
        root.add(halo);
        entry.halo = halo;
        entry.materials.push(haloMaterial);
      }
      if (node.kind === "hub") {
        const { sprite, material, texture } = makeLabel(clipLabel(node.group.label, 22), palette);
        sprite.position.set(0, node.radius, 0);
        material.userData.base = 1;
        root.add(sprite);
        entry.label = sprite;
        entry.labelPx = labelPixels(sprite, size.h);
        entry.materials.push(material);
        entry.textures.push(texture);
      }
      registry.current.set(node.id as string, entry);
      queueMicrotask(apply);
      return root;
    },
    [palette, colorBy, apply, size.h],
  );

  const linkColor = useCallback(
    (link: MapLink) => {
      if (!palette) return "rgba(0,0,0,0)";
      const lit = !selected || link.a === selected || link.b === selected;
      if (link.kind === "shared") {
        if (selected && lit) return rgba(palette.accent, palette.dark ? 0.55 : 0.5);
        return rgba(palette.dark ? palette.accent : palette.ink, selected ? 0.03 : palette.dark ? 0.09 : 0.06);
      }
      return rgba(palette.ink, lit ? (palette.dark ? 0.26 : 0.3) : 0.05);
    },
    [palette, selected],
  );

  // Gaya tarik/tolak: isu menempel dekat hubnya, hub saling menjauh, tautan aspek menarik pelan.
  useEffect(() => {
    const fg = graph.current;
    if (!fg) return;
    const link = fg.d3Force("link");
    link?.distance?.((l: MapLink) => l.length).strength?.((l: MapLink) => (l.kind === "spoke" ? 0.9 : 0.015));
    const charge = fg.d3Force("charge");
    charge?.strength?.((n: MapNode) => (n.kind === "hub" ? -220 - n.radius * 9 : -6));
    charge?.distanceMax?.(520);
    // Tarikan lembut ke pusat supaya hub tanpa tautan (mis. produk sehat) tidak hanyut jauh.
    let pool: MapNode[] = [];
    const gravity = Object.assign(
      (alpha: number) => {
        for (const n of pool) {
          if (n.kind !== "hub" || n.x == null || n.y == null || n.z == null) continue;
          // Tarikan dasar + batas lunak: hub tanpa tautan tidak boleh hanyut jauh dari gugus utama.
          const d = Math.hypot(n.x, n.y, n.z) || 1;
          const k = 0.035 * alpha + (d > BOUND ? ((d - BOUND) / d) * 0.4 * alpha : 0);
          n.vx = (n.vx ?? 0) - n.x * k;
          n.vy = (n.vy ?? 0) - n.y * k;
          n.vz = (n.vz ?? 0) - n.z * k;
        }
      },
      { initialize: (nodes: MapNode[]) => (pool = nodes) },
    );
    fg.d3Force("gravity", gravity);
    fitted.current = false;
    fg.d3ReheatSimulation();
    // Cadangan bila simulasi belum berhenti: tetap bingkai seluruh peta setelah sebentar.
    const timer = window.setTimeout(() => {
      if (fitted.current || !graph.current) return;
      // Tanpa frame (tab tersembunyi) posisi objek belum bergerak; biarkan onEngineStop membingkai.
      const box = graph.current.getGraphBbox();
      if (!box || box.x[1] - box.x[0] < 20) return;
      fitted.current = true;
      if (state.current.selected) fly(state.current.selected);
      else fitAll(reducedMotion ? 0 : 600);
    }, 3000);
    return () => window.clearTimeout(timer);
    // `fly` sengaja tidak jadi dependensi: simulasi hanya dipanaskan ulang saat data berubah.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, size.w > 0, palette != null]);

  // Putar pelan saat diam; berhenti saat disentuh, lanjut setelah 6 detik.
  const orbit = () => graph.current?.controls() as unknown as Orbit | undefined;
  const pause = useCallback(() => {
    const controls = orbit();
    if (controls) controls.autoRotate = false;
    window.clearTimeout(idle.current);
  }, []);
  const resumeLater = useCallback(() => {
    window.clearTimeout(idle.current);
    if (reducedMotion) return;
    idle.current = window.setTimeout(() => {
      const controls = orbit();
      if (controls && !hoverNode.current) controls.autoRotate = true;
    }, IDLE_MS);
  }, [reducedMotion]);

  useEffect(() => {
    const controls = orbit();
    if (!controls) return;
    controls.enableDamping = true;
    controls.dampingFactor = 0.12;
    controls.autoRotateSpeed = 0.55;
    controls.minDistance = 30;
    controls.maxDistance = 2400;
    controls.autoRotate = !reducedMotion;
    return () => window.clearTimeout(idle.current);
  }, [size.w > 0, palette != null, reducedMotion]);

  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const touch = () => {
      pause();
      resumeLater();
    };
    const move = (event: PointerEvent) => {
      const rect = el.getBoundingClientRect();
      pointer.current = { x: event.clientX - rect.left, y: event.clientY - rect.top };
      const node = hoverNode.current;
      if (node) onHover(node.kind === "hub" ? { group: node.group, ...pointer.current } : { finding: node.finding, ...pointer.current });
    };
    const leave = () => {
      hoverNode.current = null;
      setHovered(null);
      onHover(null);
    };
    el.addEventListener("pointerdown", touch);
    el.addEventListener("wheel", touch, { passive: true });
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerleave", leave);
    return () => {
      el.removeEventListener("pointerdown", touch);
      el.removeEventListener("wheel", touch);
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerleave", leave);
    };
  }, [onHover, pause, resumeLater]);

  // Hemat GPU: berhenti menggambar saat peta keluar layar.
  useEffect(() => {
    const el = wrap.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    const observer = new IntersectionObserver(([entry]) => {
      const fg = graph.current;
      if (!fg) return;
      if (entry.isIntersecting) fg.resumeAnimation();
      else fg.pauseAnimation();
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [size.w > 0]);

  // Bersihkan sumber daya milik kita saat dilepas (renderer dibuang oleh pustaka).
  useEffect(
    () => () => {
      window.clearTimeout(idle.current);
      for (const entry of registry.current.values()) {
        entry.materials.forEach((m) => m.dispose());
        entry.textures.forEach((t) => t.dispose());
      }
      registry.current.clear();
      graph.current?.pauseAnimation();
    },
    [],
  );

  const fly = useCallback(
    (key: string) => {
      const fg = graph.current;
      const node = data.nodes.find((n) => n.id === "h:" + key);
      if (!fg || !node || node.x == null || node.y == null || node.z == null) return;
      const target = new THREE.Vector3(node.x, node.y, node.z);
      const camera = fg.camera().position.clone();
      const dir = camera.sub(target);
      if (dir.lengthSq() < 1) dir.set(0, 0, 1);
      dir.normalize();
      const distance = 70 + node.radius * 5;
      const to = target.clone().add(dir.multiplyScalar(distance));
      fg.cameraPosition({ x: to.x, y: to.y, z: to.z }, { x: target.x, y: target.y, z: target.z }, reducedMotion ? 0 : FLY_MS);
    },
    [data, reducedMotion],
  );


  // Bingkai seluruh peta: bola pembungkus semua node, jarak kamera dari FOV tersempit (vertikal/horizontal).
  // zoomToFit bawaan membingkai terlalu longgar saat label sprite ikut terhitung.
  const fitAll = useCallback(
    (ms: number) => {
      const fg = graph.current;
      const pts = data.nodes.filter((n) => n.x != null && n.y != null && n.z != null);
      if (!fg || !pts.length) return;
      const center = new THREE.Vector3();
      for (const n of pts) center.add(new THREE.Vector3(n.x, n.y, n.z));
      center.divideScalar(pts.length);
      let radius = 1;
      for (const n of pts)
        radius = Math.max(radius, center.distanceTo(new THREE.Vector3(n.x, n.y, n.z)) + (n.kind === "hub" ? n.radius : 2));
      const camera = fg.camera() as THREE.PerspectiveCamera;
      const vfov = ((camera.fov ?? 50) * Math.PI) / 180;
      const hfov = 2 * Math.atan(Math.tan(vfov / 2) * (size.w / Math.max(1, size.h)));
      const distance = (radius / Math.sin(Math.min(vfov, hfov) / 2)) * 1.02;
      const dir = camera.position.clone().sub(center);
      if (dir.lengthSq() < 1) dir.set(0, 0, 1);
      dir.normalize();
      const to = center.clone().add(dir.multiplyScalar(distance));
      fg.cameraPosition({ x: to.x, y: to.y, z: to.z }, { x: center.x, y: center.y, z: center.z }, ms);
    },
    [data, size.w, size.h],
  );

  useEffect(() => {
    if (selected) fly(selected);
  }, [selected, focusSeq, fly]);

  useImperativeHandle(
    ref,
    () => {
      const dolly = (factor: number) => {
        const fg = graph.current;
        const controls = orbit();
        if (!fg || !controls) return;
        pause();
        resumeLater();
        const target = controls.target.clone();
        const to = fg.camera().position.clone().sub(target).multiplyScalar(factor).add(target);
        fg.cameraPosition({ x: to.x, y: to.y, z: to.z }, { x: target.x, y: target.y, z: target.z }, reducedMotion ? 0 : 300);
      };
      return {
        zoomIn: () => dolly(0.72),
        zoomOut: () => dolly(1.38),
        fit: () => {
          fitAll(reducedMotion ? 0 : FLY_MS);
          resumeLater();
        },
      };
    },
    [pause, resumeLater, reducedMotion, fitAll],
  );

  return (
    <div className="map3d-canvas map3d-canvas--gl" ref={wrap} role="img" aria-label={summary}>
      {size.w > 0 && palette && (
        <ForceGraph3D<MapNode, MapLink>
          ref={graph}
          graphData={data}
          width={size.w}
          height={size.h}
          backgroundColor="rgba(0,0,0,0)"
          showNavInfo={false}
          controlType="orbit"
          nodeId="id"
          nodeLabel={() => ""}
          nodeThreeObject={nodeObject}
          linkColor={linkColor}
          linkOpacity={1}
          linkWidth={0}
          enableNodeDrag={false}
          warmupTicks={80}
          cooldownTicks={160}
          cooldownTime={Infinity}
          d3VelocityDecay={0.35}
          onEngineStop={() => {
            for (const n of data.nodes)
              if (n.x != null && n.y != null && n.z != null) positions.current.set(n.id as string, { x: n.x, y: n.y, z: n.z });
            // Bingkai ulang saat simulasi selesai, walau cadangan 3 detik sudah membingkai posisi sementara.
            fitted.current = true;
            if (state.current.selected) fly(state.current.selected);
            else fitAll(reducedMotion ? 0 : 600);
          }}
          onNodeHover={(node) => {
            hoverNode.current = node;
            setHovered(node ? node.key : null);
            if (node) {
              pause();
              onHover(node.kind === "hub" ? { group: node.group, ...pointer.current } : { finding: node.finding, ...pointer.current });
            } else {
              onHover(null);
              resumeLater();
            }
          }}
          onNodeClick={(node) => {
            if (node.kind === "issue") openIssue(node.finding);
            else onSelect(selected === node.key ? null : node.key);
          }}
          onBackgroundClick={() => onSelect(null)}
        />
      )}
    </div>
  );
});

const hubGeometry = new THREE.SphereGeometry(1, 36, 24);
const issueGeometry = new THREE.SphereGeometry(1, 16, 12);

export default IssueMap3D;
