/* Kontrak bersama antara pembungkus IssueMap dan kanvasnya (2D SVG atau 3D WebGL). Kanvas hanya
 * menggambar dan melaporkan interaksi; filter, pilihan, tooltip, dan panel ada di pembungkus. */
import { issueLink } from "@/lib/workspace-model.js";
import { channelColor, urgencyColor, type Group, type GroupBy, type MapFinding } from "@/lib/insight-model";

export type ColorBy = "urgency" | "channel";

export interface MapHover {
  finding?: MapFinding;
  group?: Group;
  /** Koordinat relatif terhadap panggung peta. */
  x: number;
  y: number;
}

export interface MapCanvasHandle {
  zoomIn(): void;
  zoomOut(): void;
  /** Kembalikan kamera/tampilan ke seluruh peta. */
  fit(): void;
}

export interface MapCanvasProps {
  groups: Group[];
  links: [number, number][];
  groupBy: GroupBy;
  colorBy: ColorBy;
  labels: boolean;
  selected: string | null;
  /** Bertambah setiap kali pilihan datang dari daftar samping (minta peta menyorot). */
  focusSeq: number;
  summary: string;
  reducedMotion: boolean;
  onSelect(key: string | null): void;
  onHover(hover: MapHover | null): void;
}

/** Warna titik isu: urgensi atau kanal. Nilai berupa `var(--…)` agar ikut tema. */
export function leafColor(finding: MapFinding, colorBy: ColorBy) {
  return colorBy === "urgency" ? urgencyColor(finding.bucket) : channelColor(finding.channel);
}

/** Warna hub: urgensi terburuk (atau kanal bila diwarnai per kanal); hub sehat hijau pucat. */
export function hubColor(group: Group, colorBy: ColorBy) {
  if (group.kind === "channel") return channelColor(group.key);
  if (colorBy === "channel" && group.channel) return channelColor(group.channel);
  if (group.worst) return urgencyColor(group.worst);
  return group.kind === "product" ? "var(--map-healthy)" : "var(--map-hub)";
}

/** Buka halaman isu, sama seperti tautan di daftar samping. */
export function openIssue(finding: MapFinding) {
  window.location.hash = issueLink(finding).slice(1);
}

/** Hub yang diberi label di kanvas 3D: paling mendesak dulu. */
export const TOP_LABELS_3D = 8;
