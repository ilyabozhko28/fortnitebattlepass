import type { Sex } from "@/lib/types";

interface Props {
  value: Sex | null;
  onChange: (sex: Sex) => void;
}

export function SexSelector({ value, onChange }: Props) {
  return (
    <div className="card p-4">
      <div className="text-sm text-ink-300 mb-2">Sex (required — tier ranges differ)</div>
      <div className="grid grid-cols-2 gap-2">
        {(["male", "female"] as const).map((s) => {
          const active = value === s;
          return (
            <button
              key={s}
              type="button"
              onClick={() => onChange(s)}
              className={[
                "rounded-xl px-4 py-3 text-sm font-medium capitalize transition border",
                active
                  ? "border-accent-500 bg-accent-500/15 text-white"
                  : "border-ink-700 bg-ink-900/50 text-ink-200 hover:border-ink-500",
              ].join(" ")}
            >
              {s}
            </button>
          );
        })}
      </div>
    </div>
  );
}
