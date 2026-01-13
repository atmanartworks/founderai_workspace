import { useState, useEffect, useRef } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { ragApi } from "@/services/ragApi";
import { Button } from "@/components/ui/button";
import { ChevronLeft, FileText, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

interface Chunk {
  chunk_id: string;
  content: string;
  chunk_index: number;
}

export default function DocumentViewer() {
  const { documentId } = useParams<{ documentId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [documentName, setDocumentName] = useState<string>("");
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [highlightedChunkId, setHighlightedChunkId] = useState<string | null>(null);
  const [highlightedText, setHighlightedText] = useState<string | null>(null);
  
  const chunkRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
  const highlightTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!documentId) return;
    
    loadDocument();
    
    // Check for chunk_id and quoted_text in URL params
    const chunkId = searchParams.get("chunk_id");
    const quotedText = searchParams.get("quoted_text");
    
    if (chunkId) {
      setHighlightedChunkId(chunkId);
      if (quotedText) {
        setHighlightedText(decodeURIComponent(quotedText));
      }
    }
  }, [documentId, searchParams]);

  useEffect(() => {
    // Scroll to highlighted chunk after chunks are loaded
    if (highlightedChunkId && chunks.length > 0) {
      setTimeout(() => {
        scrollToChunk(highlightedChunkId);
      }, 100);
    }
  }, [highlightedChunkId, chunks]);

  const loadDocument = async () => {
    if (!documentId) return;
    
    try {
      setLoading(true);
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        navigate("/login");
        return;
      }

      const result = await ragApi.getDocumentChunks(documentId, user.id);
      setDocumentName(result.document_name);
      setChunks(result.chunks);
    } catch (error: any) {
      console.error("Error loading document:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to load document",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const scrollToChunk = (chunkId: string) => {
    const chunkElement = chunkRefs.current[`chunk-${chunkId}`];
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

    // Normalize whitespace for matching (but preserve original for display)
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
      // No match found, return content as-is
      return <span>{content}</span>;
    }

    // Find the corresponding positions in the original content
    // We need to map from normalized positions back to original
    let normalizedPos = 0;
    let originalStart = -1;
    let originalEnd = -1;
    
    for (let i = 0; i < content.length; i++) {
      const char = content[i];
      // Count non-whitespace characters in normalized string
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
        // If we're at match start but char is whitespace, include it
        originalStart = i;
      }
    }
    
    // Fallback: if we couldn't find exact positions, use approximate
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

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading document...</p>
        </div>
      </div>
    );
  }

  if (chunks.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="mb-4"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div className="glass-card p-8 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-2xl font-semibold mb-2">{documentName || "Document"}</h2>
            <p className="text-muted-foreground">
              This document has not been processed yet. Please embed it first.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-6 flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="shrink-0"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-semibold text-foreground/90 truncate">
              {documentName}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {chunks.length} {chunks.length === 1 ? "chunk" : "chunks"}
            </p>
          </div>
        </div>

        {/* Chunks */}
        <div className="space-y-6">
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
                  "glass-card p-6 rounded-xl border transition-all duration-300",
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
      </div>
    </div>
  );
}
