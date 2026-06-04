import { useEffect, useMemo, useState } from "react";
import { fetchSubjectiveFeatures } from "@/api/client";
import type { SubjectiveFeature } from "@/lib/types";

interface Props {
  ratings: Record<string, number>;
  onChange: (next: Record<string, number>) => void;
}

interface Group {
  module: string;
  category: string;
  label: string;
  features: SubjectiveFeature[];
}

function groupLabel(module: string, category: string) {
  if (module === "MISC") return category.toUpperCase();
  if (module === "ANGU") return "ANGULARITY (manual)";
  if (module === "DIMO") return "DIMORPHISM (manual)";
  return module;
}

export function SubjectiveRatingsForm({ ratings, onChange }: Props) {
  const [features, setFeatures] = useState<SubjectiveFeature[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openGroups, setOpenGroups] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchSubjectiveFeatures()
      .then(setFeatures)
      .catch((e: Error) => setError(e.message));
  }, []);

  const groups: Group[] = useMemo(() => {
    if (!features) return [];
    const byKey = new Map<string, Group>();
    for (const f of features) {
      const key = `${f.module}:${f.category}`;
      let g = byKey.get(key);
      if (!g) {
        g = { module: f.module, category: f.category,
              label: groupLabel(f.module, f.category), features: [] };
        byKey.set(key, g);
      }
      g.features.push(f);
    }
    return Array.from(byKey.values());
  }, [features]);

  function toggleGroup(key: string) {
    setOpenGroups((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  function setRating(name: string, tier: number | null) {
    const next = { ...ratings };
    if (tier === null) delete next[name];
    else next[name] = tier;
    onChange(next);
  }

  function skipAll() {
    onChange({});
  }

  function rateAllTo(tier: number) {
    if (!features) return;
    const next: Record<string, number> = {};
    for (const f of features) {
      // Use tier capped at the feature's max tier
      const maxTier = Math.max(...f.tiers.map((t) => t[0]));
      next[f.name] = Math.min(tier, maxTier);
    }
    onChange(next);
  }

  if (error) return (
    <div className="card p-4 text-sm text-bad">Could not load subjective features: {error}</div>
  );
  if (!features) return (
    <div className="card p-4 text-sm text-ink-300">Loading subjective features…</div>
  );

  return (
    <div className="card p-4 flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <div className="text-sm font-medium">Subjective ratings (optional)</div>
        <div className="text-xs text-ink-300">{Object.keys(ratings).length} of {features.length} rated</div>
        <div className="ml-auto flex items-center gap-1.5 flex-wrap">
          <button type="button" className="btn-ghost text-xs px-2 py-1" onClick={skipAll}>Skip all</button>
          <span className="text-[11px] text-ink-300">Rate all:</span>
          {[1, 2, 3, 4, 5, 6, 7].map((t) => (
            <button
              key={t}
              type="button"
              className="btn-ghost text-xs px-2 py-1 font-semibold"
              onClick={() => rateAllTo(t)}
            >
              T{t}
            </button>
          ))}
        </div>
      </div>
      <div className="text-xs text-ink-300">
        Rate each subjective feature yourself — these can't be auto-detected from a single photo. Skipped features score 0 points.
      </div>

      <div className="space-y-2">
        {groups.map((g) => {
          const key = `${g.module}:${g.category}`;
          const open = openGroups.has(key);
          const rated = g.features.filter((f) => ratings[f.name] !== undefined).length;
          return (
            <div key={key} className="rounded-lg border border-ink-700/60 bg-ink-900/40">
              <button
                type="button"
                onClick={() => toggleGroup(key)}
                className="w-full flex items-center gap-3 px-3 py-2 text-left"
              >
                <span className="text-xs uppercase tracking-widest text-ink-300">{g.label}</span>
                <span className="text-[10px] text-ink-300">{rated}/{g.features.length}</span>
                <span className="ml-auto text-ink-300">{open ? "−" : "+"}</span>
              </button>
              {open && (
                <div className="border-t border-ink-700/60 p-3 space-y-3">
                  {g.features.map((f) => (
                    <div key={f.name} className="grid grid-cols-1 sm:grid-cols-[200px_1fr] gap-2 items-start">
                      <div>
                        <div className="text-sm font-medium">{f.label}</div>
                        <div className="text-[11px] text-ink-300">{f.description}</div>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {f.tiers.map((t) => {
                          const [tier, points, label] = t;
                          const active = ratings[f.name] === tier;
                          const tone = points > 0 ? "text-good" : points < 0 ? "text-bad" : "text-ink-200";
                          return (
                            <button
                              key={tier}
                              type="button"
                              onClick={() => setRating(f.name, active ? null : tier)}
                              className={[
                                "text-[11px] rounded-md px-2 py-1 border transition",
                                active
                                  ? "border-accent-500 bg-accent-500/20 text-white"
                                  : "border-ink-700 bg-ink-900/40 hover:border-ink-500",
                              ].join(" ")}
                              title={label}
                            >
                              <span className="font-medium">T{tier}</span>
                              <span className="text-ink-300"> · {label.length > 20 ? label.slice(0, 20) + "…" : label}</span>
                              <span className={`ml-1 ${tone}`}>{points > 0 ? "+" : ""}{points}</span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
