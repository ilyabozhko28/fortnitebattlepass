import { useCallback, useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ModuleGauges } from "@/components/ModuleGauges";
import { InteractiveOverlay } from "@/components/InteractiveOverlay";
import { SideAnnotator } from "@/components/SideAnnotator";
import { SubjectiveRatingsForm } from "@/components/SubjectiveRatingsForm";
import { ResultsBreakdown } from "@/components/ResultsBreakdown";
import { score as scoreApi } from "@/api/client";
import type { AnalysisResponse, MetricResult, Module } from "@/lib/types";

interface NavState {
  response: AnalysisResponse;
  frontalUrl: string;
  sideUrl: string | null;
}

type Tab = "frontal" | "side" | "subjective";

const MODULE_LABEL: Record<Module, string> = {
  HARM: "Harmony", DIMO: "Dimorphism", ANGU: "Angularity", MISC: "Misc",
};

export default function ResultsPage() {
  const nav = useNavigate();
  const location = useLocation();
  const state = (location.state ?? null) as NavState | null;

  const [response, setResponse] = useState<AnalysisResponse | null>(state?.response ?? null);
  const [originalLandmarks, setOriginalLandmarks] = useState<[number, number][]>(
    state?.response?.landmarks ?? [],
  );
  const [landmarks, setLandmarks] = useState<[number, number][]>(
    state?.response?.landmarks ?? [],
  );
  const [sideAnnotations, setSideAnnotations] = useState<Record<string, [number, number]>>(
    Object.fromEntries(
      Object.entries(state?.response?.side_annotations ?? {})
        .map(([k, v]) => [k, [v[0], v[1]] as [number, number]]),
    ),
  );
  const [miscRatings, setMiscRatings] = useState<Record<string, number>>(() => {
    const out: Record<string, number> = {};
    for (const m of state?.response?.metrics ?? []) {
      if (m.source === "manual" && m.tier !== null) out[m.name] = m.tier;
    }
    return out;
  });
  const [edited, setEdited] = useState(false);
  const [recomputing, setRecomputing] = useState(false);
  const [recomputeError, setRecomputeError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("frontal");

  useEffect(() => {
    if (!state) nav("/", { replace: true });
  }, [state, nav]);

  const markEdited = useCallback(() => {
    setEdited(true);
    setRecomputeError(null);
  }, []);

  const onLandmarksChange = useCallback((next: [number, number][]) => {
    setLandmarks(next);
    markEdited();
  }, [markEdited]);

  const onSideAnnotationsChange = useCallback((next: Record<string, [number, number]>) => {
    setSideAnnotations(next);
    markEdited();
  }, [markEdited]);

  const onMiscChange = useCallback((next: Record<string, number>) => {
    setMiscRatings(next);
    markEdited();
  }, [markEdited]);

  const resetPoints = useCallback(() => {
    setLandmarks(originalLandmarks);
    setEdited(false);
    setRecomputeError(null);
  }, [originalLandmarks]);

  const handleRecompute = useCallback(async () => {
    if (!response) return;
    setRecomputing(true);
    setRecomputeError(null);
    try {
      const next = await scoreApi({
        landmarks,
        sex: response.sex,
        imageSize: response.image_size,
        maskB64: response.mask_b64,
        sideAnnotations: Object.keys(sideAnnotations).length > 0 ? sideAnnotations : null,
        sideImageSize: response.side_image_size,
        miscRatings: Object.keys(miscRatings).length > 0 ? miscRatings : null,
      });
      setResponse(next);
      setOriginalLandmarks(next.landmarks);
      setLandmarks(next.landmarks);
      setEdited(false);
    } catch (e) {
      setRecomputeError((e as Error).message);
    } finally {
      setRecomputing(false);
    }
  }, [landmarks, response, sideAnnotations, miscRatings]);

  if (!state || !response) return null;

  const groupedByModule = response.metrics.reduce<Record<Module, MetricResult[]>>(
    (acc, m) => {
      (acc[m.module] = acc[m.module] || []).push(m);
      return acc;
    },
    { HARM: [], DIMO: [], ANGU: [], MISC: [] },
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-ink-300 uppercase tracking-widest">Results</div>
          <h1 className="text-2xl font-semibold tracking-tight mt-1">v2 Score Breakdown</h1>
        </div>
        <Link to="/" className="btn-ghost">Analyze another</Link>
      </div>

      <ModuleGauges modules={response.modules} final={response.final} />

      {(response.warnings.length > 0 || edited) && (
        <div className="card p-4 border-warn/40 bg-warn/10 space-y-2">
          {edited && (
            <div className="flex items-center gap-3">
              <div className="text-sm text-warn">
                Inputs edited — re-score to update the breakdown.
              </div>
              <div className="ml-auto flex gap-2">
                <button type="button" className="btn-ghost text-xs px-3 py-1.5"
                        onClick={resetPoints} disabled={recomputing}>
                  Revert points
                </button>
                <button type="button" className="btn-primary text-xs px-3 py-1.5"
                        onClick={handleRecompute} disabled={recomputing}>
                  {recomputing ? "Re-scoring…" : "Re-score"}
                </button>
              </div>
            </div>
          )}
          {response.warnings.length > 0 && (
            <ul className="text-xs text-ink-200 list-disc pl-5 space-y-1">
              {response.warnings.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          )}
          {recomputeError && <div className="text-xs text-bad">{recomputeError}</div>}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-ink-700/60 pb-0">
        {([
          { id: "frontal" as const, label: "Frontal overlay" },
          { id: "side" as const, label: state.sideUrl ? "Side overlay" : "Side (no photo)" },
          { id: "subjective" as const, label: "Subjective" },
        ]).map((t) => (
          <button key={t.id} type="button" onClick={() => setTab(t.id)}
                  disabled={t.id === "side" && !state.sideUrl}
                  className={[
                    "px-3 py-2 text-sm border-b-2 -mb-px",
                    tab === t.id
                      ? "border-accent-500 text-white"
                      : "border-transparent text-ink-300 hover:text-ink-100",
                    t.id === "side" && !state.sideUrl ? "opacity-50 cursor-not-allowed" : "",
                  ].join(" ")}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === "frontal" && (
        <InteractiveOverlay
          imageUrl={state.frontalUrl}
          landmarks={landmarks}
          imageSize={response.image_size}
          onChange={onLandmarksChange}
          onReset={resetPoints}
        />
      )}
      {tab === "side" && state.sideUrl && response.side_image_size && (
        <SideAnnotator
          imageUrl={state.sideUrl}
          imageSize={response.side_image_size}
          annotations={sideAnnotations}
          onChange={onSideAnnotationsChange}
        />
      )}
      {tab === "subjective" && (
        <SubjectiveRatingsForm ratings={miscRatings} onChange={onMiscChange} />
      )}

      {/* Per-module breakdown */}
      <div className="space-y-6">
        {(Object.keys(groupedByModule) as Module[]).map((mod) => {
          const items = groupedByModule[mod];
          if (!items || items.length === 0) return null;
          return (
            <section key={mod}>
              <h3 className="text-xs uppercase tracking-widest text-ink-300 mb-2">
                {MODULE_LABEL[mod]} · {response.modules[mod].pct.toFixed(1)}%
                <span className="ml-2 text-ink-500">
                  {response.modules[mod].measured_count}/{response.modules[mod].total_count} measured
                </span>
              </h3>
              <ResultsBreakdown metrics={items} />
            </section>
          );
        })}
      </div>
    </div>
  );
}
