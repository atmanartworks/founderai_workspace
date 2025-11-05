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
  const [searchQuery, setSearchQuery] = useState("");
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch files from database
  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      let query = supabase
        .from("vault_files")
        .select("*")
        .eq("user_id", user.id);

      // Filter by current folder
      if (currentFolderId) {
        query = query.eq("parent_folder_id", currentFolderId);
      } else {
        query = query.is("parent_folder_id", null);
      }

      const { data, error } = await query.order("is_folder", { ascending: false }).order("created_at", { ascending: false });

      if (error) throw error;

      if (data) {
        setFiles(data);
        
        // Calculate total storage used (only files, not folders)
        const { data: allFiles } = await supabase
          .from("vault_files")
          .select("file_size")
          .eq("user_id", user.id)
          .eq("is_folder", false);
        
        if (allFiles) {
          setFileCount(allFiles.length);
          const totalBytes = allFiles.reduce((acc, file) => acc + (file.file_size || 0), 0);
          setStorageUsed(totalBytes);
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

      // Upload to storage
      const { error: uploadError } = await supabase.storage
        .from("chat-files")
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false,
          contentType: file.type,
        });

      if (uploadError) throw uploadError;

      // Save metadata to database
      const { error: dbError } = await supabase
        .from("vault_files")
        .insert({
          user_id: user.id,
          storage_path: filePath,
          original_name: file.name,
          file_size: file.size,
          content_type: file.type,
          is_folder: false,
          parent_folder_id: currentFolderId,
        });

      if (dbError) throw dbError;

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

  const handleCreateFolder = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const folderName = "New Folder";

      const { error } = await supabase
        .from("vault_files")
        .insert({
          user_id: user.id,
          storage_path: "",
          original_name: folderName,
          is_folder: true,
          parent_folder_id: currentFolderId,
        });

      if (error) throw error;

      toast({
        title: "Success",
        description: "Folder created successfully!",
      });

      fetchFiles();
    } catch (error) {
      console.error("Error creating folder:", error);
      toast({
        title: "Error",
        description: "Failed to create folder",
        variant: "destructive",
      });
    }
  };

  const handleRename = async (itemId: string, newName: string) => {
    try {
      const { error } = await supabase
        .from("vault_files")
        .update({ original_name: newName })
        .eq("id", itemId);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Renamed successfully!",
      });

      fetchFiles();
      setEditingItemId(null);
    } catch (error) {
      console.error("Error renaming:", error);
      toast({
        title: "Error",
        description: "Failed to rename",
        variant: "destructive",
      });
    }
  };

  const handleItemClick = (item: any) => {
    if (item.is_folder) {
      setCurrentFolderId(item.id);
      setSelectedFile(null);
    } else {
      setSelectedFile(item);
    }
  };

  const handleItemDoubleClick = (item: any) => {
    setEditingItemId(item.id);
    setEditingName(item.original_name);
  };

  const goBackToParent = async () => {
    if (!currentFolderId) return;

    try {
      const { data } = await supabase
        .from("vault_files")
        .select("parent_folder_id")
        .eq("id", currentFolderId)
        .single();

      if (data) {
        setCurrentFolderId(data.parent_folder_id);
      }
    } catch (error) {
      console.error("Error navigating back:", error);
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

  const storageLimit = 1024 * 1024 * 1024; // 1 GB limit
  const usedGB = (storageUsed / (1024 * 1024 * 1024)).toFixed(2);
  const totalGB = (storageLimit / (1024 * 1024 * 1024)).toFixed(0);
  const percentUsed = (storageUsed / storageLimit) * 100;

  const filteredFiles = files.filter(file => {
    return file.original_name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  useEffect(() => {
    fetchFiles();
  }, [currentFolderId]);

  return (
    <div className="min-h-screen bg-background p-8">
      <Navbar />
      <h1 className="text-3xl font-bold mb-6">File Explorer</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - File Explorer */}
        <Card className="p-6">
          <div className="mb-4 space-y-3">
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
                {usedGB} GB used of {totalGB} GB
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 mb-4">
            <input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="border border-border rounded-md px-2 py-1 text-sm w-full bg-background text-foreground"
            />
          </div>

          <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
            <div className="flex items-center space-x-2">
              {currentFolderId && (
                <button onClick={goBackToParent} className="hover:text-foreground">
                  ← Back
                </button>
              )}
              <span>/ MyVault /</span>
            </div>
          </div>

          <div className="space-y-1 border border-border rounded-md p-2 h-72 overflow-y-auto">
            {loading ? (
              <p className="text-sm text-muted-foreground text-center py-4">Loading files...</p>
            ) : filteredFiles.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                {searchQuery ? "No files found" : "No files uploaded yet"}
              </p>
            ) : (
              filteredFiles.map((file) => (
                <div
                  key={file.id}
                  onClick={() => handleItemClick(file)}
                  onDoubleClick={() => handleItemDoubleClick(file)}
                  className={`flex items-center px-2 py-1 rounded cursor-pointer ${
                    selectedFile?.id === file.id ? "bg-primary/10 text-primary" : "hover:bg-muted"
                  }`}
                >
                  <span className="mr-2">{file.is_folder ? "📁" : "📄"}</span>
                  {editingItemId === file.id ? (
                    <input
                      type="text"
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      onBlur={() => handleRename(file.id, editingName)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleRename(file.id, editingName);
                        if (e.key === "Escape") setEditingItemId(null);
                      }}
                      autoFocus
                      className="flex-1 bg-background border border-border rounded px-1 text-sm"
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <span>{file.original_name}</span>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Hidden file input */}
          <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileChange} />

          <div className="flex justify-center gap-2 mt-4">
            <Button onClick={handleCreateFolder} variant="outline">New Folder</Button>
            <Button onClick={handleUploadClick}>Upload</Button>
          </div>
        </Card>

        {/* Right Panel - Preview */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">
            Preview: {selectedFile?.original_name || "No file selected"}
          </h2>

          {selectedFile ? (
            <>
              <div className="border border-border rounded-lg p-8 flex items-center justify-center mb-6 bg-muted/20">
                <div className="w-24 h-32 bg-white border border-border rounded flex items-center justify-center">
                  <span className="text-xs text-muted-foreground text-center">
                    [Thumbnail: {selectedFile.original_name}]
                  </span>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <p>
                  <strong>Name:</strong> {selectedFile.original_name}
                </p>
                <p>
                  <strong>Size:</strong> {formatFileSize(selectedFile.file_size || 0)}
                </p>
                <p>
                  <strong>Uploaded:</strong>{" "}
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
