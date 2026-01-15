import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background" style={{
      backgroundImage: 
        "radial-gradient(at 0% 0%, hsl(220 15% 10% / 0.3) 0px, transparent 50%), " +
        "radial-gradient(at 100% 100%, hsl(217 91% 60% / 0.05) 0px, transparent 50%)",
      backgroundAttachment: "fixed",
    }}>
      <div className="text-center">
        <div className="inline-block p-8 rounded-xl bg-black/50 backdrop-blur-md mb-6 border border-border/40">
          <h1 className="mb-4 text-6xl font-bold text-foreground drop-shadow-sm">404</h1>
        </div>
        <p className="mb-4 text-xl text-muted-foreground">Oops! Page not found</p>
        <a href="/" className="text-primary underline hover:text-primary/80 transition-smooth">
          Return to Home
        </a>
      </div>
    </div>
  );
};

export default NotFound;
