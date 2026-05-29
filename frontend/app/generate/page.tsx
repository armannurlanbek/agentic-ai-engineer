"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Copy, Check, Loader2 } from "lucide-react";
import { startGeneration, getRunStatus, getRunResult, type RunStatus, type RunResult } from "@/lib/api";

const CONTENT_TYPES = [
  { value: "quote_retweet", label: "Quote RT" },
  { value: "thread", label: "Thread" },
  { value: "essay", label: "Essay" },
  { value: "article", label: "Article" },
];

const AGENT_LABELS: Record<string, string> = {
  pending: "Waiting...",
  discovery: "Discovering sources",
  retrieval: "Retrieving context",
  angle: "Generating angles",
  draft_writer: "Writing draft",
  critic: "Reviewing draft",
  fact_checker: "Checking facts",
  voice_reviewer: "Matching voice",
  done: "Complete",
  failed: "Failed",
};

export default function GeneratePage() {
  const [topic, setTopic] = useState("");
  const [contentType, setContentType] = useState("thread");
  const [targetLength, setTargetLength] = useState("medium");
  const [originalTweet, setOriginalTweet] = useState("");
  const [voiceDesc, setVoiceDesc] = useState("");

  const [runId, setRunId] = useState<string | null>(null);
  const [status, setStatus] = useState<RunStatus | null>(null);
  const [result, setResult] = useState<RunResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxProgress, setMaxProgress] = useState(0);

  const pollStatus = useCallback(async (rid: string) => {
    try {
      const s = await getRunStatus(rid);
      setStatus(s);
      setMaxProgress((prev) => Math.max(prev, s.progress_pct));

      if (s.status === "completed") {
        const r = await getRunResult(rid);
        setResult(r);
        setLoading(false);
      } else if (s.status === "failed") {
        setError(s.error || "Pipeline failed");
        setLoading(false);
      }
      return s.status;
    } catch {
      return "running";
    }
  }, []);

  useEffect(() => {
    if (!runId || !loading) return;
    const interval = setInterval(async () => {
      const s = await pollStatus(runId);
      if (s === "completed" || s === "failed") clearInterval(interval);
    }, 2000);
    return () => clearInterval(interval);
  }, [runId, loading, pollStatus]);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setError(null);
    setResult(null);
    setStatus(null);
    setMaxProgress(0);
    setLoading(true);
    try {
      const res = await startGeneration({
        topic,
        content_type: contentType,
        target_length: targetLength,
        original_tweet_text: originalTweet,
        voice_description: voiceDesc,
      });
      setRunId(res.run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start");
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.final_content) {
      navigator.clipboard.writeText(result.final_content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Generate Content</h1>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardContent className="pt-6 space-y-4">
          <Textarea
            placeholder="What do you want to write about?"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="min-h-[100px] bg-zinc-950 border-zinc-700"
          />

          <div className="flex flex-wrap gap-2">
            {CONTENT_TYPES.map((ct) => (
              <button
                key={ct.value}
                onClick={() => setContentType(ct.value)}
                className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
                  contentType === ct.value
                    ? "bg-zinc-100 text-zinc-900 border-zinc-100"
                    : "bg-zinc-900 text-zinc-400 border-zinc-700 hover:border-zinc-500"
                }`}
              >
                {ct.label}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            {["short", "medium", "long"].map((len) => (
              <button
                key={len}
                onClick={() => setTargetLength(len)}
                className={`px-3 py-1 text-xs rounded border transition-colors capitalize ${
                  targetLength === len
                    ? "bg-zinc-700 text-zinc-100 border-zinc-600"
                    : "bg-zinc-900 text-zinc-500 border-zinc-700"
                }`}
              >
                {len}
              </button>
            ))}
          </div>

          {contentType === "quote_retweet" && (
            <Textarea
              placeholder="Original tweet text to quote..."
              value={originalTweet}
              onChange={(e) => setOriginalTweet(e.target.value)}
              className="min-h-[60px] bg-zinc-950 border-zinc-700"
            />
          )}

          <details className="text-sm">
            <summary className="text-zinc-500 cursor-pointer hover:text-zinc-300">
              Voice description (optional)
            </summary>
            <Textarea
              placeholder="e.g. Write like Paul Graham — clear, conversational, contrarian..."
              value={voiceDesc}
              onChange={(e) => setVoiceDesc(e.target.value)}
              className="mt-2 min-h-[60px] bg-zinc-950 border-zinc-700"
            />
          </details>

          <Button onClick={handleGenerate} disabled={loading || !topic.trim()} className="w-full">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              "Generate"
            )}
          </Button>
        </CardContent>
      </Card>

      {loading && status && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              {AGENT_LABELS[status.current_agent] || status.current_agent}
              {status.draft_iteration > 0 && (
                <Badge variant="outline" className="ml-2">
                  Draft iteration {status.draft_iteration}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={maxProgress} className="h-2" />
            <div className="flex justify-between text-xs text-zinc-500 mt-1">
              <span>Discovery</span>
              <span>Draft/Critic</span>
              <span>Fact Check</span>
              <span>Voice</span>
            </div>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="bg-red-950/30 border-red-800">
          <CardContent className="pt-6">
            <p className="text-red-400 text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Output</CardTitle>
            <Button variant="ghost" size="sm" onClick={handleCopy}>
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="whitespace-pre-wrap text-zinc-200 leading-relaxed font-mono text-sm bg-zinc-950 p-4 rounded-md border border-zinc-800">
              {result.final_content}
            </div>

            {result.traces.length > 0 && (
              <div className="text-xs text-zinc-500 flex gap-4">
                <span>
                  {result.trace_summary.total_duration_ms
                    ? `${(Number(result.trace_summary.total_duration_ms) / 1000).toFixed(1)}s`
                    : ""}
                </span>
                <span>{result.draft_history.length} draft(s)</span>
                <span>{result.fact_check_results.length} claims checked</span>
                <a href={`/traces/${result.run_id}`} className="text-zinc-400 hover:text-zinc-200 underline">
                  View full trace
                </a>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
