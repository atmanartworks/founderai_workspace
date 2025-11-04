import { useState } from "react";
import { Paperclip, Mic, Send } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

interface ChatComposerProps {
  onSend: (message: string) => void;
}

export const ChatComposer = ({ onSend }: ChatComposerProps) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border bg-background p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-2">
          <Button variant="ghost" size="icon" className="flex-shrink-0">
            <Paperclip className="w-5 h-5" />
          </Button>
          
          <div className="flex-1 relative">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your AI co-founder anything..."
              className="min-h-[60px] max-h-[200px] resize-none bg-card border-border pr-12"
            />
          </div>

          <Button variant="ghost" size="icon" className="flex-shrink-0">
            <Mic className="w-5 h-5" />
          </Button>
          
          <Button 
            onClick={handleSend}
            disabled={!message.trim()}
            className="gradient-primary hover:opacity-90 transition-smooth flex-shrink-0"
            size="icon"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  );
};
