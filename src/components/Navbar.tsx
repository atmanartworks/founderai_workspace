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
    <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div onClick={() => navigate("/")} className="flex items-center gap-3 cursor-pointer group">
            <img src="/atman-logo.png" alt="ĀTMAN" className="w-16 h-16 object-contain group-hover:scale-110 transition-smooth" />
            <span className="text-xl font-bold golden-text">Founder GPT</span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className="text-sm text-muted-foreground hover:text-foreground transition-smooth"
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
            <SheetContent side="right" className="w-[300px] bg-card border-border">
              <div className="flex flex-col gap-6 mt-8">
                {navItems.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => {
                      navigate(item.path);
                      setIsOpen(false);
                    }}
                    className="text-left text-lg text-muted-foreground hover:text-foreground transition-smooth"
                  >
                    {item.label}
                  </button>
                ))}
                <div className="flex flex-col gap-3 pt-6 border-t border-border">
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
                    className="gradient-primary hover:opacity-90 transition-smooth w-full"
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
