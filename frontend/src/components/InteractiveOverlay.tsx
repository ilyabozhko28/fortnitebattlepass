import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyLandmark } from "@/lib/landmarks";
import { GROUP_COLORS, KEY_INDEX_SET, KEY_LANDMARKS } from "@/lib/landmarks";

type Point = [number, number];
type Group = KeyLandmark["group"];

interface Props {
  imageUrl: string;
  imageSize: { width: number; height: number };
  landmarks: Point[];
  onChange: (next: Point[]) => void;
  onReset: () => void;
}

interface ViewState {
  scale: number;
  tx: number;
  ty: number;
}

const MIN_SCALE = 0.5;
const MAX_SCALE = 20;

const ALL_GROUPS: Group[] = ["eyes", "brows", "nose", "mouth", "cheeks", "jaw", "face"];

export function InteractiveOverlay({
  imageUrl,
  imageSize,
  landmarks,
  onChange,
  onReset,
}: Props) {
  const cardRef = useRef<HTMLDivElement | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [view, setView] = useState<ViewState>({ scale: 1, tx: 0, ty: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [containerSize, setContainerSize] = useState({ width: 1, height: 1 });
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null);
  const panState = useRef<{ startX: number; startY: number; tx: number; ty: number } | null>(
    null,
  );
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const [visibleGroups, setVisibleGroups] = useState<Set<Group>>(
    () => new Set(ALL_GROUPS),
  );
  const [showBackground, setShowBackground] = useState(false);

  function toggleGroup(g: Group) {
    setVisibleGroups((prev) => {
      const next = new Set(prev);
      if (next.has(g)) next.delete(g);
      else next.add(g);
      return next;
    });
  }

  function setAllGroups(visible: boolean) {
    setVisibleGroups(visible ? new Set(ALL_GROUPS) : new Set());
  }

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

  // Fit-to-container scale recompute when image or container size changes.
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const observer = new ResizeObserver(() => {
      const rect = el.getBoundingClientRect();
      setContainerSize({ width: rect.width, height: rect.height });
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const fitScale = useMemo(() => {
    if (containerSize.width <= 0 || containerSize.height <= 0) return 1;
    return Math.min(
      containerSize.width / imageSize.width,
      containerSize.height / imageSize.height,
    );
  }, [containerSize, imageSize]);

  // Reset view when the image changes.
  useEffect(() => {
    setView({ scale: 1, tx: 0, ty: 0 });
  }, [imageUrl]);

  function screenToImage(clientX: number, clientY: number): Point | null {
    const el = wrapRef.current;
    if (!el) return null;
    const rect = el.getBoundingClientRect();
    const dispW = imageSize.width * fitScale * view.scale;
    const dispH = imageSize.height * fitScale * view.scale;
    const offsetX = (rect.width - dispW) / 2 + view.tx;
    const offsetY = (rect.height - dispH) / 2 + view.ty;
    const xLocal = clientX - rect.left - offsetX;
    const yLocal = clientY - rect.top - offsetY;
    const imgX = xLocal / (fitScale * view.scale);
    const imgY = yLocal / (fitScale * view.scale);
    return [imgX, imgY];
  }

  function onWheel(e: React.WheelEvent) {
    e.preventDefault();
    const el = wrapRef.current;
    if (!el) return;
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    const nextScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, view.scale * factor));
    // Zoom toward cursor: keep the image point under the cursor fixed in screen space.
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
    // Landmark drag handled separately; this handles background pan.
    const target = e.target as Element;
    if (target.getAttribute("data-landmark-index") !== null) return;
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
    panState.current = {
      startX: e.clientX,
      startY: e.clientY,
      tx: view.tx,
      ty: view.ty,
    };
  }

  function onPointerMove(e: React.PointerEvent) {
    if (panState.current) {
      const { startX, startY, tx, ty } = panState.current;
      setView((v) => ({ ...v, tx: tx + (e.clientX - startX), ty: ty + (e.clientY - startY) }));
      return;
    }
    if (draggingIndex !== null) {
      const pt = screenToImage(e.clientX, e.clientY);
      if (!pt) return;
      const next = landmarks.slice();
      next[draggingIndex] = [
        Math.max(0, Math.min(imageSize.width, pt[0])),
        Math.max(0, Math.min(imageSize.height, pt[1])),
      ];
      onChange(next);
    }
  }

  function onPointerUp(e: React.PointerEvent) {
    if (panState.current) {
      panState.current = null;
      try {
        (e.currentTarget as Element).releasePointerCapture(e.pointerId);
      } catch {
        // pointer may not have been captured (touch race)
      }
    }
    if (draggingIndex !== null) {
      setDraggingIndex(null);
    }
  }

  function startLandmarkDrag(idx: number, e: React.PointerEvent) {
    e.stopPropagation();
    setDraggingIndex(idx);
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  }

  function resetView() {
    setView({ scale: 1, tx: 0, ty: 0 });
  }

  const dispW = imageSize.width * fitScale * view.scale;
  const dispH = imageSize.height * fitScale * view.scale;

  const keyByIndex = useMemo(() => {
    const m = new Map<number, (typeof KEY_LANDMARKS)[number]>();
    for (const k of KEY_LANDMARKS) m.set(k.index, k);
    return m;
  }, []);

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
        <span className="hidden sm:inline">
          scroll: zoom · drag: pan · drag a colored dot to move it
        </span>
        <span className="ml-auto tabular-nums">{(view.scale * 100).toFixed(0)}%</span>
        <button type="button" className="btn-ghost text-xs px-2 py-1" onClick={resetView}>
          Reset view
        </button>
        <button type="button" className="btn-ghost text-xs px-2 py-1" onClick={onReset}>
          Reset points
        </button>
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
          "relative w-full rounded-lg bg-ink-900/60 overflow-hidden touch-none select-none cursor-grab active:cursor-grabbing",
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
            width: dispW,
            height: dispH,
            left: `calc(50% - ${dispW / 2}px + ${view.tx}px)`,
            top: `calc(50% - ${dispH / 2}px + ${view.ty}px)`,
            willChange: "transform",
          }}
        >
          <img
            ref={imgRef}
            src={imageUrl}
            alt="analyzed face"
            draggable={false}
            className="block w-full h-full"
            style={{ pointerEvents: "none" }}
          />
          <svg
            viewBox={`0 0 ${imageSize.width} ${imageSize.height}`}
            className="absolute inset-0 w-full h-full"
            style={{ overflow: "visible" }}
          >
            {/* Background dots: the 438 non-key landmarks. */}
            {showBackground && (
              <g>
                {landmarks.map(([x, y], i) =>
                  KEY_INDEX_SET.has(i) ? null : (
                    <circle
                      key={i}
                      cx={x}
                      cy={y}
                      r={Math.max(0.35, 0.9 / view.scale)}
                      fill="rgba(255,255,255,0.35)"
                      pointerEvents="none"
                    />
                  ),
                )}
              </g>
            )}
            {/* Key landmarks: small, colored, draggable with a center crosshair. */}
            <g>
              {KEY_LANDMARKS.map((k) => {
                if (!visibleGroups.has(k.group)) return null;
                const p = landmarks[k.index];
                if (!p) return null;
                const r = Math.max(1.2, 3.0 / view.scale);
                const tick = r * 0.45;
                const color = GROUP_COLORS[k.group];
                const active = draggingIndex === k.index || hoverIndex === k.index;
                return (
                  <g key={k.index}>
                    {active && (
                      <text
                        x={p[0] + r * 2.2}
                        y={p[1] - r * 1.6}
                        fill="#fff"
                        fontSize={Math.max(7, 9 / view.scale)}
                        style={{ paintOrder: "stroke", stroke: "#000", strokeWidth: 1.5 }}
                      >
                        {k.label}
                      </text>
                    )}
                    <circle
                      data-landmark-index={k.index}
                      cx={p[0]}
                      cy={p[1]}
                      r={r}
                      fill={color}
                      stroke="white"
                      strokeWidth={active ? 0.7 / view.scale : 0.35 / view.scale}
                      style={{ cursor: "grab" }}
                      onPointerDown={(e) => startLandmarkDrag(k.index, e)}
                      onPointerEnter={() => setHoverIndex(k.index)}
                      onPointerLeave={() => setHoverIndex((cur) => (cur === k.index ? null : cur))}
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
            </g>
          </svg>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-[11px]">
        <div className="text-ink-300 mr-1">Show:</div>
        {ALL_GROUPS.map((g) => {
          const on = visibleGroups.has(g);
          return (
            <button
              key={g}
              type="button"
              onClick={() => toggleGroup(g)}
              className={[
                "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 border transition",
                on
                  ? "border-ink-500 bg-ink-700/60 text-ink-100"
                  : "border-ink-700 bg-transparent text-ink-300 line-through opacity-60",
              ].join(" ")}
            >
              <span
                className="inline-block w-2.5 h-2.5 rounded-full"
                style={{ background: GROUP_COLORS[g] }}
              />
              {g}
            </button>
          );
        })}
        <button
          type="button"
          onClick={() => setAllGroups(true)}
          className="ml-1 text-ink-300 hover:text-ink-100 underline-offset-2 hover:underline"
        >
          all
        </button>
        <button
          type="button"
          onClick={() => setAllGroups(false)}
          className="text-ink-300 hover:text-ink-100 underline-offset-2 hover:underline"
        >
          none
        </button>
        <label className="ml-auto inline-flex items-center gap-1.5 text-ink-300 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={showBackground}
            onChange={(e) => setShowBackground(e.target.checked)}
            className="accent-accent-500"
          />
          background mesh ({landmarks.length - KEY_INDEX_SET.size} pts)
        </label>
      </div>
    </div>
  );
}
