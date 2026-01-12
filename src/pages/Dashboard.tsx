import { Navbar } from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRef, useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { FileText, File, Image as ImageIcon, Trash2, Eye } from "lucide-react";
import { ragApi } from "@/services/ragApi";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

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
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null);
  const [filePreviewContent, setFilePreviewContent] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<any>(null);
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
        
        // Count files from DB (exclude folders)
        const { data: allFiles } = await supabase
          .from("vault_files")
          .select("file_size, is_folder")
          .eq("user_id", user.id)
          .eq("is_folder", false);
        
        if (allFiles) {
          setFileCount(allFiles.length);
          const totalBytesDB = allFiles.reduce((acc, file) => acc + (file.file_size || 0), 0);
          setStorageUsed(totalBytesDB);
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

      toast({
        title: "Uploading...",
        description: "Please wait while we upload and process your file.",
      });

      // Check if filename already exists
      const { data: existingFiles } = await supabase
        .from("vault_files")
        .select("original_name")
        .eq("user_id", user.id)
        .eq("is_folder", false);

      // Generate unique filename if duplicate
      let finalFileName = file.name;
      if (existingFiles) {
        const existingNames = existingFiles.map(f => f.original_name);
        
        if (existingNames.includes(finalFileName)) {
          const fileNameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.'));
          const fileExt = file.name.substring(file.name.lastIndexOf('.'));
          
          let counter = 1;
          while (existingNames.includes(finalFileName)) {
            finalFileName = `${fileNameWithoutExt} duplicate ${counter}${fileExt}`;
            counter++;
          }
        }
      }

      const fileExt = finalFileName.split(".").pop();
      const randomFileName = `${Math.random()}.${fileExt}`;
      const filePath = `${user.id}/${randomFileName}`;

      console.log('Uploading file:', finalFileName, 'to path:', filePath);

      // Upload to storage (using 'vault' bucket to match backend)
      const { error: uploadError, data: uploadData } = await supabase.storage
        .from("vault")
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false,
          contentType: file.type,
        });

      if (uploadError) {
        console.error('Upload error:', uploadError);
        throw new Error(`Upload failed: ${uploadError.message}`);
      }
      
      console.log('Upload successful:', uploadData);

      // Save metadata to database with the final (possibly renamed) filename
      const { data: insertedData, error: dbError } = await supabase
        .from("vault_files")
        .insert({
          user_id: user.id,
          storage_path: filePath,
          original_name: finalFileName,  // Use the renamed filename
          file_size: file.size,
          content_type: file.type,
          is_folder: false,
          parent_folder_id: currentFolderId,
        })
        .select();

      if (dbError) throw dbError;

      const vaultId = insertedData?.[0]?.id;

      // Check if file should be embedded (text-based files)
      const embeddableExtensions = ['txt', 'pdf', 'docx', 'md', 'html', 'json'];
      if (vaultId && embeddableExtensions.includes(fileExt?.toLowerCase() || '')) {
        toast({
          title: "Processing...",
          description: "Extracting text and creating embeddings.",
        });

        // Small delay to ensure storage upload is complete
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Call embedding API using ragApi service
        try {
          const result = await ragApi.embedDocument(vaultId);
          console.log('Embedding result:', result);
          
          const uploadMsg = finalFileName !== file.name 
            ? `File renamed to "${finalFileName}" and processed! Created ${result.chunks || 0} chunks.`
            : `File processed! Created ${result.chunks || 0} chunks.`;
            
          toast({
            title: "Success!",
            description: uploadMsg,
          });
        } catch (embedError: any) {
          console.error('Error calling embedding API:', embedError);
          toast({
            title: "Warning",
            description: `File uploaded but embedding failed: ${embedError.message}`,
            variant: "destructive",
          });
        }
      } else {
        const uploadMsg = finalFileName !== file.name 
          ? `File renamed to "${finalFileName}" and uploaded successfully!`
          : "File uploaded successfully!";
          
        toast({
          title: "Success",
          description: uploadMsg,
        });
      }

      fetchFiles();
    } catch (error: any) {
      console.error("Error uploading file:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to upload file",
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

  const handleItemClick = async (item: any) => {
    if (item.is_folder) {
      setCurrentFolderId(item.id);
      setSelectedFile(null);
      setFilePreviewUrl(null);
      setFilePreviewContent(null);
    } else {
      setSelectedFile(item);
      await loadFilePreview(item);
    }
  };

  const loadFilePreview = async (file: any) => {
    setPreviewLoading(true);
    setFilePreviewUrl(null);
    setFilePreviewContent(null);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Get file extension
      const ext = file.original_name.split('.').pop()?.toLowerCase();
      
      console.log('Loading preview for:', file.original_name, 'Extension:', ext);
      console.log('File data:', file);
      
      // For images, try to get signed URL first, then public URL
      if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext || '')) {
        // Try signed URL first (works with private buckets)
        const { data: signedData, error: signedError } = await supabase.storage
          .from('vault')
          .createSignedUrl(file.storage_path, 3600); // 1 hour expiry
        
        if (!signedError && signedData?.signedUrl) {
          console.log('Using signed URL for image');
          setFilePreviewUrl(signedData.signedUrl);
        } else {
          // Fallback to public URL
          const { data } = supabase.storage
            .from('vault')
            .getPublicUrl(file.storage_path);
          
          if (data?.publicUrl) {
            console.log('Using public URL for image');
            setFilePreviewUrl(data.publicUrl);
          }
        }
      }
      // For text files, download and show content
      else if (['txt', 'md', 'json', 'csv', 'log'].includes(ext || '')) {
        const { data, error } = await supabase.storage
          .from('vault')
          .download(file.storage_path);

        if (!error && data) {
          const text = await data.text();
          console.log('Loaded text content, length:', text.length);
          setFilePreviewContent(text);
        } else {
          console.error('Error downloading text file:', error);
        }
      }
      // For Word/PDF files, check if text_content exists in database
      else if (['doc', 'docx', 'pdf'].includes(ext || '')) {
        if (file.text_content && file.text_content.trim().length > 0) {
          console.log('Using text_content from database, length:', file.text_content.length);
          setFilePreviewContent(file.text_content.substring(0, 10000)); // Show first 10000 chars
        } else {
          console.log('No text_content available for document. File may need to be processed.');
          // Try to download and extract text directly
          try {
            const { data, error } = await supabase.storage
              .from('vault')
              .download(file.storage_path);

            if (!error && data) {
              console.log('Downloaded document, attempting text extraction preview');
              // For simple preview, we won't do full extraction here
              // Just show a message that processing is needed
            }
          } catch (err) {
            console.error('Could not download document:', err);
          }
        }
      }
      // For other files, try to get the stored text_content
      else if (file.text_content) {
        console.log('Using text_content from database (other file type)');
        setFilePreviewContent(file.text_content.substring(0, 5000));
      }
    } catch (error) {
      console.error('Error loading preview:', error);
    } finally {
      setPreviewLoading(false);
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

  const handleDeleteFile = async () => {
    if (!fileToDelete) return;

    try {
      // Delete from backend (handles storage, FAISS, and database)
      await ragApi.deleteFile(fileToDelete.id);
      
      toast({
        title: "Success",
        description: `File "${fileToDelete.original_name}" deleted successfully`,
      });

      // Clear selection if deleted file was selected
      if (selectedFile?.id === fileToDelete.id) {
        setSelectedFile(null);
        setFilePreviewUrl(null);
        setFilePreviewContent(null);
      }

      // Refresh file list
      fetchFiles();
      setDeleteDialogOpen(false);
      setFileToDelete(null);
    } catch (error: any) {
      console.error("Error deleting file:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to delete file",
        variant: "destructive",
      });
    }
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
                {formatFileSize(storageUsed)} used of {totalGB} GB
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
                  className={`flex items-center gap-2 group px-2 py-1.5 rounded cursor-pointer ${
                    selectedFile?.id === file.id ? "bg-primary/10 text-primary" : "hover:bg-muted"
                  }`}
                >
                  <div
                    className="flex items-center flex-1 min-w-0"
                    onClick={() => handleItemClick(file)}
                    onDoubleClick={() => handleItemDoubleClick(file)}
                  >
                    <span className="mr-2 shrink-0">{file.is_folder ? "📁" : "📄"}</span>
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
                      <span className="truncate flex-1">{file.original_name}</span>
                    )}
                  </div>
                  {!file.is_folder && (
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleItemClick(file);
                        }}
                        title="Preview"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive hover:text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFileToDelete(file);
                          setDeleteDialogOpen(true);
                        }}
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
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
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">
              Preview: {selectedFile?.original_name || "No file selected"}
            </h2>
            {selectedFile && !selectedFile.is_folder && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  setFileToDelete(selectedFile);
                  setDeleteDialogOpen(true);
                }}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            )}
          </div>

          {selectedFile ? (
            <>
              {/* Preview Area */}
              <div className="border border-border rounded-lg mb-6 bg-muted/20 overflow-hidden min-h-[400px]">
                {previewLoading ? (
                  <div className="p-8 text-center text-muted-foreground">
                    Loading preview...
                  </div>
                ) : filePreviewUrl ? (
                  // Image preview
                  <div className="p-4 flex items-center justify-center bg-white min-h-[400px]">
                    <img 
                      src={filePreviewUrl} 
                      alt={selectedFile.original_name}
                      className="max-w-full max-h-[500px] object-contain rounded"
                    />
                  </div>
                ) : filePreviewContent ? (
                  // Text content preview
                  <div className="p-4 max-h-[500px] overflow-y-auto">
                    <pre className="text-sm font-mono whitespace-pre-wrap break-words text-foreground">
                      {filePreviewContent}
                    </pre>
                  </div>
                ) : (
                  // Default icon preview
                  <div className="p-8 flex flex-col items-center justify-center gap-3 min-h-[400px]">
                    {selectedFile.original_name.match(/\.(pdf)$/i) ? (
                      <>
                        <File className="w-16 h-16 text-red-500" />
                        <p className="text-sm text-muted-foreground text-center max-w-md">
                          PDF preview not available.<br/>
                          {selectedFile.text_content ? (
                            <span className="text-xs mt-2 block">
                              Text content is available. Click "Show Text" to view extracted text.
                            </span>
                          ) : (
                            <span className="text-xs mt-2 block">
                              Process this file through embeddings to extract text.
                            </span>
                          )}
                        </p>
                        {selectedFile.text_content && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setFilePreviewContent(selectedFile.text_content.substring(0, 50000));
                            }}
                          >
                            Show Extracted Text
                          </Button>
                        )}
                      </>
                    ) : selectedFile.original_name.match(/\.(doc|docx)$/i) ? (
                      <>
                        <FileText className="w-16 h-16 text-blue-500" />
                        <p className="text-sm text-muted-foreground text-center max-w-md">
                          Document preview not available.<br/>
                          {selectedFile.text_content ? (
                            <span className="text-xs mt-2 block">
                              Text content is available. Click "Show Text" to view extracted text.
                            </span>
                          ) : (
                            <span className="text-xs mt-2 block">
                              Process this file through embeddings to extract text.
                            </span>
                          )}
                        </p>
                        {selectedFile.text_content && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setFilePreviewContent(selectedFile.text_content.substring(0, 50000));
                            }}
                          >
                            Show Extracted Text
                          </Button>
                        )}
                      </>
                    ) : (
                      <>
                        <File className="w-16 h-16 text-muted-foreground" />
                        <p className="text-sm text-muted-foreground">
                          Preview not available for this file type
                        </p>
                        {selectedFile.text_content && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setFilePreviewContent(selectedFile.text_content.substring(0, 50000));
                            }}
                          >
                            Show Text Content
                          </Button>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>

              {/* File Info */}
              <div className="space-y-2 text-sm border-t pt-4">
                <p>
                  <strong>Name:</strong> {selectedFile.original_name}
                </p>
                <p>
                  <strong>Size:</strong> {formatFileSize(selectedFile.file_size || 0)}
                </p>
                <p>
                  <strong>Type:</strong> {selectedFile.content_type || "Unknown"}
                </p>
                <p>
                  <strong>Uploaded:</strong>{" "}
                  {new Date(selectedFile.created_at).toLocaleDateString()} at{" "}
                  {new Date(selectedFile.created_at).toLocaleTimeString()}
                </p>
                {selectedFile.text_content && (
                  <p className="text-xs text-muted-foreground">
                    <strong>Text Content:</strong> {formatFileSize(selectedFile.text_content.length)} extracted
                  </p>
                )}
              </div>
            </>
          ) : (
            <div className="text-center text-muted-foreground py-8">
              Select a file to preview
            </div>
          )}
        </Card>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete File</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Are you sure you want to delete "{fileToDelete?.original_name}"? This action cannot be undone.
            <br />
            <span className="text-xs text-destructive mt-2 block">
              This will also delete all embeddings and chunks associated with this file.
            </span>
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteFile}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default VaultFiles;
