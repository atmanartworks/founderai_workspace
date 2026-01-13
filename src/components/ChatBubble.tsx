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

  const isImage = (filename: string) => {
    return /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(filename);
  };

  return (
    <div className={cn("flex gap-4 mb-6 animate-fade-in", isAI ? "flex-row" : "flex-row-reverse")}>
      <div className={cn(
        "flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-smooth",
        isAI 
          ? "bg-card/60 backdrop-blur-sm text-primary border border-border/30 shadow-sm" 
          : "bg-accent/60 backdrop-blur-sm text-foreground border border-border/30 shadow-sm"
      )}>
        {isAI ? <Bot className="w-4.5 h-4.5" /> : <User className="w-4.5 h-4.5" />}
      </div>
      
      <div className={cn("flex-1 max-w-[80%] md:max-w-[70%]", !isAI && "flex flex-col items-end")}>
        <div className={cn(
          "rounded-2xl px-5 py-3.5 transition-smooth glass-card highlight-top",
          isAI 
            ? "bg-card/80 text-card-foreground border-border/40" 
            : "bg-accent/70 text-accent-foreground border-border/40"
        )}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground/95">{message}</p>
          
          {/* Display attached files */}
          {files.length > 0 && (
            <div className="mt-3 space-y-2">
              {files.map((file: any, index: number) => (
                isImage(file.name) ? (
                  <div key={index} className="space-y-2">
                    <img
                      src={file.url}
                      alt={file.name}
                      className="rounded-lg max-w-full h-auto max-h-96 object-contain border border-border/30 shadow-sm"
                    />
                    <a
                      href={file.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={cn(
                        "flex items-center gap-2 p-2.5 rounded-lg transition-all group text-xs glass hover:bg-accent/30",
                        isAI ? "bg-muted/30" : "bg-accent/40"
                      )}
                    >
                      <FileText className={cn("w-3.5 h-3.5", isAI ? "text-primary" : "text-foreground")} />
                      <span className="flex-1 truncate text-foreground/90">{file.name}</span>
                      <Download className="w-3.5 h-3.5 opacity-0 group-hover:opacity-70 transition-opacity text-muted-foreground" />
                    </a>
                  </div>
                ) : (
                  <a
                    key={index}
                    href={file.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={cn(
                      "flex items-center gap-2.5 p-2.5 rounded-lg transition-all group glass hover:bg-accent/30",
                      isAI ? "bg-muted/30" : "bg-accent/40"
                    )}
                  >
                    <FileText className={cn("w-4 h-4", isAI ? "text-primary" : "text-foreground")} />
                    <span className="text-sm flex-1 truncate text-foreground/90">{file.name}</span>
                    <Download className="w-4 h-4 opacity-0 group-hover:opacity-70 transition-opacity text-muted-foreground" />
                  </a>
                )
              ))}
            </div>
          )}
        </div>
        {timestamp && (
          <span className="text-xs text-muted-foreground/70 mt-2 px-2 block">{timestamp}</span>
        )}
      </div>
    </div>
  );
};
