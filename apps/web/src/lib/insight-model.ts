/* Model data untuk peta isu, grafik per kanal, dan sebaran bintang. Semua fungsi murni supaya
 * bisa diuji tanpa DOM; komponen hanya menggambar hasilnya. */

export type Bucket = "recurrence" | "needs_fact" | "to_do" | "monitoring";
export type GroupBy = "product" | "aspect" | "type" | "channel";

export interface MapFinding {
  id: string;
  product_id: string;
  product_title: string;
  channel: string;
  attribute: string;
  attribute_local: string;
  finding_type: string;
  severity: string;
  bucket: string;
  support: number;
  denominator: number;
  aspect: string;
}
export interface MapProduct {
  id: string;
  title: string;
  channel: string;
  image_url?: string | null;
  reviews: number;
  rating: number | null;
}
export interface Landscape {
  channels: string[];
  volume_by_channel: Record<string, number | string>[];
  evidence_by_channel: Record<string, number | string>[];
  ratings_by_channel: Record<string, number[]>;
  ratings_window_by_channel: Record<string, number[]>;
  map: { products: MapProduct[]; findings: MapFinding[] };
}

/** Urutan kanal global = urutan slot warna. Warna mengikuti kanal, bukan peringkatnya. */
export const CHANNEL_ORDER = ["woocommerce", "lazada", "tokopedia", "shopee", "tiktok", "blibli", "manual"];
export const CHANNEL_LABEL: Record<string, string> = {
  woocommerce: "WooCommerce",
  lazada: "Lazada",
  tokopedia: "Tokopedia",
  shopee: "Shopee",
  tiktok: "TikTok Shop",
  blibli: "Blibli",
  manual: "Manual",
  sample: "Sample",
};
export function channelColor(channel: string) {
  const slot = CHANNEL_ORDER.indexOf(channel);
  return slot < 0 ? "var(--series-other)" : `var(--series-${slot + 1})`;
}
export function channelLabel(channel: string) {
  return CHANNEL_LABEL[channel] ?? channel;
}
export function sortChannels(channels: string[]) {
  const rank = (c: string) => (CHANNEL_ORDER.includes(c) ? CHANNEL_ORDER.indexOf(c) : 99);
  return [...channels].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
}

export const BUCKETS: Bucket[] = ["recurrence", "needs_fact", "to_do", "monitoring"];
export const URGENCY: Record<Bucket, { color: string; key: string; hint: string; weight: number }> = {
  recurrence: { color: "var(--status-critical)", key: "urgent", hint: "urgentHint", weight: 8 },
  needs_fact: { color: "var(--status-warning)", key: "waiting", hint: "waitingHint", weight: 4 },
  to_do: { color: "var(--status-info)", key: "ready", hint: "readyHint", weight: 2 },
  monitoring: { color: "var(--status-good)", key: "watching", hint: "watchingHint", weight: 0 },
};
export function urgencyColor(bucket: string) {
  return URGENCY[bucket as Bucket]?.color ?? "var(--muted)";
}

/** Bintang: divergen merah↔biru dengan titik tengah abu, supaya 3★ tidak terbaca baik/buruk. */
export const STAR_COLORS = ["var(--star-1)", "var(--star-2)", "var(--star-3)", "var(--star-4)", "var(--star-5)"];

export interface Group {
  key: string;
  label: string;
  kind: GroupBy;
  channel?: string;
  product?: MapProduct;
  findings: MapFinding[];
  counts: Record<Bucket, number>;
  score: number;
  worst: Bucket | null;
}

export function groupKey(finding: MapFinding, by: GroupBy) {
  return by === "product" ? finding.product_id
    : by === "aspect" ? finding.aspect
    : by === "type" ? finding.finding_type
    : finding.channel;
}

export function buildGroups(
  findings: MapFinding[],
  products: MapProduct[],
  by: GroupBy,
  label: (kind: GroupBy, key: string) => string,
  includeHealthy: boolean,
): Group[] {
  const map = new Map<string, Group>();
  const productById = new Map(products.map((p) => [p.id, p]));
  const ensure = (key: string) => {
    let group = map.get(key);
    if (!group) {
      const product = by === "product" ? productById.get(key) : undefined;
      group = {
        key,
        kind: by,
        label: product?.title ?? label(by, key),
        channel: product?.channel ?? (by === "channel" ? key : undefined),
        product,
        findings: [],
        counts: { recurrence: 0, needs_fact: 0, to_do: 0, monitoring: 0 },
        score: 0,
        worst: null,
      };
      map.set(key, group);
    }
    return group;
  };
  for (const finding of findings) {
    const group = ensure(groupKey(finding, by));
    group.findings.push(finding);
    const bucket = finding.bucket as Bucket;
    if (bucket in group.counts) group.counts[bucket] += 1;
  }
  if (includeHealthy && by === "product") for (const product of products) ensure(product.id);
  for (const group of map.values()) {
    group.score = BUCKETS.reduce((sum, b) => sum + group.counts[b] * URGENCY[b].weight, 0)
      + group.findings.reduce((sum, f) => sum + Math.min(f.support, 20) / 20, 0);
    group.worst = BUCKETS.find((b) => group.counts[b] > 0) ?? null;
    group.findings.sort((a, b) => BUCKETS.indexOf(a.bucket as Bucket) - BUCKETS.indexOf(b.bucket as Bucket) || b.support - a.support);
  }
  return [...map.values()].sort((a, b) => b.score - a.score || b.findings.length - a.findings.length || a.label.localeCompare(b.label));
}

export interface Placed {
  group: Group;
  x: number;
  y: number;
  r: number; // radius hub
  ring: number; // radius cincin terluar titik isu
  leaves: { finding: MapFinding; x: number; y: number; r: number }[];
}

export function leafRadius(support: number) {
  return 3.2 + Math.min(5, Math.sqrt(Math.max(0, support)) * 1.1);
}

/** Tata letak deterministik: titik isu mengelilingi hubnya dalam cincin, hub didorong saling
 * menjauh (tabrakan per cincin) dan ditarik ringan ke pusat serta ke hub yang berbagi aspek. */
export function layout(groups: Group[], links: [number, number][], iterations = 260): Placed[] {
  const placed: Placed[] = groups.map((group, index) => {
    const n = group.findings.length;
    // Hub produk sebesar volume ulasannya; hub kelompok lain sebesar jumlah isunya.
    const volume = group.product ? group.product.reviews : n * 4;
    const r = n === 0 ? 5 + Math.min(4, Math.sqrt(volume) * 0.5) : 7 + Math.min(13, Math.sqrt(volume) * 1.25);
    const leaves: Placed["leaves"] = [];
    let ringRadius = r + 16;
    let placedCount = 0;
    let ring = r;
    while (placedCount < n) {
      const circumference = 2 * Math.PI * ringRadius;
      const capacity = Math.max(6, Math.floor(circumference / 15));
      const take = Math.min(capacity, n - placedCount);
      const offset = (ringRadius / 17) % (Math.PI * 2);
      for (let k = 0; k < take; k++) {
        const angle = offset + (k / take) * Math.PI * 2;
        const finding = group.findings[placedCount + k];
        leaves.push({ finding, x: Math.cos(angle) * ringRadius, y: Math.sin(angle) * ringRadius, r: leafRadius(finding.support) });
      }
      placedCount += take;
      ring = ringRadius + 8;
      ringRadius += 16;
    }
    // Spiral emas sebagai posisi awal: deterministik dan sudah cukup tersebar.
    const angle = index * 2.39996;
    const distance = 40 * Math.sqrt(index + 0.5);
    return { group, x: Math.cos(angle) * distance, y: Math.sin(angle) * distance, r, ring: Math.max(ring, r + 6), leaves };
  });
  const count = placed.length;
  for (let step = 0; step < iterations; step++) {
    const alpha = 1 - step / iterations;
    for (let i = 0; i < count; i++) {
      const a = placed[i];
      // gravitasi ke pusat
      a.x -= a.x * 0.008 * alpha;
      a.y -= a.y * 0.008 * alpha;
      for (let j = i + 1; j < count; j++) {
        const b = placed[j];
        let dx = b.x - a.x;
        let dy = b.y - a.y;
        let dist = Math.hypot(dx, dy);
        if (dist < 0.01) {
          dx = 0.01 * (j - i);
          dy = 0.01;
          dist = Math.hypot(dx, dy);
        }
        const min = a.ring + b.ring + 22;
        if (dist < min) {
          const push = ((min - dist) / dist) * 0.5;
          a.x -= dx * push;
          a.y -= dy * push;
          b.x += dx * push;
          b.y += dy * push;
        }
      }
    }
    for (const [i, j] of links) {
      const a = placed[i];
      const b = placed[j];
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.hypot(dx, dy) || 1;
      const target = a.ring + b.ring + 44;
      if (dist > target) {
        const pull = ((dist - target) / dist) * 0.012 * alpha;
        a.x += dx * pull;
        a.y += dy * pull;
        b.x -= dx * pull;
        b.y -= dy * pull;
      }
    }
  }
  return placed;
}

/** Hub yang berbagi sesuatu: produk yang punya aspek sama, atau kelompok yang punya produk sama. */
export function sharedLinks(groups: Group[], by: GroupBy): [number, number][] {
  const owner = new Map<string, number[]>();
  groups.forEach((group, index) => {
    const keys = new Set(group.findings.map((f) => (by === "product" ? f.aspect : f.product_id)));
    for (const key of keys) {
      if (by === "product" && key === "other") continue;
      owner.set(key, [...(owner.get(key) ?? []), index]);
    }
  });
  const seen = new Set<string>();
  const out: [number, number][] = [];
  for (const members of owner.values()) {
    for (let a = 0; a < members.length; a++)
      for (let b = a + 1; b < members.length; b++) {
        const id = members[a] + ":" + members[b];
        if (!seen.has(id)) {
          seen.add(id);
          out.push([members[a], members[b]]);
        }
      }
  }
  return out.slice(0, 400);
}

export function bounds(placed: Placed[]) {
  if (!placed.length) return { x: -100, y: -100, w: 200, h: 200 };
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const p of placed) {
    minX = Math.min(minX, p.x - p.ring);
    minY = Math.min(minY, p.y - p.ring - 14);
    maxX = Math.max(maxX, p.x + p.ring);
    maxY = Math.max(maxY, p.y + p.ring);
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

export function sumStars(byChannel: Record<string, number[]>, channel: string) {
  const out = [0, 0, 0, 0, 0];
  for (const [key, counts] of Object.entries(byChannel)) {
    if (channel && key !== channel) continue;
    counts.forEach((value, index) => (out[index] += value));
  }
  return out;
}

export function averageStars(counts: number[]) {
  const total = counts.reduce((s, v) => s + v, 0);
  return total ? counts.reduce((s, v, i) => s + v * (i + 1), 0) / total : null;
}

/** Label ujung garis yang tidak bertumpuk: urut menurut y lalu didorong minimal `gap` piksel. */
export function spreadLabels<T extends { y: number }>(items: T[], gap: number, min: number, max: number) {
  const sorted = [...items].sort((a, b) => a.y - b.y).map((item) => ({ ...item, ly: item.y }));
  for (let i = 1; i < sorted.length; i++)
    if (sorted[i].ly - sorted[i - 1].ly < gap) sorted[i].ly = sorted[i - 1].ly + gap;
  const overflow = sorted.length ? sorted[sorted.length - 1].ly - max : 0;
  if (overflow > 0) for (const item of sorted) item.ly -= overflow;
  for (let i = 0; i < sorted.length; i++) sorted[i].ly = Math.max(min + i * gap, sorted[i].ly);
  return sorted;
}

/** Pilih label hub yang tidak saling tumpuk, mulai dari kelompok paling mendesak. */
export function pickLabels(placed: Placed[], wanted: Set<string>, charWidth = 5.4, height = 12) {
  const boxes: { x0: number; x1: number; y0: number; y1: number }[] = [];
  const out = new Set<string>();
  const order = [...placed].sort((a, b) => b.group.score - a.group.score);
  for (const p of order) {
    if (!wanted.has(p.group.key)) continue;
    const width = Math.min(22, p.group.label.length) * charWidth;
    const y = p.y - p.ring + 2;
    const box = { x0: p.x - width / 2, x1: p.x + width / 2, y0: y - height, y1: y + 2 };
    if (boxes.some((b) => b.x0 < box.x1 && box.x0 < b.x1 && b.y0 < box.y1 && box.y0 < b.y1)) continue;
    boxes.push(box);
    out.add(p.group.key);
  }
  return out;
}
