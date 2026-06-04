interface Props {
  score: number;
  totalPoints: number;
  maxPoints: number;
}

function pickColor(p: number) {
  if (p >= 0.7) return "#21c187";
  if (p >= 0.45) return "#f7b500";
  return "#ef4d4d";
}

export function ScoreGauge({ score, totalPoints, maxPoints }: Props) {
  const clamped = Math.max(0, Math.min(1, score));
  const radius = 90;
  const stroke = 14;
  const c = 2 * Math.PI * radius;
  const color = pickColor(clamped);
  const dash = c * clamped;
  const display = (clamped * 100).toFixed(1);

  return (
    <div className="card p-6 flex items-center gap-6">
      <svg width={220} height={220} viewBox="0 0 220 220" className="shrink-0">
        <circle
          cx={110}
          cy={110}
          r={radius}
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={stroke}
          fill="none"
        />
        <circle
          cx={110}
          cy={110}
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c}`}
          transform="rotate(-90 110 110)"
          style={{ transition: "stroke-dasharray 600ms ease" }}
        />
        <text
          x="110"
          y="108"
          textAnchor="middle"
          fontSize="36"
          fontWeight={700}
          fill="#f5f5f7"
        >
          {display}%
        </text>
        <text x="110" y="138" textAnchor="middle" fontSize="12" fill="#9b9bad">
          harmony
        </text>
      </svg>
      <div className="flex-1">
        <div className="text-xs uppercase tracking-widest text-ink-300">Frontal Harmony</div>
        <div className="text-3xl font-semibold mt-1">{display}%</div>
        <div className="text-sm text-ink-300 mt-2">
          {totalPoints.toFixed(2)} / {maxPoints} points
        </div>
        <div className="mt-4 text-xs text-ink-300 max-w-md leading-relaxed">
          Sum of awarded points across 20 metrics, divided by 275 per the
          specification. Negative tiers reduce the total.
        </div>
      </div>
    </div>
  );
}
