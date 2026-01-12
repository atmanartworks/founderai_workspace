import { useState, useEffect, useRef } from "react";
import { ChatBubble } from "@/components/ChatBubble";
import { ChatComposer } from "@/components/ChatComposer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { MessageSquare, Settings, User, Folder, ChevronLeft, LogOut, Plus, Trash2, Edit2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { useConversations } from "@/hooks/useConversations";
import { ragApi } from "@/services/ragApi";
import { generateSmartTitle } from "@/services/titleGenerator";
import type { User as SupabaseUser, Session } from "@supabase/supabase-js";

const Chat = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<SupabaseUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string>("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [renamingConversationId, setRenamingConversationId] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
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
  } = useConversations(user?.id || null);

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        
        if (!session) {
          navigate("/login");
        }
      }
    );

    supabase.auth.getSession().then(async ({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      
      if (!session) {
        navigate("/login");
        return;
      }

      // Fetch avatar
      const { data: profile } = await supabase
        .from("profiles")
        .select("avatar_url")
        .eq("id", session.user.id)
        .single();

      if (profile?.avatar_url) {
        setAvatarUrl(profile.avatar_url);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  // Don't auto-create conversation on mount - wait for user to send a message

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Keyboard shortcut: Ctrl/Cmd+K to create new chat
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        handleNewChat();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleLogout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      toast({
        title: "Error",
        description: "Failed to log out. Please try again.",
        variant: "destructive",
      });
    } else {
      toast({
        title: "Success",
        description: "Logged out successfully!",
      });
      navigate("/login");
    }
  };

  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!user) return;

    // Ensure we have a conversation
    let conversation = currentConversation;
    let isNewConversation = false;
    
    if (!conversation) {
      // Generate a smart title from the first message
      const smartTitle = generateSmartTitle(content);
      const newConv = await createConversation(smartTitle);
      
      if (!newConv) {
        toast({
          title: "Error",
          description: "Failed to create conversation",
          variant: "destructive",
        });
        return;
      }
      conversation = newConv;
      isNewConversation = true;
    }

    // Upload files to RAG vault if any
    let uploadedFiles: string[] = [];
    if (files && files.length > 0) {
      toast({
        title: "Uploading files...",
        description: `Uploading ${files.length} file(s) to vault`,
      });

      try {
        // Get existing files to check for duplicates
        const existingFilesResponse = await ragApi.listFiles();
        const existingFiles = existingFilesResponse.files || [];
        const existingFileNames = existingFiles.map(f => f.original_name);

        const uploadPromises = files.map(async (file) => {
          let fileName = file.name;
          
          // Check for duplicates and rename if necessary
          if (existingFileNames.includes(fileName)) {
            const nameParts = fileName.split('.');
            const extension = nameParts.pop();
            const baseName = nameParts.join('.');
            
            let counter = 1;
            let newFileName = `${baseName} duplicate ${counter}.${extension}`;
            
            while (existingFileNames.includes(newFileName)) {
              counter++;
              newFileName = `${baseName} duplicate ${counter}.${extension}`;
            }
            
            fileName = newFileName;
            existingFileNames.push(fileName); // Add to list to prevent duplicates in same batch
            
            // Create a new File object with the renamed filename
            const renamedFile = new File([file], fileName, { type: file.type });
            file = renamedFile;
          }

          const result = await ragApi.uploadFile(user.id, file);
          // Auto-embed the document after upload
          if (result.vault_id) {
            await ragApi.embedDocument(result.vault_id);
          }
          return result.storage_path;
        });
        uploadedFiles = await Promise.all(uploadPromises);
        
        toast({
          title: "Success",
          description: "Files uploaded and embedded successfully",
        });
      } catch (error: any) {
        toast({
          title: "Upload Error",
          description: error.message || "Failed to upload files",
          variant: "destructive",
        });
      }
    }

    // Add user message with the conversation we have
    const userMessage = await addMessage(content, false, uploadedFiles, conversation.id);
    if (!userMessage) {
      toast({
        title: "Error",
        description: "Failed to save your message",
        variant: "destructive",
      });
      return;
    }

    // Get AI response from RAG backend
    try {
      const response = await ragApi.sendMessage({
        conversation_id: conversation.id,
        message: content,
        user_id: user.id,
        top_k: 10, // Retrieve more chunks for detailed answers
      });

      // Add AI response with sources
      let aiMessage = response.response;
      if (response.sources && response.sources.length > 0) {
        aiMessage += `\n\n📚 **Sources:**\n${response.sources.map(s => `• ${s}`).join('\n')}`;
      }

      await addMessage(aiMessage, true, undefined, conversation.id);
    } catch (error: any) {
      console.error("RAG API Error:", error);
      await addMessage(
        `⚠️ Sorry, I encountered an error: ${error.message}\n\nPlease make sure the RAG backend is running at http://127.0.0.1:8000`,
        true,
        undefined,
        conversation.id
      );
    }
  };

  const handleNewChat = async () => {
    // Clear current conversation - new one will be created when user sends first message
    setCurrentConversation(null);
    setMessages([]);
    
    toast({
      title: "New Chat",
      description: "Start typing to begin a new conversation",
    });
  };

  const handleDeleteConversation = async (
    e: React.MouseEvent,
    conversationId: string
  ) => {
    e.stopPropagation();
    await deleteConversation(conversationId);
  };

  const handleRenameClick = (e: React.MouseEvent, conversationId: string, currentTitle: string) => {
    e.stopPropagation();
    setRenamingConversationId(conversationId);
    setNewTitle(currentTitle);
    setRenameDialogOpen(true);
  };

  const handleRenameSubmit = async () => {
    if (renamingConversationId && newTitle.trim()) {
      await renameConversation(renamingConversationId, newTitle.trim());
      setRenameDialogOpen(false);
      setRenamingConversationId(null);
      setNewTitle("");
    }
  };

  return (
    <div className="h-screen flex overflow-hidden bg-background">
      {/* Left Sidebar */}
      <aside
        className={`${sidebarOpen ? "w-72" : "w-0"} lg:w-72 bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center gap-3 mb-6">
            <img src="/atman-logo.png" alt="ĀTMAN" className="w-16 h-16 object-contain" />
            <span className="text-xl font-bold golden-text">Founder GPT</span>
          </div>

          <nav className="space-y-1">
            {/* <Button 
              variant="ghost" 
              className="w-full justify-start"
              onClick={() => navigate("/")}
            >
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button> */}
            <Button variant="ghost" className="w-full justify-start bg-sidebar-accent">
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat
            </Button>
            <Button variant="ghost" className="w-full justify-start" onClick={() => navigate("/dashboard")}>
              <Folder className="w-4 h-4 mr-2" />
              Vault
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </nav>
        </div>

        <div className="flex-1 p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">CHAT HISTORY</h3>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={handleNewChat}
              title="New Chat"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-0.5">
            {conversations.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                No conversations yet
              </p>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`flex items-center gap-1 group px-1 py-0.5 rounded-md transition-colors ${
                    currentConversation?.id === conv.id ? "bg-sidebar-accent" : "hover:bg-sidebar-accent/50"
                  }`}
                >
                  <Button
                    variant="ghost"
                    className="flex-1 justify-start text-sm text-left min-w-0 px-2 py-1.5 h-auto font-normal"
                    onClick={() => selectConversation(conv)}
                    title={conv.title}
                  >
                    <span className="block truncate">{conv.title}</span>
                  </Button>
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={(e) => handleRenameClick(e, conv.id, conv.title)}
                      title="Rename"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={(e) => handleDeleteConversation(e, conv.id)}
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="p-4 border-t border-sidebar-border space-y-2">
          <Button 
            variant="ghost" 
            className="w-full justify-start gap-2"
            onClick={() => navigate("/profile")}
          >
            {avatarUrl ? (
              <img src={avatarUrl} alt="Avatar" className="w-6 h-6 rounded-full object-cover" />
            ) : (
              <User className="w-4 h-4" />
            )}
            <span className="truncate">{user?.email || "Loading..."}</span>
          </Button>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-destructive hover:text-destructive"
            onClick={handleLogout}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 border-b border-border flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <ChevronLeft className={`w-5 h-5 transition-transform ${sidebarOpen ? "" : "rotate-180"}`} />
            </Button>
            <h1 className="text-lg font-semibold">
              {currentConversation?.title || "Select a conversation"}
            </h1>
          </div>

        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-4xl mx-auto">
            {loading && messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">Loading...</div>
            ) : messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <h2 className="text-2xl font-semibold mb-2">
                  Hello! I'm your AI co-founder.
                </h2>
                <p>How can I help you build and scale your startup today?</p>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <ChatBubble
                    key={message.id}
                    message={message.content}
                    isAI={message.is_ai}
                    timestamp={new Date(message.created_at).toLocaleString()}
                    fileUrls={message.file_urls}
                  />
                ))}
                {/* Invisible element to scroll to */}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>

        {/* Chat Composer */}
        <ChatComposer onSend={handleSendMessage} />
      </main>

      {/* Rename Dialog */}
      <Dialog open={renameDialogOpen} onOpenChange={setRenameDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Conversation</DialogTitle>
          </DialogHeader>
          <Input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Enter new title"
            onKeyPress={(e) => {
              if (e.key === "Enter") {
                handleRenameSubmit();
              }
            }}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleRenameSubmit}>Rename</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Chat;
