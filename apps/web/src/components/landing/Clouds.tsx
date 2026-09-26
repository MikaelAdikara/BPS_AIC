import { useId } from "react";

/** Bank awan dekoratif: elips lembut yang tepinya dibuat bergelombang oleh noise fraktal lalu
 *  diblur, sehingga tidak terlihat seperti lingkaran radial-gradient. Selalu `aria-hidden`. */
const PUFFS: Array<[number, number, number, number, "sky" | "deep"]> = [
  [90, 150, 170, 70, "sky"],
  [260, 120, 200, 86, "sky"],
  [470, 150, 230, 78, "deep"],
  [700, 118, 210, 90, "sky"],
  [910, 150, 240, 80, "sky"],
  [1120, 128, 190, 84, "deep"],
  [1320, 152, 180, 70, "sky"],
  [360, 190, 260, 60, "sky"],
  [820, 196, 280, 58, "deep"],
  [1220, 196, 230, 56, "sky"],
];

export function Clouds({ className = "" }: { className?: string }) {
  const id = useId().replace(/:/g, "");
  return (
    <svg
      className={"clouds " + className}
      viewBox="0 0 1440 260"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden
      focusable="false"
    >
      <defs>
        <filter id={"f" + id} x="-20%" y="-60%" width="140%" height="220%">
          <feTurbulence type="fractalNoise" baseFrequency="0.011 0.028" numOctaves="3" seed="7" />
          <feDisplacementMap in="SourceGraphic" scale="46" />
          <feGaussianBlur stdDeviation="14" />
        </filter>
      </defs>
      <g filter={`url(#f${id})`}>
        {PUFFS.map(([cx, cy, rx, ry, tone], i) => (
          <ellipse
            key={i}
            cx={cx}
            cy={cy}
            rx={rx}
            ry={ry}
            className={tone === "sky" ? "clouds__sky" : "clouds__deep"}
          />
        ))}
      </g>
    </svg>
  );
}
