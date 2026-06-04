import { useCallback, useRef, useState } from "react";

interface Props {
  onPick: (file: File, previewUrl: string) => void;
  previewUrl: string | null;
}

export function ImageUploader({ onPick, previewUrl }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith("image/")) return;
      const url = URL.createObjectURL(file);
      onPick(file, url);
    },
    [onPick],
  );

  return (
    <div className="card p-4 flex flex-col gap-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const file = e.dataTransfer.files[0];
          if (file) handleFile(file);
        }}
        onClick={() => inputRef.current?.click()}
        className={[
          "relative cursor-pointer rounded-xl border-2 border-dashed transition flex items-center justify-center min-h-[280px] overflow-hidden",
          dragging ? "border-accent-500 bg-accent-500/5" : "border-ink-700 hover:border-ink-500",
        ].join(" ")}
      >
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="preview"
            className="max-h-[360px] w-auto object-contain"
          />
        ) : (
          <div className="text-center px-6 py-10">
            <div className="text-ink-100 font-medium">Drop a frontal photo here</div>
            <div className="text-xs text-ink-300 mt-1">or click to browse</div>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </div>
      <div className="text-xs text-ink-300">
        Tip: shoot facing the camera, even light, hair off the forehead.
      </div>
    </div>
  );
}
