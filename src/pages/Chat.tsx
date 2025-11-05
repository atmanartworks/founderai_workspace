import { useState, useEffect } from "react";
import { ChatBubble } from "@/components/ChatBubble";
import { ChatComposer } from "@/components/ChatComposer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Zap, Home, MessageSquare, Settings, User, FileText, Folder, ChevronLeft, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import type { User as SupabaseUser, Session } from "@supabase/supabase-js";

interface Message {
  id: string;
  content: string;
  isAI: boolean;
  timestamp: string;
}

const Chat = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<SupabaseUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI co-founder. How can I help you build and scale your startup today?",
      isAI: true,
      timestamp: "Just now",
    },
  ]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [contextPanelOpen, setContextPanelOpen] = useState(true);

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        
        if (!session) {
          navigate("/");
        }
      }
    );

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      
      if (!session) {
        navigate("/");
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

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
      navigate("/");
    }
  };

  const handleSendMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      isAI: false,
      timestamp: "Just now",
    };

    setMessages([...messages, newMessage]);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content:
          "That's a great question! Let me help you with that. Based on current best practices and successful startup strategies, here's what I recommend...",
        isAI: true,
        timestamp: "Just now",
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="h-screen flex overflow-hidden bg-background">
      {/* Left Sidebar */}
      <aside
        className={`${sidebarOpen ? "w-64" : "w-0"} lg:w-64 bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">FounderGPT</span>
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
          <h3 className="text-xs font-semibold text-muted-foreground mb-3">CHAT HISTORY</h3>
          <div className="space-y-1">
            <Button variant="ghost" className="w-full justify-start text-sm">
              Product Strategy Discussion
            </Button>
            <Button variant="ghost" className="w-full justify-start text-sm">
              Go-to-Market Plan
            </Button>
            <Button variant="ghost" className="w-full justify-start text-sm">
              Fundraising Advice
            </Button>
          </div>
        </div>

        <div className="p-4 border-t border-sidebar-border space-y-2">
          <Button 
            variant="ghost" 
            className="w-full justify-start"
            onClick={() => navigate("/profile")}
          >
            <User className="w-4 h-4 mr-2" />
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
            <h1 className="text-lg font-semibold">New Conversation</h1>
          </div>

          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            onClick={() => setContextPanelOpen(!contextPanelOpen)}
          >
            Context Panel
          </Button>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatBubble
                key={message.id}
                message={message.content}
                isAI={message.isAI}
                timestamp={message.timestamp}
              />
            ))}
          </div>
        </div>

        {/* Chat Composer */}
        <ChatComposer onSend={handleSendMessage} />
      </main>

      {/* Right Context Panel */}
      <aside
        className={`${
          contextPanelOpen ? "w-80" : "w-0"
        } md:w-80 bg-card border-l border-border transition-all duration-300 overflow-hidden`}
      >
        <div className="p-4 h-full overflow-y-auto">
          <h2 className="text-lg font-semibold mb-4">Dashboard</h2>

          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start text-sm" size="sm">
              📁 No. of. Files
            </Button>

            {/* Storage Taken Section */}
            <div className="p-3 border rounded-lg bg-muted/30">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium flex items-center gap-2">📦 Storage</span>
                <span className="text-xs text-muted-foreground">0 GB Total</span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                <div className="bg-blue-500 h-2" style={{ width: `${((0 - 0) / 0) * 0}%` }}></div>
              </div>

              {/* Storage Info */}
              <div className="mt-1 text-xs text-muted-foreground text-right">0 GB free of 0 GB</div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
};

export default Chat;
