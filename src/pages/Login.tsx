import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().trim().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

const Login = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        navigate("/chat");
      }
    };
    checkAuth();
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const validatedData = loginSchema.parse(formData);

      const { data, error } = await supabase.auth.signInWithPassword({
        email: validatedData.email,
        password: validatedData.password,
      });

      if (error) {
        if (error.message.includes("Invalid login credentials")) {
          toast({
            title: "Error",
            description: "Invalid email or password. Please try again.",
            variant: "destructive",
          });
        } else {
          toast({
            title: "Error",
            description: error.message,
            variant: "destructive",
          });
        }
        return;
      }

      if (data.session) {
        toast({
          title: "Success",
          description: "Logged in successfully!",
        });
        navigate("/chat");
      }
    } catch (error) {
      if (error instanceof z.ZodError) {
        toast({
          title: "Validation Error",
          description: error.errors[0].message,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Error",
          description: "An unexpected error occurred. Please try again.",
          variant: "destructive",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4" style={{
      backgroundImage: 
        "radial-gradient(at 0% 0%, hsl(220 15% 10% / 0.3) 0px, transparent 50%), " +
        "radial-gradient(at 100% 100%, hsl(217 91% 60% / 0.05) 0px, transparent 50%)",
      backgroundAttachment: "fixed",
    }}>
      <Card className="w-full max-w-md p-6 sm:p-8 bg-black/60 backdrop-blur-md border-border/40 shadow-elevated mx-4 sm:mx-auto">
        <div className="flex flex-col items-center mb-8">
          <img src="/atman-logo.png" alt="ĀTMAN" className="w-32 h-32 object-contain mb-6" />
          <h1 className="text-3xl font-bold golden-text">Founder GPT</h1>
          <p className="text-muted-foreground mt-2">Welcome back</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="bg-black/40 backdrop-blur-sm border-border/40"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="bg-black/40 backdrop-blur-sm border-border/40"
            />
          </div>

          <div className="flex justify-end mb-2">
            <button
              type="button"
              onClick={() => navigate("/reset-password")}
              className="text-sm text-primary hover:underline"
            >
              Forgot Password?
            </button>
          </div>

          <Button 
            type="submit" 
            className="w-full gradient-primary hover:opacity-90"
            disabled={isLoading}
          >
            {isLoading ? "Logging in..." : "Log In"}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Don't have an account?{" "}
            <button
              onClick={() => navigate("/signup")}
              className="text-primary hover:underline font-medium"
            >
              Sign Up
            </button>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Login;
