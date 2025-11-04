import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatBubbleProps {
  message: string;
  isAI: boolean;
  timestamp?: string;
}

export const ChatBubble = ({ message, isAI, timestamp }: ChatBubbleProps) => {
  return (
    <div className={cn("flex gap-3 mb-6 animate-fade-in", isAI ? "flex-row" : "flex-row-reverse")}>
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center",
        isAI ? "bg-primary/10 text-primary" : "bg-card text-foreground border border-border"
      )}>
        {isAI ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
      </div>
      
      <div className={cn("flex-1 max-w-[80%] md:max-w-[70%]", !isAI && "flex flex-col items-end")}>
        <div className={cn(
          "rounded-2xl px-4 py-3 transition-smooth",
          isAI 
            ? "bg-card text-card-foreground" 
            : "gradient-primary text-white"
        )}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
        </div>
        {timestamp && (
          <span className="text-xs text-muted-foreground mt-1 px-2">{timestamp}</span>
        )}
      </div>
    </div>
  );
};
