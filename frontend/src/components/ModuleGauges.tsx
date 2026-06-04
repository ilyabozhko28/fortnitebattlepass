import type { FinalScore, Module, ModuleScore } from "@/lib/types";

interface Props {
  modules: Record<Module, ModuleScore>;
  final: FinalScore;
}

const MODULE_INFO: Record<Module, { label: string; color: string; description: string }> = {
  HARM: { label: "Harmony",     color: "#7c5cff", description: "Facial proportions (26 features, 32% weight)" },
  MISC: { label: "Misc",        color: "#ec4899", description: "Skin/eyes/colour subjective (50 features, 26% weight)" },
  ANGU: { label: "Angularity",  color: "#06b6d4", description: "Edge sharpness, projection (9 features, 22% weight)" },
  DIMO: { label: "Dimorphism",  color: "#21c187", description: "Masculine/feminine traits (11 features, 20% weight)" },
};

function pickFinalColor(pct: number) {
  if (pct >= 70) return "#21c187";
  if (pct >= 50) return "#f7b500";
  return "#ef4d4d";
}

function clamp01(x: number) {
  return Math.max(0, Math.min(1, x));
}

function MiniGauge({ label, color, pct, sub, foot }: {
  label: string; color: string; pct: number; sub: string; foot?: string;
}) {
  const fill = clamp01(pct / 100);
  const radius = 42;
  const stroke = 8;
  const circ = 2 * Math.PI * radius;
  return (
    <div className="rounded-xl border border-ink-700/60 bg-ink-900/40 p-3 flex flex-col items-center">
      <svg width={120} height={120} viewBox="0 0 120 120">
        <circle cx={60} cy={60} r={radius} stroke="rgba(255,255,255,0.08)"
                strokeWidth={stroke} fill="none" />
        <circle cx={60} cy={60} r={radius} stroke={color}
                strokeWidth={stroke} fill="none" strokeLinecap="round"
                strokeDasharray={`${circ * fill} ${circ}`}
                transform="rotate(-90 60 60)"
                style={{ transition: "stroke-dasharray 600ms ease" }} />
        <text x="60" y="60" textAnchor="middle" fontSize="20" fontWeight={600} fill="#f5f5f7">
          {pct.toFixed(1)}%
        </text>
        <text x="60" y="80" textAnchor="middle" fontSize="9" fill="#9b9bad">
          {label}
        </text>
      </svg>
      <div className="text-[11px] text-ink-300 text-center mt-1 leading-tight">{sub}</div>
      {foot && <div className="text-[10px] text-ink-300 text-center mt-0.5">{foot}</div>}
    </div>
  );
}

export function ModuleGauges({ modules, final }: Props) {
  const finalPct = Math.max(0, Math.min(100, final.final * 10));
  const color = pickFinalColor(finalPct);
  const radius = 90;
  const stroke = 14;
  const circ = 2 * Math.PI * radius;
  const finalFill = clamp01(finalPct / 100);

  return (
    <div className="space-y-4">
      {/* Final big gauge */}
      <div className="card p-6 flex items-center gap-6">
        <svg width={220} height={220} viewBox="0 0 220 220" className="shrink-0">
          <circle cx={110} cy={110} r={radius} stroke="rgba(255,255,255,0.08)"
                  strokeWidth={stroke} fill="none" />
          <circle cx={110} cy={110} r={radius} stroke={color}
                  strokeWidth={stroke} fill="none" strokeLinecap="round"
                  strokeDasharray={`${circ * finalFill} ${circ}`}
                  transform="rotate(-90 110 110)"
                  style={{ transition: "stroke-dasharray 600ms ease" }} />
          <text x="110" y="103" textAnchor="middle" fontSize="36" fontWeight={700} fill="#f5f5f7">
            {final.final.toFixed(2)}
          </text>
          <text x="110" y="125" textAnchor="middle" fontSize="11" fill="#9b9bad">
            / 10
          </text>
          <text x="110" y="155" textAnchor="middle" fontSize="10" fill="#9b9bad">
            FINAL
          </text>
        </svg>
        <div className="flex-1">
          <div className="text-xs uppercase tracking-widest text-ink-300">Final Frontal Harmony</div>
          <div className="text-3xl font-semibold mt-1">{final.final.toFixed(2)} / 10</div>
          <div className="text-sm text-ink-300 mt-2">
            Weighted sum: <b className="text-ink-100">{final.weighted.toFixed(2)}</b> −
            imbalance penalty: <b className="text-bad">{final.deduction.toFixed(2)}</b>
          </div>
          <div className="mt-3 text-xs text-ink-300 leading-relaxed max-w-md">
            Each of HARM (32%), MISC (26%), ANGU (22%), DIMO (20%) is normalized
            to 0-10. The deduction = 0.1 × (max-min) penalizes imbalance across modules.
          </div>
        </div>
      </div>

      {/* 4 sub-gauges */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {(Object.keys(MODULE_INFO) as Module[]).map((m) => {
          const info = MODULE_INFO[m];
          const score = modules[m];
          if (!score) return null;
          const sub = `${score.measured_count}/${score.total_count} measured`;
          const foot = `${(score.weighted_tens).toFixed(2)} pts towards final`;
          return (
            <MiniGauge key={m} label={info.label} color={info.color}
                       pct={score.pct} sub={sub} foot={foot} />
          );
        })}
      </div>
    </div>
  );
}
