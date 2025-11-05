import { useState, useEffect, useRef } from "react";
import { Paperclip, Mic, Send, X, Bot } from "lucide-react";
// import { FaGoogle, FaRobot } from "react-icons/fa6"; // Gemini & fallback
import { SiOpenai, SiAnthropic } from "react-icons/si"; // ChatGPT & Claude

import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { cn } from "@/lib/utils"; // optional utility if you have it in your project

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

export const ChatComposer = ({ onSend }: ChatComposerProps) => {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [model, setModel] = useState("ChatGPT");
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

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

  // --- AI Model List ---
  const models = [{ name: "ChatGPT" }, { name: "Gemini" }, { name: "Claude" }];

  return (
    <div className="border-t border-border bg-background p-4">
      <div className="max-w-4xl mx-auto space-y-2">
        {/* File Preview */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center gap-2 bg-muted px-3 py-1 rounded-lg text-sm">
                <span>{file.name}</span>
                <button onClick={() => handleFileRemove(index)} className="text-muted-foreground">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input Row */}
        <div className="flex items-end gap-2">
          {/* 📎 File Upload */}
          <Button variant="ghost" size="icon" className="flex-shrink-0" onClick={handleFileButtonClick}>
            <Paperclip className="w-5 h-5" />
          </Button>

          <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileChange} />

          {/* 🧠 Textarea */}
          <div className="flex-1 relative">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask ${model} anything...`}
              className="min-h-[60px] max-h-[200px] resize-none bg-card border-border pr-12"
            />
          </div>

          {/* 🎙️ Voice Button */}
          <Button
            onClick={toggleRecording}
            variant={isRecording ? "destructive" : "ghost"}
            size="icon"
            className={`flex-shrink-0 transition-all ${isRecording ? "animate-pulse bg-red-500 text-white" : ""}`}
          >
            <Mic className="w-5 h-5" />
          </Button>

          {/* 🤖 AI Model Selector */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="flex-shrink-0 relative">
                <Bot className="w-5 h-5" />
                <span className="absolute -bottom-1 text-[10px] text-muted-foreground">{model}</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-40 p-2">
              <div className="flex flex-col gap-1">
                {models.map((m) => (
                  <Button
                    key={m.name}
                    variant={m.name === model ? "default" : "ghost"}
                    onClick={() => setModel(m.name)}
                    className="flex justify-start gap-2 text-sm items-center"
                  >
                    {m.name}
                  </Button>
                ))}
              </div>
            </PopoverContent>
          </Popover>

          {/* 🚀 Send Button */}
          <Button
            onClick={handleSend}
            disabled={!message.trim() && files.length === 0}
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
