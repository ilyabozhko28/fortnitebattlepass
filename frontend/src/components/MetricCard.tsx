import type { MetricResult } from "@/lib/types";
import { TierBadge } from "./TierBadge";

interface Props {
  metric: MetricResult;
}

function formatRaw(raw: number | null) {
  if (raw === null || Number.isNaN(raw)) return "—";
  if (Math.abs(raw) >= 100) return raw.toFixed(1);
  if (Math.abs(raw) >= 10) return raw.toFixed(2);
  return raw.toFixed(3);
}

export function MetricCard({ metric }: Props) {
  const pos = metric.points > 0;
  const neg = metric.points < 0;
  return (
    <div className="card p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="text-sm font-medium leading-snug break-words">
            {metric.label}
          </div>
          <div className="text-xs text-ink-300 mt-0.5 break-words">
            {metric.tier_label ?? "—"}
          </div>
        </div>
        <TierBadge tier={metric.tier} points={metric.points} />
      </div>

      <div className="mt-3 flex items-end justify-between gap-3">
        <div>
          <div className="text-[11px] uppercase tracking-widest text-ink-300">value</div>
          <div className="text-lg font-semibold tabular-nums">{formatRaw(metric.raw)}</div>
        </div>
        <div className="text-right">
          <div className="text-[11px] uppercase tracking-widest text-ink-300">points</div>
          <div
            className={[
              "text-lg font-semibold tabular-nums",
              pos && "text-good",
              neg && "text-bad",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            {metric.points > 0 ? "+" : ""}
            {metric.points.toFixed(2)}
          </div>
        </div>
      </div>

      {metric.note && <div className="mt-3 text-xs text-ink-300">{metric.note}</div>}
    </div>
  );
}
