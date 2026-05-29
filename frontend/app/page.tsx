import Link from "next/link";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
      <Sparkles size={48} className="text-zinc-400" />
      <h1 className="text-3xl font-bold tracking-tight">Content Engine</h1>
      <p className="text-zinc-400 text-center max-w-md">
        Generate high-quality, high-IQ content for X/Twitter using a multi-agent AI pipeline.
        Smart. Insightful. Never slop.
      </p>
      <Link href="/generate">
        <Button size="lg">Start Generating</Button>
      </Link>
    </div>
  );
}
