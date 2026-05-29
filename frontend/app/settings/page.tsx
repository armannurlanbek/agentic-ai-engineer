"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const [voiceDesc, setVoiceDesc] = useState("");
  const [defaultType, setDefaultType] = useState("tweet");
  const [defaultLength, setDefaultLength] = useState("medium");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("content-engine-settings");
    if (stored) {
      const parsed = JSON.parse(stored);
      setVoiceDesc(parsed.voiceDesc || "");
      setDefaultType(parsed.defaultType || "tweet");
      setDefaultLength(parsed.defaultLength || "medium");
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem(
      "content-engine-settings",
      JSON.stringify({ voiceDesc, defaultType, defaultLength })
    );
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-sm">Voice Description</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder="Describe your writing voice... e.g. 'Write like Paul Graham — clear, conversational, contrarian with strong opinions'"
            value={voiceDesc}
            onChange={(e) => setVoiceDesc(e.target.value)}
            className="min-h-[100px] bg-zinc-950 border-zinc-700"
          />
        </CardContent>
      </Card>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-sm">Default Content Type</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-2">
          {["tweet", "thread", "essay", "article"].map((t) => (
            <button
              key={t}
              onClick={() => setDefaultType(t)}
              className={`px-3 py-1.5 text-sm rounded border capitalize transition-colors ${
                defaultType === t
                  ? "bg-zinc-100 text-zinc-900 border-zinc-100"
                  : "bg-zinc-900 text-zinc-400 border-zinc-700"
              }`}
            >
              {t}
            </button>
          ))}
        </CardContent>
      </Card>

      <Card className="bg-zinc-900 border-zinc-800">
        <CardHeader>
          <CardTitle className="text-sm">Default Length</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-2">
          {["short", "medium", "long"].map((l) => (
            <button
              key={l}
              onClick={() => setDefaultLength(l)}
              className={`px-3 py-1.5 text-sm rounded border capitalize transition-colors ${
                defaultLength === l
                  ? "bg-zinc-100 text-zinc-900 border-zinc-100"
                  : "bg-zinc-900 text-zinc-400 border-zinc-700"
              }`}
            >
              {l}
            </button>
          ))}
        </CardContent>
      </Card>

      <Button onClick={handleSave}>{saved ? "Saved!" : "Save Settings"}</Button>
    </div>
  );
}
