// RAG Backend API Service
const RAG_API_URL = import.meta.env.VITE_RAG_API_URL || "http://127.0.0.1:8000";

export interface ChatRequest {
  conversation_id: string | null;
  message: string;
  user_id: string;
  top_k?: number;
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

export const ragApi = {
  // Send chat message with RAG
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
    const response = await fetch(`${RAG_API_URL}/api/embeddings/embed-document/${vaultId}`, {
      method: "POST",
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to embed document");
    }

    return response.json();
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

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${RAG_API_URL}/health`);
    return response.json();
  },
};

