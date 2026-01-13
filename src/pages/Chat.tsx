import { useState, useEffect, useRef } from "react";
import { ChatBubble } from "@/components/ChatBubble";
import { ChatComposer } from "@/components/ChatComposer";
import { DocumentViewerPanel } from "@/components/DocumentViewerPanel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { MessageSquare, Settings, User, Folder, ChevronLeft, LogOut, Plus, Trash2, Edit2, Bot } from "lucide-react";
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
  
  // Document viewer panel state
  const [documentViewerOpen, setDocumentViewerOpen] = useState(false);
  const [viewingDocumentId, setViewingDocumentId] = useState<string | null>(null);
  const [viewingChunkId, setViewingChunkId] = useState<string | null>(null);
  const [viewingQuotedText, setViewingQuotedText] = useState<string | null>(null);

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

      // Add AI response with citations (citations are handled in ChatBubble component)
      await addMessage(response.response, true, undefined, conversation.id, response.citations);
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
        className={`${sidebarOpen ? "w-72" : "w-0"} lg:w-72 bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col backdrop-blur-sm`}
        style={{
          background: 'linear-gradient(180deg, hsl(220, 13%, 10%), hsl(220, 13%, 9%))',
        }}
      >
        <div className="p-4 border-b border-sidebar-border/50 highlight-top">
          <div className="flex items-center gap-3 mb-6">
            <div className="relative">
              <img src="/atman-logo.png" alt="ĀTMAN" className="w-16 h-16 object-contain" />
              <div className="absolute inset-0 bg-primary/10 blur-xl rounded-full -z-10" />
            </div>
            <span className="text-xl font-semibold golden-text">Founder GPT</span>
          </div>

          <nav className="space-y-1">
            <Button 
              variant="ghost" 
              className="w-full justify-start bg-sidebar-accent hover:bg-sidebar-accent/80 transition-smooth"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat
            </Button>
            <Button 
              variant="ghost" 
              className="w-full justify-start hover:bg-sidebar-accent/50 transition-smooth" 
              onClick={() => navigate("/dashboard")}
            >
              <Folder className="w-4 h-4 mr-2" />
              Vault
            </Button>
            <Button 
              variant="ghost" 
              className="w-full justify-start hover:bg-sidebar-accent/50 transition-smooth"
            >
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
              className="h-7 w-7 hover:bg-sidebar-accent/50 transition-smooth rounded-lg"
              onClick={handleNewChat}
              title="New Chat"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-1">
            {conversations.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-6">
                No conversations yet
              </p>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`flex items-center gap-1 group px-2 py-1.5 rounded-lg transition-all ${
                    currentConversation?.id === conv.id 
                      ? "bg-sidebar-accent shadow-sm" 
                      : "hover:bg-sidebar-accent/40"
                  }`}
                >
                  <Button
                    variant="ghost"
                    className="flex-1 justify-start text-sm text-left min-w-0 px-2 py-1 h-auto font-normal hover:bg-transparent"
                    onClick={() => selectConversation(conv)}
                    title={conv.title}
                  >
                    <span className="block truncate text-sidebar-foreground">{conv.title}</span>
                  </Button>
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 hover:bg-sidebar-accent/60 rounded-md"
                      onClick={(e) => handleRenameClick(e, conv.id, conv.title)}
                      title="Rename"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 hover:bg-destructive/20 rounded-md"
                      onClick={(e) => handleDeleteConversation(e, conv.id)}
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5 text-destructive/80" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="p-4 border-t border-sidebar-border/50 space-y-2 highlight-top">
          <Button 
            variant="ghost" 
            className="w-full justify-start gap-2 hover:bg-sidebar-accent/50 transition-smooth rounded-lg"
            onClick={() => navigate("/profile")}
          >
            {avatarUrl ? (
              <div className="relative">
                <img src={avatarUrl} alt="Avatar" className="w-6 h-6 rounded-full object-cover ring-2 ring-sidebar-border/50" />
                <div className="absolute inset-0 rounded-full bg-primary/20 blur-sm -z-10" />
              </div>
            ) : (
              <div className="w-6 h-6 rounded-full bg-sidebar-accent flex items-center justify-center">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
            <span className="truncate text-sm">{user?.email || "Loading..."}</span>
          </Button>
          <Button 
            variant="ghost" 
            className="w-full justify-start text-destructive/90 hover:text-destructive hover:bg-destructive/10 transition-smooth rounded-lg"
            onClick={handleLogout}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-background">
        {/* Header */}
        <header className="h-16 border-b border-border/30 flex items-center justify-between px-6 backdrop-blur-sm glass highlight-top">
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              size="icon" 
              className="lg:hidden hover:bg-accent/50 transition-smooth rounded-lg" 
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <ChevronLeft className={`w-5 h-5 transition-transform duration-300 ${sidebarOpen ? "" : "rotate-180"}`} />
            </Button>
            <h1 className="text-lg font-medium text-foreground/90">
              {currentConversation?.title || "New Chat"}
            </h1>
          </div>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-4xl mx-auto">
            {loading && messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-12">
                <div className="inline-block w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mb-4" />
                <p>Loading...</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="text-center py-16">
                <div className="inline-block p-4 rounded-2xl bg-card/50 backdrop-blur-sm mb-6">
                  <Bot className="w-12 h-12 text-primary/60" />
                </div>
                <h2 className="text-2xl font-semibold mb-3 text-foreground">
                  Hello! I'm your AI co-founder.
                </h2>
                <p className="text-muted-foreground text-lg">How can I help you build and scale your startup today?</p>
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
                    citations={message.citations}
                    onCitationClick={(documentId, chunkId, quotedText) => {
                      console.log("Citation clicked in Chat:", { documentId, chunkId, quotedText });
                      setViewingDocumentId(documentId);
                      setViewingChunkId(chunkId);
                      setViewingQuotedText(quotedText);
                      setDocumentViewerOpen(true);
                      console.log("Document viewer state updated");
                    }}
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

      {/* Document Viewer Panel */}
      {documentViewerOpen && (
        <DocumentViewerPanel
          documentId={viewingDocumentId}
          chunkId={viewingChunkId}
          quotedText={viewingQuotedText}
          onClose={() => {
            setDocumentViewerOpen(false);
            setViewingDocumentId(null);
            setViewingChunkId(null);
            setViewingQuotedText(null);
          }}
        />
      )}
    </div>
  );
};

export default Chat;
