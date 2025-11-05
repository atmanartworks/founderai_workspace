import { Bot, User, FileText, Download } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatBubbleProps {
  message: string;
  isAI: boolean;
  timestamp?: string;
  fileUrls?: string[];
}

export const ChatBubble = ({ message, isAI, timestamp, fileUrls }: ChatBubbleProps) => {
  // Parse file data if it exists
  const files = fileUrls?.map(url => {
    try {
      return JSON.parse(url);
    } catch {
      return { url, name: "File" };
    }
  }) || [];

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
          
          {/* Display attached files */}
          {files.length > 0 && (
            <div className="mt-3 space-y-2">
              {files.map((file: any, index: number) => (
                <a
                  key={index}
                  href={file.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={cn(
                    "flex items-center gap-2 p-2 rounded-md transition-colors group",
                    isAI ? "bg-muted/50 hover:bg-muted" : "bg-white/10 hover:bg-white/20"
                  )}
                >
                  <FileText className={cn("w-4 h-4", isAI ? "text-primary" : "text-white")} />
                  <span className="text-sm flex-1 truncate">{file.name}</span>
                  <Download className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                </a>
              ))}
            </div>
          )}
        </div>
        {timestamp && (
          <span className="text-xs text-muted-foreground mt-1 px-2">{timestamp}</span>
        )}
      </div>
    </div>
  );
};
