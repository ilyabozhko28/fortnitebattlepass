import { useEffect, useRef, useState } from "react";

interface Props {
  onCapture: (file: File, previewUrl: string) => void;
  previewUrl: string | null;
}

export function WebcamCapture({ onCapture, previewUrl }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    return () => {
      stop();
    };
  }, []);

  async function start() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 960 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setActive(true);
    } catch (e) {
      setError((e as Error).message || "Could not access webcam");
    }
  }

  function stop() {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setActive(false);
  }

  function snap() {
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
        const url = URL.createObjectURL(blob);
        onCapture(file, url);
        stop();
      },
      "image/jpeg",
      0.92,
    );
  }

  return (
    <div className="card p-4 flex flex-col gap-3">
      <div className="relative rounded-xl overflow-hidden bg-ink-900/60 min-h-[280px] flex items-center justify-center">
        {previewUrl && !active ? (
          <img src={previewUrl} alt="capture" className="max-h-[360px] w-auto object-contain" />
        ) : (
          <video
            ref={videoRef}
            playsInline
            muted
            className={active ? "max-h-[360px] w-auto" : "hidden"}
          />
        )}
        {!active && !previewUrl && (
          <div className="text-center px-6 py-10">
            <div className="text-ink-100 font-medium">Webcam capture</div>
            <div className="text-xs text-ink-300 mt-1">Start the camera, align your face, then snap.</div>
          </div>
        )}
        {active && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <div className="w-48 h-64 rounded-full border-2 border-white/30 border-dashed" />
          </div>
        )}
      </div>
      <div className="flex gap-2">
        {!active ? (
          <button type="button" className="btn-ghost" onClick={start}>
            {previewUrl ? "Retake" : "Start camera"}
          </button>
        ) : (
          <>
            <button type="button" className="btn-primary" onClick={snap}>
              Snap
            </button>
            <button type="button" className="btn-ghost" onClick={stop}>
              Cancel
            </button>
          </>
        )}
      </div>
      {error && <div className="text-xs text-bad">{error}</div>}
    </div>
  );
}
