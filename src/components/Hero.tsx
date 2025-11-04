import { Button } from "./ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ChatBubble } from "./ChatBubble";

export const Hero = () => {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-[90vh] flex items-center">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none" />
      
      <div className="container mx-auto px-4 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8 animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-foreground">AI-Powered Co-Founder Assistant</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight">
              Your AI Co-Founder for{" "}
              <span className="gradient-text">Everything Startup</span>
            </h1>
            
            <p className="text-xl text-muted-foreground leading-relaxed max-w-xl">
              From ideation to execution, get instant expert guidance on strategy, product, growth, and everything in between.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                onClick={() => navigate("/chat")}
                size="lg"
                className="gradient-primary hover:opacity-90 transition-smooth text-base group"
              >
                Start for Free
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-smooth" />
              </Button>
              
              <Button 
                onClick={() => navigate("/dashboard")}
                variant="outline" 
                size="lg"
                className="text-base border-border hover:border-primary/50 transition-smooth"
              >
                View Demo
              </Button>
            </div>
          </div>
          
          <div className="bg-card border border-border rounded-2xl p-6 space-y-4 animate-fade-in" style={{ animationDelay: "0.2s" }}>
            <div className="flex items-center gap-2 mb-6">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-sm text-muted-foreground">Live Preview</span>
            </div>
            
            <ChatBubble 
              message="What's the best go-to-market strategy for a B2B SaaS product?"
              isAI={false}
            />
            
            <ChatBubble 
              message="For a B2B SaaS product, I'd recommend a product-led growth strategy combined with strategic outbound sales. Start with a freemium model to lower adoption barriers, focus on SEO and content marketing to attract organic traffic, and leverage customer success stories for social proof. Would you like me to break down each component?"
              isAI={true}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
