"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, Trash2, FileText } from "lucide-react";
import { uploadFile, listUploads, deleteUpload } from "@/lib/api";

interface UploadItem {
  file_id: string;
  filename: string;
  upload_type: string;
  chunk_count: number;
  uploaded_at: number;
}

export default function UploadsPage() {
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const [uploading, setUploading] = useState(false);

  const refresh = useCallback(() => {
    listUploads("default").then(setUploads).catch(() => {});
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const handleUpload = async (type: "voice" | "context") => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".txt,.md,.pdf,.docx";
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      setUploading(true);
      try {
        await uploadFile(file, type);
        refresh();
      } catch {
      } finally {
        setUploading(false);
      }
    };
    input.click();
  };

  const handleDelete = async (fileId: string) => {
    await deleteUpload(fileId);
    refresh();
  };

  const voiceUploads = uploads.filter((u) => u.upload_type === "voice");
  const contextUploads = uploads.filter((u) => u.upload_type === "context");

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Uploads</h1>

      <Tabs defaultValue="voice">
        <TabsList className="bg-zinc-900">
          <TabsTrigger value="voice">Voice Samples</TabsTrigger>
          <TabsTrigger value="context">Context Documents</TabsTrigger>
        </TabsList>

        <TabsContent value="voice" className="space-y-4">
          <Card className="bg-zinc-900 border-zinc-800 border-dashed">
            <CardContent className="pt-6 flex flex-col items-center gap-3">
              <Upload className="text-zinc-500" />
              <p className="text-sm text-zinc-400">Upload writing samples to match your voice</p>
              <Button variant="outline" size="sm" onClick={() => handleUpload("voice")} disabled={uploading}>
                {uploading ? "Uploading..." : "Upload Voice Sample"}
              </Button>
            </CardContent>
          </Card>
          {voiceUploads.map((u) => (
            <Card key={u.file_id} className="bg-zinc-900 border-zinc-800">
              <CardContent className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-zinc-500" />
                  <span className="text-sm">{u.filename}</span>
                  <Badge variant="outline" className="text-xs">{u.chunk_count} chunks</Badge>
                </div>
                <Button variant="ghost" size="sm" onClick={() => handleDelete(u.file_id)}>
                  <Trash2 size={14} />
                </Button>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="context" className="space-y-4">
          <Card className="bg-zinc-900 border-zinc-800 border-dashed">
            <CardContent className="pt-6 flex flex-col items-center gap-3">
              <Upload className="text-zinc-500" />
              <p className="text-sm text-zinc-400">Upload reference documents for grounding</p>
              <Button variant="outline" size="sm" onClick={() => handleUpload("context")} disabled={uploading}>
                {uploading ? "Uploading..." : "Upload Context Document"}
              </Button>
            </CardContent>
          </Card>
          {contextUploads.map((u) => (
            <Card key={u.file_id} className="bg-zinc-900 border-zinc-800">
              <CardContent className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-zinc-500" />
                  <span className="text-sm">{u.filename}</span>
                  <Badge variant="outline" className="text-xs">{u.chunk_count} chunks</Badge>
                </div>
                <Button variant="ghost" size="sm" onClick={() => handleDelete(u.file_id)}>
                  <Trash2 size={14} />
                </Button>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
