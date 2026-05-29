"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getRunResult, type RunResult } from "@/lib/api";
import { CheckCircle, XCircle, Clock } from "lucide-react";

export default function TraceDetailPage() {
  const params = useParams();
  const runId = params.id as string;
  const [result, setResult] = useState<RunResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (runId) {
      getRunResult(runId).then(setResult).catch(() => {}).finally(() => setLoading(false));
    }
  }, [runId]);

  if (loading) return <p className="text-zinc-500">Loading trace...</p>;
  if (!result) return <p className="text-zinc-500">Trace not found.</p>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">Trace</h1>
        <Badge variant="outline">{result.content_type}</Badge>
        <Badge variant={result.status === "completed" ? "default" : "destructive"}>
          {result.status}
        </Badge>
      </div>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-sm">Agent Timeline</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {result.traces.map((trace, i) => (
            <div key={i} className="flex items-start gap-3 text-sm">
              <div className="mt-0.5">
                {trace.error ? (
                  <XCircle size={16} className="text-red-400" />
                ) : (
                  <CheckCircle size={16} className="text-green-400" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-zinc-200">{trace.node_name}</span>
                  <span className="text-zinc-500 flex items-center gap-1">
                    <Clock size={12} />
                    {(trace.duration_ms / 1000).toFixed(1)}s
                  </span>
                  {trace.total_tokens > 0 && (
                    <span className="text-zinc-600">{trace.total_tokens} tokens</span>
                  )}
                </div>
                {trace.output_summary && (
                  <p className="text-zinc-500 truncate text-xs mt-0.5">{trace.output_summary}</p>
                )}
                {trace.error && <p className="text-red-400 text-xs mt-0.5">{trace.error}</p>}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {result.draft_history.length > 0 && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-sm">Draft History ({result.draft_history.length} versions)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {result.draft_history.map((draft, i) => (
              <details key={i} className="text-sm">
                <summary className="text-zinc-400 cursor-pointer hover:text-zinc-200">
                  Draft {i + 1}
                  {result.critic_feedback_history[i] && (
                    <span className="ml-2 text-zinc-600">
                      Score: {(result.critic_feedback_history[i] as Record<string, number>).score?.toFixed(1)}
                    </span>
                  )}
                </summary>
                <pre className="mt-2 whitespace-pre-wrap text-zinc-300 bg-zinc-950 p-3 rounded text-xs border border-zinc-800">
                  {draft}
                </pre>
              </details>
            ))}
          </CardContent>
        </Card>
      )}

      {result.fact_check_results.length > 0 && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-sm">Fact Check Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {result.fact_check_results.map((fc: Record<string, unknown>, i: number) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  {fc.action === "keep" ? (
                    <CheckCircle size={14} className="text-green-400 shrink-0" />
                  ) : fc.action === "remove" ? (
                    <XCircle size={14} className="text-red-400 shrink-0" />
                  ) : (
                    <Badge variant="outline" className="text-xs">softened</Badge>
                  )}
                  <span className="text-zinc-400 truncate">{fc.claim_text as string}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {result.final_content && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-sm">Final Output</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap text-zinc-200 bg-zinc-950 p-4 rounded text-sm border border-zinc-800">
              {result.final_content}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
