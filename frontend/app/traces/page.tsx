"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { listRuns, type RunSummary } from "@/lib/api";

export default function TracesPage() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRuns(50).then(setRuns).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const statusColor = (s: string) => {
    if (s === "completed") return "bg-green-900 text-green-300";
    if (s === "failed") return "bg-red-900 text-red-300";
    if (s === "running") return "bg-yellow-900 text-yellow-300";
    return "bg-zinc-800 text-zinc-400";
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Traces</h1>

      {loading && <p className="text-zinc-500 text-sm">Loading...</p>}

      {!loading && runs.length === 0 && (
        <p className="text-zinc-500 text-sm">No runs yet. Generate some content first.</p>
      )}

      <div className="space-y-2">
        {runs.map((run) => (
          <Link key={run.run_id} href={`/traces/${run.run_id}`}>
            <Card className="bg-zinc-900 border-zinc-800 hover:border-zinc-600 transition-colors cursor-pointer">
              <CardContent className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge className={statusColor(run.status)}>{run.status}</Badge>
                  <Badge variant="outline">{run.content_type}</Badge>
                  <span className="text-sm text-zinc-300 truncate max-w-[300px]">{run.topic}</span>
                </div>
                <span className="text-xs text-zinc-500">
                  {new Date(run.created_at * 1000).toLocaleString()}
                </span>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
