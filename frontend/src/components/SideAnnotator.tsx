import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { SIDE_LANDMARKS } from "@/lib/sideLandmarks";

type Point = [number, number];

interface Props {
  imageUrl: string;
  imageSize: { width: number; height: number };
  annotations: Record<string, Point>;
  onChange: (next: Record<string, Point>) => void;
}

interface ViewState {
  scale: number;
  tx: number;
  ty: number;
}

const COLORS = [
  "#7c5cff", "#21c187", "#f7b500", "#ef4d4d", "#06b6d4", "#c084fc",
  "#ec4899", "#84cc16", "#f97316", "#22d3ee", "#a78bfa", "#fb7185",
  "#34d399", "#facc15", "#60a5fa", "#f472b6",
];

const MIN_SCALE = 0.5;
const MAX_SCALE = 20;

export function SideAnnotator({ imageUrl, imageSize, annotations, onChange }: Props) {
  const cardRef = useRef<HTMLDivElement | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [view, setView] = useState<ViewState>({ scale: 1, tx: 0, ty: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [containerSize, setContainerSize] = useState({ width: 1, height: 1 });
  const [draggingName, setDraggingName] = useState<string | null>(null);
  const panState = useRef<{ startX: number; startY: number; tx: number; ty: number } | null>(
    null,
  );
  const [hoverName, setHoverName] = useState<string | null>(null);

  const nextToPlace = useMemo(
    () => SIDE_LANDMARKS.find((s) => !annotations[s.name]) ?? null,
    [annotations],
  );

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      const rect = el.getBoundingClientRect();
      setContainerSize({ width: rect.width, height: rect.height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    function onFsChange() {
      setIsFullscreen(document.fullscreenElement === cardRef.current);
    }
    document.addEventListener("fullscreenchange", onFsChange);
    return () => document.removeEventListener("fullscreenchange", onFsChange);
  }, []);

  async function toggleFullscreen() {
    if (!cardRef.current) return;
    if (document.fullscreenElement) {
      await document.exitFullscreen().catch(() => {});
    } else {
      await cardRef.current.requestFullscreen().catch(() => {});
    }
  }

  const fitScale = useMemo(() => {
    if (containerSize.width <= 0 || containerSize.height <= 0) return 1;
    return Math.min(
      containerSize.width / imageSize.width,
      containerSize.height / imageSize.height,
    );
  }, [containerSize, imageSize]);

  useEffect(() => {
    setView({ scale: 1, tx: 0, ty: 0 });
  }, [imageUrl]);

  function screenToImage(clientX: number, clientY: number): Point | null {
    const el = wrapRef.current;
    if (!el) return null;
    const rect = el.getBoundingClientRect();
    const dispW = imageSize.width * fitScale * view.scale;
    const dispH = imageSize.height * fitScale * view.scale;
    const offX = (rect.width - dispW) / 2 + view.tx;
    const offY = (rect.height - dispH) / 2 + view.ty;
    const xLocal = clientX - rect.left - offX;
    const yLocal = clientY - rect.top - offY;
    return [xLocal / (fitScale * view.scale), yLocal / (fitScale * view.scale)];
  }

  function onWheel(e: React.WheelEvent) {
    e.preventDefault();
    const el = wrapRef.current;
    if (!el) return;
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    const nextScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, view.scale * factor));
    const rect = el.getBoundingClientRect();
    const cx = e.clientX - rect.left - rect.width / 2;
    const cy = e.clientY - rect.top - rect.height / 2;
    const ratio = nextScale / view.scale;
    setView({
      scale: nextScale,
      tx: cx + (view.tx - cx) * ratio,
      ty: cy + (view.ty - cy) * ratio,
    });
  }

  function onPointerDown(e: React.PointerEvent) {
    const target = e.target as Element;
    if (target.getAttribute("data-side-name") !== null) return;
    // Clicking on empty image area: if there's a next-to-place point, place it.
    if (nextToPlace) {
      const pt = screenToImage(e.clientX, e.clientY);
      if (pt) {
        onChange({ ...annotations, [nextToPlace.name]: [
          Math.max(0, Math.min(imageSize.width, pt[0])),
          Math.max(0, Math.min(imageSize.height, pt[1])),
        ] });
      }
      return;
    }
    // Otherwise: pan
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
    panState.current = { startX: e.clientX, startY: e.clientY, tx: view.tx, ty: view.ty };
  }

  function onPointerMove(e: React.PointerEvent) {
    if (panState.current) {
      const { startX, startY, tx, ty } = panState.current;
      setView((v) => ({ ...v, tx: tx + (e.clientX - startX), ty: ty + (e.clientY - startY) }));
      return;
    }
    if (draggingName) {
      const pt = screenToImage(e.clientX, e.clientY);
      if (!pt) return;
      onChange({ ...annotations, [draggingName]: [
        Math.max(0, Math.min(imageSize.width, pt[0])),
        Math.max(0, Math.min(imageSize.height, pt[1])),
      ] });
    }
  }

  function onPointerUp(e: React.PointerEvent) {
    if (panState.current) {
      panState.current = null;
      try { (e.currentTarget as Element).releasePointerCapture(e.pointerId); } catch { /* */ }
    }
    if (draggingName) setDraggingName(null);
  }

  function startDrag(name: string, e: React.PointerEvent) {
    e.stopPropagation();
    setDraggingName(name);
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  }

  const resetView = useCallback(() => setView({ scale: 1, tx: 0, ty: 0 }), []);
  const clearAnnotations = useCallback(() => onChange({}), [onChange]);

  const dispW = imageSize.width * fitScale * view.scale;
  const dispH = imageSize.height * fitScale * view.scale;
  const placed = Object.keys(annotations).length;

  return (
    <div
      ref={cardRef}
      className={[
        "card p-3 flex flex-col gap-2",
        isFullscreen
          ? "fixed inset-0 z-50 rounded-none bg-ink-900 h-screen w-screen"
          : "",
      ].join(" ")}
    >
      <div className="flex items-center gap-2 text-xs text-ink-300">
        <span>
          {nextToPlace
            ? <>click to place: <b className="text-ink-100">{nextToPlace.label}</b></>
            : <>all {SIDE_LANDMARKS.length} points placed — drag to refine</>}
        </span>
        <span className="ml-auto tabular-nums">{placed}/{SIDE_LANDMARKS.length}</span>
        <span className="tabular-nums">{(view.scale * 100).toFixed(0)}%</span>
        <button type="button" className="btn-ghost text-xs px-2 py-1" onClick={resetView}>Reset view</button>
        <button type="button" className="btn-ghost text-xs px-2 py-1" onClick={clearAnnotations}>Clear all</button>
        <button
          type="button"
          className="btn-ghost text-xs px-2 py-1"
          onClick={toggleFullscreen}
          aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
        >
          {isFullscreen ? "Exit fullscreen" : "Fullscreen"}
        </button>
      </div>
      <div
        ref={wrapRef}
        className={[
          "relative w-full rounded-lg bg-ink-900/60 overflow-hidden touch-none select-none cursor-crosshair active:cursor-grabbing",
          isFullscreen ? "flex-1 h-auto" : "h-[480px]",
        ].join(" ")}
        onWheel={onWheel}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
      >
        <div
          className="absolute"
          style={{
            width: dispW, height: dispH,
            left: `calc(50% - ${dispW / 2}px + ${view.tx}px)`,
            top: `calc(50% - ${dispH / 2}px + ${view.ty}px)`,
            willChange: "transform",
          }}
        >
          <img src={imageUrl} alt="side profile" draggable={false}
               className="block w-full h-full" style={{ pointerEvents: "none" }} />
          <svg
            viewBox={`0 0 ${imageSize.width} ${imageSize.height}`}
            className="absolute inset-0 w-full h-full"
            style={{ overflow: "visible" }}
          >
            {SIDE_LANDMARKS.map((s, i) => {
              const p = annotations[s.name];
              if (!p) return null;
              const r = Math.max(1.2, 3.0 / view.scale);
              const color = COLORS[i % COLORS.length];
              const active = draggingName === s.name || hoverName === s.name;
              // Tiny crosshair so the geometric center is visible even when the
              // dot is shrunk for precision placement.
              const tick = r * 0.45;
              return (
                <g key={s.name}>
                  {active && (
                    <text x={p[0] + r * 2.2} y={p[1] - r * 1.6}
                          fill="#fff" fontSize={Math.max(7, 9 / view.scale)}
                          style={{ paintOrder: "stroke", stroke: "#000", strokeWidth: 1.5 }}>
                      {s.label}
                    </text>
                  )}
                  <circle
                    data-side-name={s.name}
                    cx={p[0]} cy={p[1]} r={r}
                    fill={color} stroke="white"
                    strokeWidth={active ? 0.7 / view.scale : 0.35 / view.scale}
                    style={{ cursor: "grab" }}
                    onPointerDown={(e) => startDrag(s.name, e)}
                    onPointerEnter={() => setHoverName(s.name)}
                    onPointerLeave={() => setHoverName((cur) => (cur === s.name ? null : cur))}
                  />
                  <line x1={p[0] - tick} y1={p[1]} x2={p[0] + tick} y2={p[1]}
                        stroke="rgba(255,255,255,0.85)"
                        strokeWidth={0.25 / view.scale} pointerEvents="none" />
                  <line x1={p[0]} y1={p[1] - tick} x2={p[0]} y2={p[1] + tick}
                        stroke="rgba(255,255,255,0.85)"
                        strokeWidth={0.25 / view.scale} pointerEvents="none" />
                </g>
              );
            })}
          </svg>
        </div>
      </div>
      <div className="text-[11px] text-ink-300">
        Click the image to place the highlighted point, then move on. Drag any
        placed point to refine. Wheel to zoom, drag empty area to pan (only
        once all points are placed).
      </div>
    </div>
  );
}
