import { useState, useEffect, useRef, useCallback } from "react";
import { Paperclip, Mic, Send, X, Bot, Code2, Rocket, Layers, Palette, CircleUserRound, MonitorIcon, FileUp, ImageIcon, PlusIcon, ArrowUpIcon } from "lucide-react";
import { SiOpenai, SiAnthropic } from "react-icons/si";

import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface ChatComposerEnhancedProps {
  onSend: (message: string, files?: File[]) => Promise<void> | void;
  model?: string;
  onModelChange?: (model: string) => void;
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

interface QuickActionProps {
  icon: React.ReactNode;
  label: string;
  onClick?: () => void;
}

function QuickAction({ icon, label, onClick }: QuickActionProps) {
  return (
    <Button
      variant="outline"
      onClick={onClick}
      className="flex items-center gap-2 rounded-full border-border/40 bg-card/50 backdrop-blur-sm text-foreground/80 hover:text-foreground hover:bg-accent/50 hover:border-border/60 transition-smooth shadow-sm hover:shadow-md"
    >
      {icon}
      <span className="text-xs font-medium">{label}</span>
    </Button>
  );
}

export const ChatComposerEnhanced = ({ 
  onSend, 
  model: externalModel,
  onModelChange 
}: ChatComposerEnhancedProps) => {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [model, setModel] = useState(externalModel || "ChatGPT");
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 48,
    maxHeight: 150,
  });

  // Sync external model changes
  useEffect(() => {
    if (externalModel) {
      setModel(externalModel);
    }
  }, [externalModel]);

  // Speech Recognition setup
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
  }, [adjustHeight]);

  // Send handler
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

  // Voice control
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

  // File upload
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

  const handleModelChange = (newModel: string) => {
    setModel(newModel);
    if (onModelChange) {
      onModelChange(newModel);
    }
  };

  // AI Model List
  const models = [{ name: "ChatGPT" }, { name: "Gemini" }, { name: "Claude" }];

  // Quick action handlers
  const quickActions = [
    { icon: <Code2 className="w-4 h-4" />, label: "Generate Code", prompt: "Generate code for " },
    { icon: <Rocket className="w-4 h-4" />, label: "Launch App", prompt: "Help me launch my app by " },
    { icon: <Layers className="w-4 h-4" />, label: "UI Components", prompt: "Create UI components for " },
    { icon: <Palette className="w-4 h-4" />, label: "Theme Ideas", prompt: "Suggest theme ideas for " },
    { icon: <CircleUserRound className="w-4 h-4" />, label: "User Dashboard", prompt: "Design a user dashboard with " },
    { icon: <MonitorIcon className="w-4 h-4" />, label: "Landing Page", prompt: "Create a landing page for " },
    { icon: <FileUp className="w-4 h-4" />, label: "Upload Docs", onClick: handleFileButtonClick },
    { icon: <ImageIcon className="w-4 h-4" />, label: "Image Assets", onClick: handleFileButtonClick },
  ];

  const handleQuickAction = (action: typeof quickActions[0]) => {
    if (action.onClick) {
      action.onClick();
    } else if (action.prompt) {
      setMessage(action.prompt);
      adjustHeight();
      textareaRef.current?.focus();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mb-8">
      {/* File Preview */}
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
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

      {/* Input Box */}
      <div className="relative bg-card/60 backdrop-blur-md rounded-xl border border-border/40 glass-card highlight-top shadow-elevated">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => {
            setMessage(e.target.value);
            adjustHeight();
          }}
          onKeyPress={handleKeyPress}
          placeholder={`Ask ${model} anything...`}
          className={cn(
            "w-full px-4 py-3 resize-none border-none",
            "bg-transparent text-foreground text-sm",
            "focus-visible:ring-0 focus-visible:ring-offset-0",
            "placeholder:text-muted-foreground/60 min-h-[48px]",
            "transition-smooth"
          )}
          style={{ overflow: "hidden" }}
        />

        {/* Footer Buttons */}
        <div className="flex items-center justify-between p-3 border-t border-border/30">
          <div className="flex items-center gap-2">
            {/* File Upload */}
            <Button
              variant="ghost"
              size="icon"
              className="text-foreground/80 hover:text-foreground hover:bg-accent/50 transition-smooth rounded-lg"
              onClick={handleFileButtonClick}
            >
              <Paperclip className="w-4 h-4" />
            </Button>
            <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileChange} />

            {/* Voice Button */}
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

            {/* AI Model Selector */}
            <Popover>
              <PopoverTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="text-foreground/80 hover:text-foreground hover:bg-accent/50 transition-smooth rounded-lg relative"
                >
                  <Bot className="w-4 h-4" />
                  <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 text-[9px] text-muted-foreground/70 font-medium">{model}</span>
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-40 p-2 glass-card border-border/40">
                <div className="flex flex-col gap-1">
                  {models.map((m) => (
                    <Button
                      key={m.name}
                      variant={m.name === model ? "default" : "ghost"}
                      onClick={() => handleModelChange(m.name)}
                      className="flex justify-start gap-2 text-sm items-center transition-smooth rounded-lg"
                    >
                      {m.name}
                    </Button>
                  ))}
                </div>
              </PopoverContent>
            </Popover>
          </div>

          {/* Send Button */}
          <Button
            onClick={handleSend}
            disabled={!message.trim() && files.length === 0}
            className={cn(
              "flex items-center gap-1 px-3 py-2 rounded-lg transition-all",
              "bg-primary text-primary-foreground hover:bg-primary/90",
              "disabled:opacity-40 disabled:cursor-not-allowed",
              "shadow-sm hover:shadow-md glow-hover"
            )}
          >
            <ArrowUpIcon className="w-4 h-4" />
            <span className="sr-only">Send</span>
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex items-center justify-center flex-wrap gap-3 mt-6">
        {quickActions.map((action, index) => (
          <QuickAction
            key={index}
            icon={action.icon}
            label={action.label}
            onClick={() => handleQuickAction(action)}
          />
        ))}
      </div>
    </div>
  );
};
