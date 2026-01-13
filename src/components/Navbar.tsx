import { Button } from "./ui/button";
import { Menu } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";

export const Navbar = () => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { label: "Vault", path: "/dashboard" },
    { label: "Chat", path: "/chat" },
    { label: "Logs", path: "/logs" },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-background/70 backdrop-blur-xl border-b border-border/30 glass highlight-top">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div onClick={() => navigate("/")} className="flex items-center gap-3 cursor-pointer group">
            <div className="relative">
              <img src="/atman-logo.png" alt="ĀTMAN" className="w-16 h-16 object-contain group-hover:scale-105 transition-smooth" />
              <div className="absolute inset-0 bg-primary/10 blur-xl rounded-full -z-10 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <span className="text-xl font-semibold golden-text">Founder GPT</span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className="text-sm text-muted-foreground hover:text-foreground transition-smooth px-3 py-1.5 rounded-lg hover:bg-accent/30"
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            {/* <Button 
              variant="ghost"
              onClick={() => navigate("/chat")}
            >
              Sign In
            </Button> */}
            {/* <Button 
              onClick={() => navigate("/chat")}
              className="gradient-primary hover:opacity-90 transition-smooth"
            >
              Get Started
            </Button> */}
          </div>

          {/* Mobile Menu */}
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon">
                <Menu className="w-6 h-6" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] bg-card/90 backdrop-blur-xl border-border/30 glass-card">
              <div className="flex flex-col gap-6 mt-8">
                {navItems.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => {
                      navigate(item.path);
                      setIsOpen(false);
                    }}
                    className="text-left text-lg text-muted-foreground hover:text-foreground transition-smooth px-3 py-2 rounded-lg hover:bg-accent/30"
                  >
                    {item.label}
                  </button>
                ))}
                <div className="flex flex-col gap-3 pt-6 border-t border-border/30">
                  <Button
                    variant="outline"
                    onClick={() => {
                      navigate("/chat");
                      setIsOpen(false);
                    }}
                    className="w-full"
                  >
                    Sign In
                  </Button>
                  <Button
                    onClick={() => {
                      navigate("/chat");
                      setIsOpen(false);
                    }}
                    className="gradient-primary hover:opacity-90 transition-smooth w-full glow-hover"
                  >
                    Get Started
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  );
};
