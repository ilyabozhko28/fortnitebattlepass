import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SexSelector } from "@/components/SexSelector";
import { ImageUploader } from "@/components/ImageUploader";
import { WebcamCapture } from "@/components/WebcamCapture";
import { SideAnnotator } from "@/components/SideAnnotator";
import { SubjectiveRatingsForm } from "@/components/SubjectiveRatingsForm";
import { analyze } from "@/api/client";
import type { Sex } from "@/lib/types";

type FrontalTab = "upload" | "webcam";

interface ImageInfo {
  file: File;
  url: string;
  size: { width: number; height: number };
}

async function loadImageSize(url: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.naturalWidth, height: img.naturalHeight });
    img.onerror = () => resolve({ width: 1, height: 1 });
    img.src = url;
  });
}

export default function HomePage() {
  const nav = useNavigate();
  const [sex, setSex] = useState<Sex | null>(null);
  const [tab, setTab] = useState<FrontalTab>("upload");
  const [frontal, setFrontal] = useState<ImageInfo | null>(null);
  const [side, setSide] = useState<ImageInfo | null>(null);
  const [sideAnnotations, setSideAnnotations] = useState<Record<string, [number, number]>>({});
  const [showSideAnnotator, setShowSideAnnotator] = useState(false);
  const [showSubjective, setShowSubjective] = useState(false);
  const [misc, setMisc] = useState<Record<string, number>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState<string>("");

  const canSubmit = !!sex && !!frontal && !busy;

  async function pickFrontal(f: File, url: string) {
    const size = await loadImageSize(url);
    setFrontal({ file: f, url, size });
    setError(null);
  }

  async function pickSide(f: File, url: string) {
    const size = await loadImageSize(url);
    setSide({ file: f, url, size });
    setShowSideAnnotator(true);
  }

  function clearSide() {
    setSide(null);
    setSideAnnotations({});
    setShowSideAnnotator(false);
  }

  async function submit() {
    if (!sex || !frontal) return;
    setBusy(true);
    setError(null);
    setStage("uploading + analyzing…");
    try {
      const res = await analyze(frontal.file, sex, {
        sideImage: side?.file ?? null,
        sideAnnotations: Object.keys(sideAnnotations).length > 0 ? sideAnnotations : null,
        miscRatings: Object.keys(misc).length > 0 ? misc : null,
      });
      nav("/results", { state: {
        response: res,
        frontalUrl: frontal.url,
        sideUrl: side?.url ?? null,
      } });
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
      setStage("");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Measure your face — v2</h1>
        <p className="text-sm text-ink-300 mt-2 max-w-3xl">
          4-module scoring across 96 features: <b>HARM</b>ony (frontal landmarks),
          <b> DIMO</b>rphism (frontal + side + subjective), <b>ANGU</b>larity (subjective),
          <b> MISC</b> (subjective). Final score = weighted sum − imbalance penalty.
        </p>
      </div>

      {/* Step 1: Sex + Frontal */}
      <section className="card p-4 space-y-4">
        <div className="flex items-center gap-3">
          <span className="rounded-full w-7 h-7 inline-flex items-center justify-center bg-accent-500/20 text-accent-500 text-sm font-semibold">1</span>
          <div className="text-sm font-medium">Frontal photo (required)</div>
          {frontal && <span className="text-xs text-good ml-auto">✓ uploaded</span>}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-4">
          <div>
            <div className="flex gap-2 mb-2">
              <button type="button" onClick={() => setTab("upload")}
                      className={["btn", tab === "upload" ? "bg-ink-700/70 text-white" : "bg-transparent text-ink-300"].join(" ")}>
                Upload
              </button>
              <button type="button" onClick={() => setTab("webcam")}
                      className={["btn", tab === "webcam" ? "bg-ink-700/70 text-white" : "bg-transparent text-ink-300"].join(" ")}>
                Webcam
              </button>
            </div>
            {tab === "upload"
              ? <ImageUploader onPick={pickFrontal} previewUrl={frontal?.url ?? null} />
              : <WebcamCapture onCapture={pickFrontal} previewUrl={frontal?.url ?? null} />}
          </div>
          <SexSelector value={sex} onChange={setSex} />
        </div>
      </section>

      {/* Step 2: Side profile (optional) */}
      <section className="card p-4 space-y-4">
        <div className="flex items-center gap-3">
          <span className="rounded-full w-7 h-7 inline-flex items-center justify-center bg-ink-700 text-ink-200 text-sm font-semibold">2</span>
          <div className="text-sm font-medium">Side profile (optional — unlocks 8 metrics)</div>
          {side && <span className="text-xs text-good ml-auto">✓ {Object.keys(sideAnnotations).length}/16 points</span>}
        </div>
        {!side && <ImageUploader onPick={pickSide} previewUrl={null} />}
        {side && (
          <>
            <div className="flex items-center gap-2 text-xs">
              <button type="button" className="btn-ghost text-xs px-2 py-1" onClick={() => setShowSideAnnotator((s) => !s)}>
                {showSideAnnotator ? "Hide annotator" : "Annotate landmarks"}
              </button>
              <button type="button" className="btn-ghost text-xs px-2 py-1" onClick={clearSide}>
                Remove side photo
              </button>
              <span className="ml-auto text-ink-300">
                {Object.keys(sideAnnotations).length === 0
                  ? "no landmarks placed yet — side metrics will be skipped"
                  : `${Object.keys(sideAnnotations).length} / 16 placed`}
              </span>
            </div>
            {showSideAnnotator && (
              <SideAnnotator imageUrl={side.url} imageSize={side.size}
                             annotations={sideAnnotations} onChange={setSideAnnotations} />
            )}
          </>
        )}
      </section>

      {/* Step 3: Subjective ratings (optional) */}
      <section className="card p-4 space-y-4">
        <div className="flex items-center gap-3">
          <span className="rounded-full w-7 h-7 inline-flex items-center justify-center bg-ink-700 text-ink-200 text-sm font-semibold">3</span>
          <div className="text-sm font-medium">Subjective ratings (optional — fills MISC/ANGU/manual DIMO)</div>
          {Object.keys(misc).length > 0 && <span className="text-xs text-good ml-auto">✓ {Object.keys(misc).length} rated</span>}
          <button type="button" className="btn-ghost text-xs px-2 py-1"
                  onClick={() => setShowSubjective((s) => !s)}>
            {showSubjective ? "Hide" : "Show form"}
          </button>
        </div>
        {showSubjective && <SubjectiveRatingsForm ratings={misc} onChange={setMisc} />}
      </section>

      {/* Step 4: Analyze button */}
      <section className="card p-4 flex items-center gap-3">
        <div className="text-sm">
          <div className="font-medium">{canSubmit ? "Ready to analyze" : "Complete step 1 to continue"}</div>
          <div className="text-xs text-ink-300 mt-0.5">
            Frontal: {frontal ? "✓" : "—"} · Side: {side ? "✓" : "skipped"} · Ratings: {Object.keys(misc).length}/{Object.keys(misc).length > 0 ? "rated" : "skipped"}
          </div>
        </div>
        <button type="button" className="btn-primary ml-auto" disabled={!canSubmit} onClick={submit}>
          {busy ? "Analyzing…" : "Analyze"}
        </button>
      </section>

      {busy && stage && <div className="text-xs text-ink-300 text-center">{stage}</div>}
      {error && <div className="text-xs text-bad text-center">{error}</div>}
    </div>
  );
}
