// RAG Backend API Service
const RAG_API_URL = import.meta.env.VITE_RAG_API_URL || "http://127.0.0.1:8000";

export interface ChatRequest {
  conversation_id: string | null;
  message: string;
  user_id: string;
  top_k?: number;
  active_document_id?: string | null;  // Conversation-level active document context
}

export interface CitationMetadata {
  citation_id: number;
  source_document_id: string;
  source_document_name: string;
  chunk_id: string;
  quoted_text: string;
  chunk_content: string;
  score: number;
}

export interface ChatResponse {
  response: string;
  sources: string[];
  message_id: string;
  conversation_id: string;
  citations?: CitationMetadata[];
}

export interface VaultFile {
  id: string;
  user_id: string;
  storage_path: string;
  original_name: string;
  file_size: number;
  content_type: string;
  created_at: string;
}

export interface StreamChatCallbacks {
  onToken: (text: string) => void;
  onDone: (metadata: { citations?: CitationMetadata[]; source?: string; error?: string }) => void;
  onError?: (error: Error) => void;
}

export const ragApi = {
  // Send chat message with RAG (non-streaming)
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${RAG_API_URL}/api/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to send message");
    }

    return response.json();
  },

  // Stream chat message with SSE
  async streamMessage(request: ChatRequest, callbacks: StreamChatCallbacks): Promise<void> {
    try {
      const response = await fetch(`${RAG_API_URL}/api/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || JSON.stringify(error);
        } catch {
          // If JSON parsing fails, use status text
          errorMessage = response.statusText || `HTTP ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      if (!response.body) {
        throw new Error("Response body is null");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Split by double newline (SSE event separator)
        const events = buffer.split("\n\n");
        // Keep the last incomplete event in buffer
        buffer = events.pop() || "";

        for (const event of events) {
          if (!event.trim()) continue;

          // Parse SSE event
          const lines = event.split("\n");
          let eventType = "";
          let eventData = "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              eventType = line.replace("event: ", "").trim();
            } else if (line.startsWith("data: ")) {
              eventData = line.replace("data: ", "").trim();
            }
          }

          if (eventType === "token" && eventData) {
            try {
              const { text } = JSON.parse(eventData);
              if (text) {
                callbacks.onToken(text);
              }
            } catch (e) {
              console.error("Error parsing token data:", e, eventData);
            }
          } else if (eventType === "done" && eventData) {
            try {
              const metadata = JSON.parse(eventData);
              callbacks.onDone(metadata);
            } catch (e) {
              console.error("Error parsing done data:", e, eventData);
            }
          }
        }
      }

      // Process any remaining buffer
      if (buffer.trim()) {
        const lines = buffer.split("\n");
        let eventType = "";
        let eventData = "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            eventType = line.replace("event: ", "").trim();
          } else if (line.startsWith("data: ")) {
            eventData = line.replace("data: ", "").trim();
          }
        }

        if (eventType === "done" && eventData) {
          try {
            const metadata = JSON.parse(eventData);
            callbacks.onDone(metadata);
          } catch (e) {
            console.error("Error parsing final done data:", e);
          }
        }
      }
    } catch (error) {
      console.error("Stream error:", error);
      if (callbacks.onError) {
        callbacks.onError(error as Error);
      } else {
        callbacks.onDone({ error: (error as Error).message });
      }
    }
  },

  // Upload file to vault
  async uploadFile(userId: string, file: File, folder?: string): Promise<any> {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("file", file);
    if (folder) {
      formData.append("folder", folder);
    }

    const response = await fetch(`${RAG_API_URL}/api/vault/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to upload file");
    }

    return response.json();
  },

  // List vault files
  async listFiles(): Promise<{ files: VaultFile[] }> {
    const response = await fetch(`${RAG_API_URL}/api/vault/list`);

    if (!response.ok) {
      throw new Error("Failed to fetch vault files");
    }

    return response.json();
  },

  // Embed document
  async embedDocument(vaultId: string): Promise<any> {
    try {
      const response = await fetch(`${RAG_API_URL}/api/embeddings/embed-document/${vaultId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || JSON.stringify(error);
        } catch {
          errorMessage = response.statusText || `HTTP ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      return response.json();
    } catch (error: any) {
      console.error(`Error embedding document ${vaultId}:`, error);
      // Re-throw with more context
      throw new Error(`Failed to embed document: ${error.message || error.toString()}`);
    }
  },

  // Delete file from vault
  async deleteFile(vaultId: string): Promise<any> {
    const response = await fetch(`${RAG_API_URL}/api/vault/delete/${vaultId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to delete file");
    }

    return response.json();
  },

  // Get document chunks
  async getDocumentChunks(documentId: string, userId: string): Promise<{
    document_id: string;
    document_name: string;
    chunks: Array<{
      chunk_id: string;
      content: string;
      chunk_index: number;
    }>;
    has_text_content: boolean;
    chunks_from_faiss?: boolean;
    chunks_from_text?: boolean;
  }> {
    const response = await fetch(`${RAG_API_URL}/api/documents/${documentId}/chunks?user_id=${userId}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to get document chunks");
    }
    
    return response.json();
  },

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${RAG_API_URL}/health`);
    return response.json();
  },
};

