import { LucideIcon } from "lucide-react";
import { Card } from "./ui/card";

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export const FeatureCard = ({ icon: Icon, title, description }: FeatureCardProps) => {
  return (
    <Card className="p-6 bg-black/60 backdrop-blur-md border-border/40 hover:border-primary/50 transition-smooth group shadow-elevated">
      <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-4 group-hover:glow-primary transition-smooth">
        <Icon className="w-6 h-6 text-white" />
      </div>
      <h3 className="text-lg font-semibold mb-2 text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
    </Card>
  );
};
