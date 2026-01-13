import { useState, useEffect, useRef } from "react";
import { X, FileText, Loader2 } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "./ui/sheet";
import { ScrollArea } from "./ui/scroll-area";
import { cn } from "@/lib/utils";
import { ragApi } from "@/services/ragApi";
import { supabase } from "@/integrations/supabase/client";

interface Chunk {
  chunk_id: string;
  content: string;
  chunk_index: number;
}

interface DocumentViewerPanelProps {
  documentId: string | null;
  chunkId: string | null;
  quotedText: string | null;
  onClose: () => void;
}

export function DocumentViewerPanel({
  documentId,
  chunkId,
  quotedText,
  onClose,
}: DocumentViewerPanelProps) {
  const [documentName, setDocumentName] = useState<string>("");
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState(false);
  const [highlightedChunkId, setHighlightedChunkId] = useState<string | null>(chunkId);
  const [highlightedText, setHighlightedText] = useState<string | null>(quotedText);
  
  const chunkRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
  const highlightTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (documentId) {
      loadDocument();
    }
  }, [documentId]);

  useEffect(() => {
    // Update highlight when props change
    if (chunkId) {
      setHighlightedChunkId(chunkId);
      if (quotedText) {
        setHighlightedText(decodeURIComponent(quotedText));
      }
    }
  }, [chunkId, quotedText]);

  useEffect(() => {
    // Scroll to highlighted chunk after chunks are loaded
    if (highlightedChunkId && chunks.length > 0) {
      setTimeout(() => {
        scrollToChunk(highlightedChunkId);
      }, 200);
    }
  }, [highlightedChunkId, chunks]);

  const loadDocument = async () => {
    if (!documentId) return;
    
    try {
      setLoading(true);
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const result = await ragApi.getDocumentChunks(documentId, user.id);
      setDocumentName(result.document_name);
      setChunks(result.chunks);
    } catch (error: any) {
      console.error("Error loading document:", error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToChunk = (targetChunkId: string) => {
    const chunkElement = chunkRefs.current[`chunk-${targetChunkId}`];
    if (chunkElement) {
      chunkElement.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      
      // Clear any existing highlight timeout
      if (highlightTimeoutRef.current) {
        clearTimeout(highlightTimeoutRef.current);
      }
      
      // Remove highlight after 5 seconds
      highlightTimeoutRef.current = setTimeout(() => {
        setHighlightedChunkId(null);
        setHighlightedText(null);
      }, 5000);
    }
  };

  const highlightTextInChunk = (content: string, quotedText: string | null): React.ReactNode => {
    if (!quotedText || !quotedText.trim()) {
      return <span>{content}</span>;
    }

    // Normalize whitespace for matching
    const normalizeText = (text: string) => text.replace(/\s+/g, ' ').trim().toLowerCase();
    const normalizedQuoted = normalizeText(quotedText);
    const normalizedContent = normalizeText(content);
    
    // Try exact match first
    let matchIndex = normalizedContent.indexOf(normalizedQuoted);
    let matchLength = normalizedQuoted.length;
    
    // If no exact match, try partial match (first 30-50 chars)
    if (matchIndex === -1 && normalizedQuoted.length > 30) {
      const partialLength = Math.min(50, Math.max(30, normalizedQuoted.length));
      const partialQuoted = normalizedQuoted.substring(0, partialLength);
      matchIndex = normalizedContent.indexOf(partialQuoted);
      matchLength = partialLength;
    }
    
    if (matchIndex === -1) {
      return <span>{content}</span>;
    }

    // Find corresponding positions in original content
    let normalizedPos = 0;
    let originalStart = -1;
    let originalEnd = -1;
    
    for (let i = 0; i < content.length; i++) {
      const char = content[i];
      if (/\S/.test(char)) {
        if (normalizedPos === matchIndex && originalStart === -1) {
          originalStart = i;
        }
        if (normalizedPos === matchIndex + matchLength - 1) {
          originalEnd = i + 1;
          break;
        }
        normalizedPos++;
      } else if (normalizedPos === matchIndex && originalStart === -1) {
        originalStart = i;
      }
    }
    
    if (originalStart === -1) originalStart = 0;
    if (originalEnd === -1) originalEnd = Math.min(content.length, originalStart + quotedText.length);
    
    return (
      <>
        <span>{content.substring(0, originalStart)}</span>
        <mark className="bg-primary/40 text-primary-foreground px-1 py-0.5 rounded-md transition-all shadow-sm shadow-primary/20">
          {content.substring(originalStart, originalEnd)}
        </mark>
        <span>{content.substring(originalEnd)}</span>
      </>
    );
  };

  if (!documentId) {
    return null;
  }

  if (!documentId) {
    return null;
  }

  return (
    <Sheet open={!!documentId} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:max-w-2xl p-0 flex flex-col glass-card border-border/40 overflow-hidden h-full">
        <SheetHeader className="px-6 pt-6 pb-4 border-b border-border/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <div className="p-2 rounded-lg bg-primary/15 border border-primary/30">
                <FileText className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <SheetTitle className="text-lg font-semibold text-foreground/90 truncate">
                  {documentName || "Document"}
                </SheetTitle>
                {chunks.length > 0 && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {chunks.length} {chunks.length === 1 ? "chunk" : "chunks"}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-accent/50 transition-colors"
            >
              <X className="w-5 h-5 text-muted-foreground" />
            </button>
          </div>
        </SheetHeader>

        <ScrollArea className="flex-1 px-6 py-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
              <p className="text-sm text-muted-foreground">Loading document...</p>
            </div>
          ) : chunks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="w-16 h-16 text-muted-foreground/50 mb-4" />
              <p className="text-sm text-muted-foreground">
                This document has not been processed yet.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {chunks.map((chunk) => {
                const isHighlighted = highlightedChunkId === chunk.chunk_id;
                
                return (
                  <div
                    key={chunk.chunk_id}
                    id={`chunk-${chunk.chunk_id}`}
                    ref={(el) => {
                      chunkRefs.current[`chunk-${chunk.chunk_id}`] = el;
                    }}
                    className={cn(
                      "glass-card p-5 rounded-xl border transition-all duration-300",
                      isHighlighted
                        ? "border-primary/50 bg-primary/5 shadow-lg shadow-primary/10"
                        : "border-border/30 bg-card/80"
                    )}
                  >
                    <div className="flex items-start gap-3 mb-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                        <span className="text-xs font-semibold text-primary">
                          {chunk.chunk_index + 1}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-muted-foreground font-mono">
                          Chunk ID: {chunk.chunk_id}
                        </p>
                      </div>
                    </div>
                    <div className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap">
                      {isHighlighted && highlightedText
                        ? highlightTextInChunk(chunk.content, highlightedText)
                        : chunk.content
                      }
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
