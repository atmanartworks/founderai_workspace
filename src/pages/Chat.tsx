import { useState } from "react";
import { ChatBubble } from "@/components/ChatBubble";
import { ChatComposer } from "@/components/ChatComposer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Zap, Home, MessageSquare, Settings, User, FileText, Folder, ChevronLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Message {
  id: string;
  content: string;
  isAI: boolean;
  timestamp: string;
}

const Chat = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI co-founder. How can I help you build and scale your startup today?",
      isAI: true,
      timestamp: "Just now"
    }
  ]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [contextPanelOpen, setContextPanelOpen] = useState(true);

  const handleSendMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      isAI: false,
      timestamp: "Just now"
    };
    
    setMessages([...messages, newMessage]);
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: "That's a great question! Let me help you with that. Based on current best practices and successful startup strategies, here's what I recommend...",
        isAI: true,
        timestamp: "Just now"
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="h-screen flex overflow-hidden bg-background">
      {/* Left Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} lg:w-64 bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col`}>
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">FounderGPT</span>
          </div>
          
          <nav className="space-y-1">
            <Button 
              variant="ghost" 
              className="w-full justify-start"
              onClick={() => navigate("/")}
            >
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button>
            <Button 
              variant="ghost" 
              className="w-full justify-start bg-sidebar-accent"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat
            </Button>
            <Button 
              variant="ghost" 
              className="w-full justify-start"
              onClick={() => navigate("/dashboard")}
            >
              <Folder className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </nav>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto">
          <h3 className="text-xs font-semibold text-muted-foreground mb-3">RECENT CHATS</h3>
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
        
        <div className="p-4 border-t border-sidebar-border">
          <Button variant="ghost" className="w-full justify-start">
            <User className="w-4 h-4 mr-2" />
            <span className="truncate">john@startup.com</span>
          </Button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 border-b border-border flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <ChevronLeft className={`w-5 h-5 transition-transform ${sidebarOpen ? '' : 'rotate-180'}`} />
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
      <aside className={`${contextPanelOpen ? 'w-80' : 'w-0'} md:w-80 bg-card border-l border-border transition-all duration-300 overflow-hidden`}>
        <div className="p-4 h-full overflow-y-auto">
          <h2 className="text-lg font-semibold mb-4">Context Panel</h2>
          
          <Card className="p-4 mb-4 bg-background border-border">
            <h3 className="text-sm font-semibold mb-2">Project Info</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-muted-foreground">Industry:</span>
                <span className="ml-2">B2B SaaS</span>
              </div>
              <div>
                <span className="text-muted-foreground">Stage:</span>
                <span className="ml-2">Pre-seed</span>
              </div>
            </div>
          </Card>
          
          <div className="mb-4">
            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Templates
            </h3>
            <div className="space-y-2">
              <Button variant="outline" className="w-full justify-start text-sm" size="sm">
                Business Model Canvas
              </Button>
              <Button variant="outline" className="w-full justify-start text-sm" size="sm">
                Pitch Deck Outline
              </Button>
              <Button variant="outline" className="w-full justify-start text-sm" size="sm">
                Growth Strategy
              </Button>
              <Button variant="outline" className="w-full justify-start text-sm" size="sm">
                Market Analysis
              </Button>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
};

export default Chat;
