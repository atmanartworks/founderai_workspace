import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";

export const StorageInfo = () => {
  const [fileCount, setFileCount] = useState(0);
  const [storageUsed, setStorageUsed] = useState(0);
  const storageLimit = 1024 * 1024 * 1024; // 1 GB limit

  useEffect(() => {
    fetchStorageInfo();
  }, []);

  const fetchStorageInfo = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Primary source: vault_files table (exclude folders)
      const { data: dbFiles, error: dbError } = await supabase
        .from("vault_files")
        .select("file_size, is_folder")
        .eq("user_id", user.id)
        .eq("is_folder", false);

      if (dbError) throw dbError;

      if (dbFiles) {
        setFileCount(dbFiles.length);
        const totalBytesDB = dbFiles.reduce((acc, f) => acc + (f.file_size || 0), 0);
        setStorageUsed(totalBytesDB);
      }
    } catch (error) {
      console.error("Error fetching storage info:", error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const value = Math.round((bytes / Math.pow(k, i)) * 100) / 100;
    return `${value} ${sizes[i]}`;
  };

  const totalGB = (storageLimit / (1024 * 1024 * 1024)).toFixed(0);
  const percentUsed = (storageUsed / storageLimit) * 100;

  return (
    <div className="space-y-3">
      <Button variant="outline" className="w-full justify-start text-sm" size="sm">
        📁 {fileCount} Files
      </Button>

      <div className="p-3 border rounded-lg bg-muted/30">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium flex items-center gap-2">📦 Storage</span>
          <span className="text-xs text-muted-foreground">{totalGB} GB Total</span>
        </div>

        <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
          <div 
            className="bg-primary h-2 transition-all" 
            style={{ width: `${Math.min(percentUsed, 100)}%` }}
          ></div>
        </div>

        <div className="mt-1 text-xs text-muted-foreground text-right">
          {formatFileSize(storageUsed)} used of {totalGB} GB
        </div>
      </div>
    </div>
  );
};
