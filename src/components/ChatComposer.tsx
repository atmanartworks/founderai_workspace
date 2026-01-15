import { useState, useEffect, useRef, useCallback } from "react";
import { Paperclip, Mic, Send, X, ArrowUpIcon } from "lucide-react";

import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { cn } from "@/lib/utils";

interface ChatComposerProps {
  onSend: (message: string, files?: File[]) => Promise<void> | void;
}

// 👇 Add this at the very top of your file (before the component)
declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }

  interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    start: () => void;
    stop: () => void;
    onresult: ((event: SpeechRecognitionEvent) => void) | null;
    onerror: ((event: any) => void) | null;
  }

  interface SpeechRecognitionEvent extends Event {
    resultIndex: number;
    results: SpeechRecognitionResultList;
  }
}

interface AutoResizeProps {
  minHeight: number;
  maxHeight?: number;
}

function useAutoResizeTextarea({ minHeight, maxHeight }: AutoResizeProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`; // reset first
      const newHeight = Math.max(
        minHeight,
        Math.min(textarea.scrollHeight, maxHeight ?? Infinity)
      );
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight]
  );

  useEffect(() => {
    if (textareaRef.current) textareaRef.current.style.height = `${minHeight}px`;
  }, [minHeight]);

  return { textareaRef, adjustHeight };
}

export const ChatComposer = ({ onSend }: ChatComposerProps) => {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 48,
    maxHeight: 150,
  });

  // --- Speech Recognition setup ---
  useEffect(() => {
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        setMessage(transcript);
        adjustHeight();
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  // --- Send handler ---
  const handleSend = async () => {
    if (message.trim() || files.length > 0) {
      await onSend(message, files);
      setMessage("");
      setFiles([]);
      adjustHeight(true); // Reset height
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // --- Voice control ---
  const toggleRecording = () => {
    if (!recognitionRef.current) return alert("Voice recognition not supported in this browser.");

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  // --- File upload ---
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = e.target.files ? Array.from(e.target.files) : [];
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const handleFileRemove = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };


  return (
    <div className="border-t border-border/30 bg-transparent backdrop-blur-sm p-3 sm:p-4 md:p-6 highlight-top">
      <div className="max-w-4xl mx-auto space-y-2 sm:space-y-3">
        {/* File Preview */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {files.map((file, index) => (
              <div 
                key={index} 
                className="flex items-center gap-2 bg-card/60 backdrop-blur-sm border border-border/30 px-3 py-1.5 rounded-lg text-sm glass-card transition-smooth hover:bg-card/80"
              >
                <span className="text-foreground/90">{file.name}</span>
                <button 
                  onClick={() => handleFileRemove(index)} 
                  className="text-muted-foreground hover:text-foreground transition-colors ml-1"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input Box - Dark Glassmorphism Style */}
        <div className="relative bg-black/60 backdrop-blur-md rounded-xl border border-border/40 glass-card shadow-elevated">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              adjustHeight();
            }}
            onKeyPress={handleKeyPress}
            placeholder={`Type your request...`}
            className={cn(
              "w-full px-3 sm:px-4 py-2.5 sm:py-3 resize-none border-none",
              "bg-transparent text-foreground text-sm sm:text-base",
              "focus-visible:ring-0 focus-visible:ring-offset-0",
              "placeholder:text-muted-foreground/60 min-h-[44px] sm:min-h-[48px]",
              "transition-smooth"
            )}
            style={{ overflow: "hidden" }}
          />

          {/* Footer Buttons */}
          <div className="flex items-center justify-between p-2 sm:p-3 border-t border-border/30">
            <div className="flex items-center gap-2">
              {/* 📎 File Upload */}
              <Button
                variant="ghost"
                size="icon"
                className="text-foreground/80 hover:text-foreground hover:bg-accent/50 transition-smooth rounded-lg"
                onClick={handleFileButtonClick}
              >
                <Paperclip className="w-4 h-4" />
              </Button>
              <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileChange} />

              {/* 🎙️ Voice Button */}
              <Button
                onClick={toggleRecording}
                variant={isRecording ? "destructive" : "ghost"}
                size="icon"
                className={cn(
                  "text-foreground/80 hover:text-foreground transition-smooth rounded-lg",
                  isRecording && "animate-pulse bg-destructive/90 text-white"
                )}
              >
                <Mic className="w-4 h-4" />
              </Button>

            </div>

            {/* 🚀 Send Button */}
            <Button
              onClick={handleSend}
              disabled={!message.trim() && files.length === 0}
              className={cn(
                "flex items-center gap-1 px-3 py-2 rounded-lg transition-all",
                "bg-muted text-muted-foreground",
                "disabled:opacity-40 disabled:cursor-not-allowed",
                "hover:bg-muted/80 shadow-sm hover:shadow-md"
              )}
            >
              <ArrowUpIcon className="w-4 h-4" />
              <span className="sr-only">Send</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
