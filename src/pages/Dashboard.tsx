import { Navbar } from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRef, useState } from "react";

const VaultFiles = () => {
  const [selectedFile, setSelectedFile] = useState({
    name: "file1.pdf",
    size: "120 KB",
    pages: 5,
    modified: "2025-10-30",
  });

  const files = [
    "file1.pdf",
    "file2.pdf",
    "file3.pdf",
    "file4.pdf",
    "file5.pdf",
    "file6.pdf",
    "file7.pdf",
    "file8.pdf",
    "file9.pdf",
  ];

  // 👇 reference to hidden input element
  const fileInputRef = useRef(null);

  // 📁 Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const newFile = {
        name: file.name,
        size: `${(file.size / 1024).toFixed(2)} KB`,
        pages: Math.floor(Math.random() * 10) + 1, // dummy pages for preview
        modified: new Date().toISOString().split("T")[0],
      };
      setSelectedFile(newFile);
    }
  };

  // 🚀 Open system file manager
  const handleUploadClick = () => {
    fileInputRef.current.click();
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
            {files.map((file, index) => (
              <div
                key={index}
                onClick={() =>
                  setSelectedFile({
                    name: file,
                    size: "000 KB",
                    pages: 0,
                    modified: "0000-00-00",
                  })
                }
                className={`flex items-center px-2 py-1 rounded cursor-pointer ${
                  selectedFile.name === file ? "bg-primary/10 text-primary" : "hover:bg-muted"
                }`}
              >
                <span className="mr-2">📄</span> {file}
              </div>
            ))}
          </div>

          {/* Hidden file input */}
          <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileChange} />

          <div className="flex justify-center mt-4">
            <Button onClick={handleUploadClick}>Upload</Button>
          </div>
        </Card>

        {/* Right Panel - Preview */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Preview: {selectedFile.name}</h2>

          <div className="border border-border rounded-lg p-8 flex items-center justify-center mb-6 bg-muted/20">
            <div className="w-24 h-32 bg-white border border-border rounded flex items-center justify-center">
              <span className="text-xs text-muted-foreground text-center">[Thumbnail: {selectedFile.name}]</span>
            </div>
          </div>

          <div className="space-y-2 text-sm">
            <p>
              <strong>Name:</strong> {selectedFile.name}
            </p>
            <p>
              <strong>Size:</strong> {selectedFile.size}
            </p>
            <p>
              <strong>Pages:</strong> {selectedFile.pages}
            </p>
            <p>
              <strong>Modified:</strong> {selectedFile.modified}
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default VaultFiles;
