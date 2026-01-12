import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  content: string;
  is_ai: boolean;
  created_at: string;
  file_urls?: string[];
}

interface MessageInsert {
  conversation_id: string;
  content: string;
  is_ai: boolean;
}

export const useConversations = (userId: string | null) => {
  const { toast } = useToast();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  // Load all conversations
  useEffect(() => {
    if (userId) {
      loadConversations();
    }
  }, [userId]);

  const loadConversations = async () => {
    try {
      const { data, error } = await supabase
        .from("conversations")
        .select("*")
        .eq("user_id", userId)
        .order("updated_at", { ascending: false });

      if (error) throw error;
      setConversations(data || []);
    } catch (error: any) {
      console.error("Error loading conversations:", error);
      toast({
        title: "Error",
        description: "Failed to load conversations",
        variant: "destructive",
      });
    }
  };

  // Create new conversation
  const createConversation = async (title: string = "New Conversation") => {
    if (!userId) return null;

    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("conversations")
        .insert([{ user_id: userId, title }])
        .select()
        .single();

      if (error) throw error;

      // Update conversations list using functional update
      setConversations(prevConvs => [data, ...prevConvs]);
      setCurrentConversation(data);
      setMessages([]);
      
      return data;
    } catch (error: any) {
      console.error("Error creating conversation:", error);
      toast({
        title: "Error",
        description: "Failed to create conversation",
        variant: "destructive",
      });
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Load messages for a conversation
  const loadMessages = async (conversationId: string) => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("messages")
        .select("*")
        .eq("conversation_id", conversationId)
        .order("created_at", { ascending: true });

      if (error) throw error;
      setMessages(data || []);
    } catch (error: any) {
      console.error("Error loading messages:", error);
      toast({
        title: "Error",
        description: "Failed to load messages",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Add message to current conversation
  const addMessage = async (
    content: string, 
    isAI: boolean, 
    fileUrls?: string[], 
    conversationId?: string
  ) => {
    // Use provided conversationId or fall back to currentConversation
    const targetConversationId = conversationId || currentConversation?.id;
    
    if (!targetConversationId) {
      // Create a new conversation if none exists
      const conv = await createConversation();
      if (!conv) return null;
      // Use the newly created conversation
      return addMessage(content, isAI, fileUrls, conv.id);
    }

    try {
      // Create message data object
      const messageData: any = {
        conversation_id: targetConversationId,
        content,
        is_ai: isAI,
      };

      const { data, error } = await supabase
        .from("messages")
        .insert([messageData])
        .select()
        .single();

      if (error) throw error;

      // Add file URLs to the message object for display
      const messageWithFiles = { ...data, file_urls: fileUrls };
      
      // Update messages state using functional update to avoid stale closure
      setMessages(prevMessages => [...prevMessages, messageWithFiles]);
      
      // Update conversation's updated_at
      await supabase
        .from("conversations")
        .update({ updated_at: new Date().toISOString() })
        .eq("id", targetConversationId);

      // Reload conversations to update the list order
      await loadConversations();

      return messageWithFiles;
    } catch (error: any) {
      console.error("Error adding message:", error);
      toast({
        title: "Error",
        description: "Failed to send message",
        variant: "destructive",
      });
      return null;
    }
  };

  // Select a conversation
  const selectConversation = async (conversation: Conversation) => {
    setCurrentConversation(conversation);
    await loadMessages(conversation.id);
  };

  // Delete conversation
  const deleteConversation = async (conversationId: string) => {
    try {
      const { error } = await supabase
        .from("conversations")
        .delete()
        .eq("id", conversationId);

      if (error) throw error;

      setConversations(conversations.filter((c) => c.id !== conversationId));
      
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }

      toast({
        title: "Success",
        description: "Conversation deleted",
      });
    } catch (error: any) {
      console.error("Error deleting conversation:", error);
      toast({
        title: "Error",
        description: "Failed to delete conversation",
        variant: "destructive",
      });
    }
  };

  // Upload file to storage
  const uploadFile = async (file: File, conversationId: string) => {
    try {
      const fileExt = file.name.split(".").pop();
      const fileName = `${conversationId}/${Date.now()}.${fileExt}`;

      const { data, error } = await supabase.storage
        .from("chat-files")
        .upload(`${userId}/${fileName}`, file);

      if (error) throw error;

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from("chat-files")
        .getPublicUrl(`${userId}/${fileName}`);

      return { url: publicUrl, name: file.name };
    } catch (error: any) {
      console.error("Error uploading file:", error);
      toast({
        title: "Error",
        description: `Failed to upload ${file.name}`,
        variant: "destructive",
      });
      return null;
    }
  };

  // Rename conversation
  const renameConversation = async (conversationId: string, newTitle: string) => {
    try {
      const { error } = await supabase
        .from("conversations")
        .update({ title: newTitle })
        .eq("id", conversationId);

      if (error) throw error;

      setConversations(
        conversations.map((c) =>
          c.id === conversationId ? { ...c, title: newTitle } : c
        )
      );

      if (currentConversation?.id === conversationId) {
        setCurrentConversation({ ...currentConversation, title: newTitle });
      }

      toast({
        title: "Success",
        description: "Conversation renamed",
      });
    } catch (error: any) {
      console.error("Error renaming conversation:", error);
      toast({
        title: "Error",
        description: "Failed to rename conversation",
        variant: "destructive",
      });
    }
  };

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    createConversation,
    selectConversation,
    addMessage,
    deleteConversation,
    uploadFile,
    renameConversation,
    setCurrentConversation,
    setMessages,
  };
};
