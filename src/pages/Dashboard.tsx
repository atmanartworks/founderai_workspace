import { Navbar } from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRef, useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

const VaultFiles = () => {
  const { toast } = useToast();
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [files, setFiles] = useState<any[]>([]);
  const [fileCount, setFileCount] = useState(0);
  const [storageUsed, setStorageUsed] = useState(0);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch files from Supabase storage
  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase.storage
        .from("chat-files")
        .list(user.id, { limit: 100 });

      if (error) throw error;

      if (data) {
        setFiles(data);
        setFileCount(data.length);
        
        // Calculate total storage used
        const totalBytes = data.reduce((acc, file) => acc + (file.metadata?.size || 0), 0);
        setStorageUsed(totalBytes);

        // Select first file by default
        if (data.length > 0 && !selectedFile) {
          setSelectedFile(data[0]);
        }
      }
    } catch (error) {
      console.error("Error fetching files:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const fileExt = file.name.split(".").pop();
      const fileName = `${Math.random()}.${fileExt}`;
      const filePath = `${user.id}/${fileName}`;

      const { error: uploadError } = await supabase.storage
        .from("chat-files")
        .upload(filePath, file);

      if (uploadError) throw uploadError;

      toast({
        title: "Success",
        description: "File uploaded successfully!",
      });

      fetchFiles();
    } catch (error) {
      console.error("Error uploading file:", error);
      toast({
        title: "Error",
        description: "Failed to upload file",
        variant: "destructive",
      });
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <Navbar />
      <h1 className="text-3xl font-bold mb-6">File Explorer</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - File Explorer */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <input
              type="text"
              placeholder="Search"
              className="border border-border rounded-md px-2 py-1 text-sm w-full"
            />
            <Button variant="outline" size="sm">
              Filter
            </Button>
          </div>

          <div className="text-sm text-muted-foreground mb-3">/ MyVault /</div>

          <div className="space-y-1 border border-border rounded-md p-2 h-72 overflow-y-auto">
            {loading ? (
              <p className="text-sm text-muted-foreground text-center py-4">Loading files...</p>
            ) : files.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No files uploaded yet</p>
            ) : (
              files.map((file, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedFile(file)}
                  className={`flex items-center px-2 py-1 rounded cursor-pointer ${
                    selectedFile?.name === file.name ? "bg-primary/10 text-primary" : "hover:bg-muted"
                  }`}
                >
                  <span className="mr-2">📄</span> {file.name}
                </div>
              ))
            )}
          </div>

          {/* Hidden file input */}
          <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileChange} />

          <div className="flex justify-center mt-4">
            <Button onClick={handleUploadClick}>Upload</Button>
          </div>
        </Card>

        {/* Right Panel - Preview */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">
            Preview: {selectedFile?.name || "No file selected"}
          </h2>

          {selectedFile ? (
            <>
              <div className="border border-border rounded-lg p-8 flex items-center justify-center mb-6 bg-muted/20">
                <div className="w-24 h-32 bg-white border border-border rounded flex items-center justify-center">
                  <span className="text-xs text-muted-foreground text-center">
                    [Thumbnail: {selectedFile.name}]
                  </span>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <p>
                  <strong>Name:</strong> {selectedFile.name}
                </p>
                <p>
                  <strong>Size:</strong> {formatFileSize(selectedFile.metadata?.size || 0)}
                </p>
                <p>
                  <strong>Modified:</strong>{" "}
                  {new Date(selectedFile.created_at).toLocaleDateString()}
                </p>
              </div>
            </>
          ) : (
            <div className="text-center text-muted-foreground py-8">
              Select a file to preview
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default VaultFiles;
