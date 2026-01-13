import { Bot, User, FileText, Download, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { ScrollArea } from "./ui/scroll-area";

export interface CitationMetadata {
  citation_id: number;
  source_document_id: string;
  source_document_name: string;
  chunk_id: string;
  quoted_text: string;
  chunk_content: string;
  score: number;
}

interface ChatBubbleProps {
  message: string;
  isAI: boolean;
  timestamp?: string;
  fileUrls?: string[];
  citations?: CitationMetadata[];
}

export const ChatBubble = ({ message, isAI, timestamp, fileUrls, citations = [] }: ChatBubbleProps) => {
  const navigate = useNavigate();
  const [selectedCitation, setSelectedCitation] = useState<CitationMetadata | null>(null);
  const [citationDialogOpen, setCitationDialogOpen] = useState(false);

  // Parse file data if it exists
  const files = fileUrls?.map(url => {
    try {
      return JSON.parse(url);
    } catch {
      return { url, name: "File" };
    }
  }) || [];

  const isImage = (filename: string) => {
    return /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(filename);
  };

  // Parse citations from message text (format: [1], [2], etc.)
  const parseCitations = (text: string) => {
    const citationRegex = /\[(\d+)\]/g;
    const matches = Array.from(text.matchAll(citationRegex));
    return matches.map(match => ({
      index: match.index!,
      length: match[0].length,
      citationId: parseInt(match[1])
    }));
  };

  // Render message with clickable citations
  const renderMessageWithCitations = (text: string) => {
    if (!isAI || citations.length === 0) {
      return <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground/95">{text}</p>;
    }

    const citationMarkers = parseCitations(text);
    if (citationMarkers.length === 0) {
      return <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground/95">{text}</p>;
    }

    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    citationMarkers.forEach((marker, idx) => {
      // Add text before citation
      if (marker.index > lastIndex) {
        elements.push(
          <span key={`text-${idx}`}>
            {text.substring(lastIndex, marker.index)}
          </span>
        );
      }

      // Add clickable citation
      const citation = citations.find(c => c.citation_id === marker.citationId);
      if (citation) {
        elements.push(
          <button
            key={`citation-${idx}`}
            onClick={(e) => {
              e.preventDefault();
              // Navigate to document viewer with chunk_id and quoted_text
              const params = new URLSearchParams({
                chunk_id: citation.chunk_id,
                quoted_text: encodeURIComponent(citation.quoted_text),
              });
              navigate(`/document/${citation.source_document_id}?${params.toString()}`);
            }}
            className="inline-flex items-center justify-center min-w-[1.75rem] h-6 px-1.5 mx-0.5 text-xs font-semibold text-primary bg-primary/15 hover:bg-primary/25 border border-primary/40 rounded-md transition-all cursor-pointer hover:scale-110 hover:shadow-sm hover:shadow-primary/20 active:scale-95"
            title={`View source: ${citation.source_document_name} (Chunk ${citation.chunk_id})`}
          >
            [{marker.citationId}]
          </button>
        );
      } else {
        // Citation not found, render as plain text
        elements.push(
          <span key={`citation-${idx}`} className="text-primary/70 font-medium">
            {text.substring(marker.index, marker.index + marker.length)}
          </span>
        );
      }

      lastIndex = marker.index + marker.length;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      elements.push(
        <span key="text-end">
          {text.substring(lastIndex)}
        </span>
      );
    }

    return (
      <div className="text-sm leading-relaxed whitespace-pre-wrap text-foreground/95">
        {elements}
      </div>
    );
  };

  return (
    <div className={cn("flex gap-4 mb-6 animate-fade-in", isAI ? "flex-row" : "flex-row-reverse")}>
      <div className={cn(
        "flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-smooth",
        isAI 
          ? "bg-card/60 backdrop-blur-sm text-primary border border-border/30 shadow-sm" 
          : "bg-accent/60 backdrop-blur-sm text-foreground border border-border/30 shadow-sm"
      )}>
        {isAI ? <Bot className="w-4.5 h-4.5" /> : <User className="w-4.5 h-4.5" />}
      </div>
      
      <div className={cn("flex-1 max-w-[80%] md:max-w-[70%]", !isAI && "flex flex-col items-end")}>
        <div className={cn(
          "rounded-2xl px-5 py-3.5 transition-smooth glass-card highlight-top",
          isAI 
            ? "bg-card/80 text-card-foreground border-border/40" 
            : "bg-accent/70 text-accent-foreground border-border/40"
        )}>
          {renderMessageWithCitations(message)}
          
          {/* Display attached files */}
          {files.length > 0 && (
            <div className="mt-3 space-y-2">
              {files.map((file: any, index: number) => (
                isImage(file.name) ? (
                  <div key={index} className="space-y-2">
                    <img
                      src={file.url}
                      alt={file.name}
                      className="rounded-lg max-w-full h-auto max-h-96 object-contain border border-border/30 shadow-sm"
                    />
                    <a
                      href={file.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={cn(
                        "flex items-center gap-2 p-2.5 rounded-lg transition-all group text-xs glass hover:bg-accent/30",
                        isAI ? "bg-muted/30" : "bg-accent/40"
                      )}
                    >
                      <FileText className={cn("w-3.5 h-3.5", isAI ? "text-primary" : "text-foreground")} />
                      <span className="flex-1 truncate text-foreground/90">{file.name}</span>
                      <Download className="w-3.5 h-3.5 opacity-0 group-hover:opacity-70 transition-opacity text-muted-foreground" />
                    </a>
                  </div>
                ) : (
                  <a
                    key={index}
                    href={file.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={cn(
                      "flex items-center gap-2.5 p-2.5 rounded-lg transition-all group glass hover:bg-accent/30",
                      isAI ? "bg-muted/30" : "bg-accent/40"
                    )}
                  >
                    <FileText className={cn("w-4 h-4", isAI ? "text-primary" : "text-foreground")} />
                    <span className="text-sm flex-1 truncate text-foreground/90">{file.name}</span>
                    <Download className="w-4 h-4 opacity-0 group-hover:opacity-70 transition-opacity text-muted-foreground" />
                  </a>
                )
              ))}
            </div>
          )}
        </div>
        {timestamp && (
          <span className="text-xs text-muted-foreground/70 mt-2 px-2 block">{timestamp}</span>
        )}
      </div>

      {/* Citation Dialog */}
      <Dialog open={citationDialogOpen} onOpenChange={setCitationDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[85vh] glass-card border-border/40 p-0 overflow-hidden">
          <DialogHeader className="px-6 pt-6 pb-4 border-b border-border/30">
            <DialogTitle className="flex items-center gap-3 text-foreground/95">
              <div className="p-2 rounded-lg bg-primary/15 border border-primary/30 shadow-sm">
                <ExternalLink className="w-5 h-5 text-primary" />
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-semibold">Citation {selectedCitation?.citation_id}</span>
                {selectedCitation && (
                  <span className="text-xs text-muted-foreground/70 font-normal mt-0.5">
                    {selectedCitation.source_document_name}
                  </span>
                )}
              </div>
            </DialogTitle>
          </DialogHeader>
          {selectedCitation && (
            <ScrollArea className="max-h-[calc(85vh-120px)] px-6 py-4">
              <div className="space-y-5">
                {/* Metadata Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="glass-card p-4 border border-border/30 rounded-lg highlight-top">
                    <h4 className="text-xs font-semibold text-muted-foreground/80 uppercase tracking-wide mb-2">Chunk ID</h4>
                    <p className="text-base text-foreground/90 font-medium">{selectedCitation.chunk_id}</p>
                  </div>
                  <div className="glass-card p-4 border border-border/30 rounded-lg highlight-top">
                    <h4 className="text-xs font-semibold text-muted-foreground/80 uppercase tracking-wide mb-2">Relevance Score</h4>
                    <p className="text-base text-foreground/90 font-medium">{selectedCitation.score.toFixed(3)}</p>
                  </div>
                </div>

                {/* Quoted Text */}
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground/80 uppercase tracking-wide mb-3">Quoted Text</h4>
                  <div className="glass-card border border-border/30 rounded-lg p-5 highlight-top bg-card/50">
                    <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
                      {selectedCitation.quoted_text}
                    </p>
                  </div>
                </div>

                {/* Full Chunk Content */}
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground/80 uppercase tracking-wide mb-3">Full Chunk Content</h4>
                  <div className="glass-card border border-border/30 rounded-lg p-5 max-h-80 overflow-y-auto highlight-top bg-card/40">
                    <p className="text-sm text-foreground/85 leading-relaxed whitespace-pre-wrap">
                      {selectedCitation.chunk_content}
                    </p>
                  </div>
                </div>

                {/* Footer */}
                <div className="text-xs text-muted-foreground/60 pt-3 border-t border-border/30">
                  <span className="font-mono">Document ID: {selectedCitation.source_document_id}</span>
                </div>
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};
