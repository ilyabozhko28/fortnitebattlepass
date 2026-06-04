import type { MetricResult } from "@/lib/types";
import { MetricCard } from "./MetricCard";

interface Props {
  metrics: MetricResult[];
}

export function ResultsBreakdown({ metrics }: Props) {
  if (metrics.length === 0) {
    return (
      <div className="card p-4 text-xs text-ink-300">
        No metrics in this module — provide more inputs (side photo or ratings).
      </div>
    );
  }
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {metrics.map((m) => (
        <MetricCard key={m.name} metric={m} />
      ))}
    </div>
  );
}
