import type { AnalysisResponse, Sex, SubjectiveFeature } from "@/lib/types";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

async function parseError(res: Response): Promise<string> {
  let message = `Request failed (${res.status})`;
  try {
    const data = (await res.json()) as { detail?: string };
    if (data?.detail) message = data.detail;
  } catch {
    // ignore
  }
  return message;
}

export interface AnalyzeOptions {
  sideImage?: Blob | null;
  sideAnnotations?: Record<string, [number, number]> | null;
  miscRatings?: Record<string, number> | null;
}

export async function analyze(
  image: Blob,
  sex: Sex,
  opts: AnalyzeOptions = {},
): Promise<AnalysisResponse> {
  const form = new FormData();
  form.append("image", image, image instanceof File ? image.name : "frontal.jpg");
  form.append("sex", sex);
  if (opts.sideImage) {
    form.append(
      "side_image",
      opts.sideImage,
      opts.sideImage instanceof File ? opts.sideImage.name : "side.jpg",
    );
  }
  if (opts.sideAnnotations && Object.keys(opts.sideAnnotations).length > 0) {
    form.append("side_annotations", JSON.stringify(opts.sideAnnotations));
  }
  if (opts.miscRatings && Object.keys(opts.miscRatings).length > 0) {
    form.append("misc_ratings", JSON.stringify(opts.miscRatings));
  }

  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AnalysisResponse;
}

export interface ScoreOptions {
  landmarks: [number, number][];
  sex: Sex;
  imageSize: { width: number; height: number };
  maskB64?: string | null;
  sideAnnotations?: Record<string, [number, number]> | null;
  sideImageSize?: { width: number; height: number } | null;
  miscRatings?: Record<string, number> | null;
}

export async function score(opts: ScoreOptions): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE_URL}/api/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      landmarks: opts.landmarks,
      sex: opts.sex,
      image_size: opts.imageSize,
      mask_b64: opts.maskB64 ?? null,
      side_annotations: opts.sideAnnotations ?? null,
      side_image_size: opts.sideImageSize ?? null,
      misc_ratings: opts.miscRatings ?? null,
    }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()) as AnalysisResponse;
}

export async function fetchSubjectiveFeatures(): Promise<SubjectiveFeature[]> {
  const res = await fetch(`${API_BASE_URL}/api/subjective-features`);
  if (!res.ok) throw new Error(await parseError(res));
  const data = (await res.json()) as { features: SubjectiveFeature[] };
  return data.features;
}
