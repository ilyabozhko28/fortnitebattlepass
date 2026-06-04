import { useEffect, useRef } from "react";

interface Props {
  imageUrl: string;
  landmarks: [number, number][];
  imageSize: { width: number; height: number };
}

export function LandmarkOverlay({ imageUrl, landmarks, imageSize }: Props) {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  function draw() {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    if (!canvas || !img) return;

    const displayWidth = img.clientWidth;
    const displayHeight = img.clientHeight;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = displayWidth * dpr;
    canvas.height = displayHeight * dpr;
    canvas.style.width = `${displayWidth}px`;
    canvas.style.height = `${displayHeight}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, displayWidth, displayHeight);

    const sx = displayWidth / imageSize.width;
    const sy = displayHeight / imageSize.height;

    ctx.fillStyle = "rgba(124, 92, 255, 0.85)";
    for (const [x, y] of landmarks) {
      ctx.beginPath();
      ctx.arc(x * sx, y * sy, 1.4, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;
    if (img.complete) draw();
    const onLoad = () => draw();
    img.addEventListener("load", onLoad);
    window.addEventListener("resize", draw);
    return () => {
      img.removeEventListener("load", onLoad);
      window.removeEventListener("resize", draw);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageUrl, landmarks, imageSize]);

  return (
    <div ref={wrapRef} className="card p-3">
      <div className="relative inline-block">
        <img
          ref={imgRef}
          src={imageUrl}
          alt="analyzed face"
          className="max-h-[480px] w-auto rounded-lg"
        />
        <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none rounded-lg" />
      </div>
    </div>
  );
}
