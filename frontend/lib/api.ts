const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export interface GenerateRequest {
  topic: string;
  content_type: string;
  urls?: string[];
  voice_description?: string;
  target_length?: string;
  original_tweet_text?: string;
  user_id?: string;
  max_draft_iterations?: number;
}

export interface GenerateResponse {
  run_id: string;
  status: string;
  message: string;
}

export interface RunStatus {
  run_id: string;
  status: string;
  current_agent: string;
  progress_pct: number;
  final_content: string | null;
  draft_iteration: number;
  error: string | null;
}

export interface RunResult {
  run_id: string;
  status: string;
  final_content: string;
  content_type: string;
  all_angles: Record<string, unknown>[];
  selected_angles: Record<string, unknown>[];
  draft_history: string[];
  critic_feedback_history: Record<string, unknown>[];
  fact_check_results: Record<string, unknown>[];
  voice_review: Record<string, unknown> | null;
  traces: TraceEntry[];
  trace_summary: Record<string, unknown>;
  error: string | null;
}

export interface TraceEntry {
  node_name: string;
  started_at: number;
  finished_at: number;
  duration_ms: number;
  input_summary: string;
  output_summary: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  error: string | null;
}

export interface RunSummary {
  run_id: string;
  status: string;
  topic: string;
  content_type: string;
  created_at: number;
  current_agent: string;
}

export async function startGeneration(req: GenerateRequest): Promise<GenerateResponse> {
  return fetchAPI("/generate", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function getRunStatus(runId: string): Promise<RunStatus> {
  return fetchAPI(`/runs/${runId}`);
}

export async function getRunResult(runId: string): Promise<RunResult> {
  return fetchAPI(`/runs/${runId}/result`);
}

export async function listRuns(limit = 20): Promise<RunSummary[]> {
  return fetchAPI(`/runs?limit=${limit}`);
}

export async function uploadFile(
  file: File,
  type: "voice" | "context",
  userId = "default"
): Promise<{ file_id: string; filename: string; chunks_stored: number }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", userId);

  const res = await fetch(`${API_BASE}/upload/${type}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return res.json();
}

export async function listUploads(userId = "default") {
  return fetchAPI<
    { file_id: string; filename: string; upload_type: string; chunk_count: number; uploaded_at: number }[]
  >(`/uploads/${userId}`);
}

export async function deleteUpload(fileId: string, userId = "default") {
  return fetchAPI(`/uploads/${fileId}?user_id=${userId}`, { method: "DELETE" });
}
