import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { FeatureCard } from "@/components/FeatureCard";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Rocket, Shield, Check } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Brain,
      title: "Strategic Insights",
      description: "Get expert guidance on business strategy, market positioning, and competitive analysis from your AI co-founder."
    },
    {
      icon: Rocket,
      title: "Product Development",
      description: "From MVP to scale, receive actionable advice on product roadmaps, feature prioritization, and user experience."
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your conversations and business data are encrypted and never shared. Your secrets stay your secrets."
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Founder, TechFlow",
      quote: "Founder GPT helped me validate my product idea and create a go-to-market strategy in days, not months."
    },
    {
      name: "Marcus Rodriguez",
      role: "CEO, DataSync",
      quote: "Like having a co-founder who's available 24/7. The strategic insights are incredibly valuable."
    },
    {
      name: "Emily Watson",
      role: "Founder, GrowthLabs",
      quote: "The best investment I made in my startup journey. It's like YC office hours, but instant."
    }
  ];

  const pricingPlans = [
    {
      name: "Starter",
      price: "Free",
      description: "Perfect for validating your idea",
      features: ["100 messages/month", "Basic templates", "Community support", "Email insights"],
      cta: "Start Free"
    },
    {
      name: "Founder",
      price: "$29",
      description: "For serious entrepreneurs",
      features: ["Unlimited messages", "Advanced templates", "Priority support", "Project vault", "Usage analytics"],
      cta: "Start Trial",
      popular: true
    },
    {
      name: "Scale",
      price: "$99",
      description: "For growing teams",
      features: ["Everything in Founder", "Team collaboration", "Custom integrations", "Dedicated support", "API access"],
      cta: "Contact Sales"
    }
  ];

  return (
    <div className="min-h-screen bg-background" style={{
      backgroundImage: 
        "radial-gradient(at 0% 0%, hsl(220 15% 10% / 0.3) 0px, transparent 50%), " +
        "radial-gradient(at 100% 100%, hsl(217 91% 60% / 0.05) 0px, transparent 50%)",
      backgroundAttachment: "fixed",
    }}>
      <Navbar />
      <Hero />
      
      {/* Features Section */}
      <section className="py-24 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Everything You Need to <span className="gradient-text">Build & Scale</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Your AI co-founder provides expert guidance across every aspect of your startup journey
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div key={index} style={{ animationDelay: `${index * 0.1}s` }}>
                <FeatureCard {...feature} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-4 bg-transparent">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Trusted by <span className="gradient-text">Founders</span>
            </h2>
            <p className="text-xl text-muted-foreground">See what entrepreneurs are saying</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="p-6 bg-black/60 backdrop-blur-md border-border/40 shadow-elevated">
                <p className="text-foreground mb-4 leading-relaxed">"{testimonial.quote}"</p>
                <div>
                  <p className="font-semibold text-foreground">{testimonial.name}</p>
                  <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-24 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Simple, <span className="gradient-text">Transparent Pricing</span>
            </h2>
            <p className="text-xl text-muted-foreground">Choose the plan that fits your journey</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <Card 
                key={index} 
                className={`p-8 relative bg-black/60 backdrop-blur-md shadow-elevated ${plan.popular ? 'border-primary ring-2 ring-primary/20' : 'border-border/40'}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 gradient-primary rounded-full text-sm text-white font-medium">
                    Most Popular
                  </div>
                )}
                
                <div className="mb-6">
                  <h3 className="text-2xl font-bold mb-2 text-foreground">{plan.name}</h3>
                  <p className="text-muted-foreground text-sm mb-4">{plan.description}</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold gradient-text">{plan.price}</span>
                    {plan.price !== "Free" && <span className="text-muted-foreground">/month</span>}
                  </div>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Button 
                  onClick={() => navigate("/chat")}
                  className={`w-full ${plan.popular ? 'gradient-primary hover:opacity-90' : ''}`}
                  variant={plan.popular ? "default" : "outline"}
                >
                  {plan.cta}
                </Button>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-4">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <img src="/atman-logo.png" alt="ĀTMAN" className="w-16 h-16 object-contain" />
              <span className="text-xl font-bold golden-text">Founder GPT</span>
            </div>
            
            <div className="flex flex-wrap justify-center gap-6">
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-smooth">About</a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-smooth">Privacy</a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-smooth">Terms</a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-smooth">Contact</a>
            </div>
            
            <p className="text-sm text-muted-foreground">© 2024 Founder GPT. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
