"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  ImageIcon,
  FileUp,
  MonitorIcon,
  CircleUserRound,
  ArrowUpIcon,
  Paperclip,
  PlusIcon,
  Code2,
  Palette,
  Layers,
  Rocket,
} from "lucide-react";

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

export default function RuixenMoonChat() {
  const [message, setMessage] = useState("");
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 48,
    maxHeight: 150,
  });

  return (
    <div
      className="relative w-full h-screen bg-cover bg-center flex flex-col items-center"
      style={{
        background: "hsl(var(--background))",
        backgroundImage: 
          "radial-gradient(at 0% 0%, hsl(220 15% 10% / 0.3) 0px, transparent 50%), " +
          "radial-gradient(at 100% 100%, hsl(217 91% 60% / 0.05) 0px, transparent 50%)",
        backgroundAttachment: "fixed",
      }}
    >
      {/* Centered AI Title */}
      <div className="flex-1 w-full flex flex-col items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-semibold text-foreground drop-shadow-sm">
            Ruixen AI
          </h1>
          <p className="mt-2 text-muted-foreground">
            Build something amazing — just start typing below.
          </p>
        </div>
      </div>

      {/* Input Box Section */}
      <div className="w-full max-w-3xl mb-[20vh]">
        <div className="relative bg-black/60 backdrop-blur-md rounded-xl border border-border/40 glass-card shadow-elevated">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              adjustHeight();
            }}
            placeholder="Type your request..."
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
            <Button
              variant="ghost"
              size="icon"
              className="text-foreground/80 hover:text-foreground hover:bg-accent/50 transition-smooth rounded-lg"
            >
              <Paperclip className="w-4 h-4" />
            </Button>

            <div className="flex items-center gap-2">
              <Button
                disabled
                className={cn(
                  "flex items-center gap-1 px-3 py-2 rounded-lg transition-colors",
                  "bg-muted text-muted-foreground cursor-not-allowed",
                  "hover:bg-muted"
                )}
              >
                <ArrowUpIcon className="w-4 h-4" />
                <span className="sr-only">Send</span>
              </Button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center justify-center flex-wrap gap-3 mt-6">
          <QuickAction icon={<Code2 className="w-4 h-4" />} label="Generate Code" />
          <QuickAction icon={<Rocket className="w-4 h-4" />} label="Launch App" />
          <QuickAction icon={<Layers className="w-4 h-4" />} label="UI Components" />
          <QuickAction icon={<Palette className="w-4 h-4" />} label="Theme Ideas" />
          <QuickAction icon={<CircleUserRound className="w-4 h-4" />} label="User Dashboard" />
          <QuickAction icon={<MonitorIcon className="w-4 h-4" />} label="Landing Page" />
          <QuickAction icon={<FileUp className="w-4 h-4" />} label="Upload Docs" />
          <QuickAction icon={<ImageIcon className="w-4 h-4" />} label="Image Assets" />
        </div>
      </div>
    </div>
  );
}

interface QuickActionProps {
  icon: React.ReactNode;
  label: string;
}

function QuickAction({ icon, label }: QuickActionProps) {
  return (
    <Button
      variant="outline"
      className="flex items-center gap-2 rounded-full border-border/40 bg-card/50 backdrop-blur-sm text-foreground/80 hover:text-foreground hover:bg-accent/50 hover:border-border/60 transition-smooth shadow-sm hover:shadow-md"
    >
      {icon}
      <span className="text-xs font-medium">{label}</span>
    </Button>
  );
}
