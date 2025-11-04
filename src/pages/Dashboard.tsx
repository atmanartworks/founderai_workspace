import { Navbar } from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Folder, MessageSquare, TrendingUp, Key, Plus, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const navigate = useNavigate();

  const usageData = [
    { name: "Mon", messages: 45 },
    { name: "Tue", messages: 52 },
    { name: "Wed", messages: 38 },
    { name: "Thu", messages: 65 },
    { name: "Fri", messages: 48 },
    { name: "Sat", messages: 30 },
    { name: "Sun", messages: 25 },
  ];

  const projects = [
    { name: "SaaS MVP", status: "Active", lastActive: "2 hours ago" },
    { name: "Market Research", status: "Active", lastActive: "1 day ago" },
    { name: "Fundraising Prep", status: "Completed", lastActive: "3 days ago" },
  ];

  const recentChats = [
    { title: "Product Strategy Discussion", time: "2 hours ago", messages: 15 },
    { title: "Go-to-Market Planning", time: "1 day ago", messages: 23 },
    { title: "Competitive Analysis", time: "2 days ago", messages: 18 },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">Track your startup journey and insights</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 bg-card border-border">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Active Projects</h3>
              <Folder className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold gradient-text">3</p>
            <p className="text-xs text-muted-foreground mt-2">+1 from last week</p>
          </Card>

          <Card className="p-6 bg-card border-border">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Messages This Week</h3>
              <MessageSquare className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold gradient-text">303</p>
            <p className="text-xs text-muted-foreground mt-2">+12% from last week</p>
          </Card>

          <Card className="p-6 bg-card border-border">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Insights Gained</h3>
              <TrendingUp className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold gradient-text">47</p>
            <p className="text-xs text-muted-foreground mt-2">Across all projects</p>
          </Card>

          <Card className="p-6 bg-card border-border">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Vault Keys</h3>
              <Key className="w-5 h-5 text-primary" />
            </div>
            <p className="text-3xl font-bold gradient-text">5</p>
            <p className="text-xs text-muted-foreground mt-2">Secured secrets</p>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Usage Chart */}
          <Card className="lg:col-span-2 p-6 bg-card border-border">
            <h2 className="text-lg font-semibold mb-4">Weekly Usage</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis 
                  dataKey="name" 
                  stroke="hsl(var(--muted-foreground))"
                  tick={{ fill: 'hsl(var(--muted-foreground))' }}
                />
                <YAxis 
                  stroke="hsl(var(--muted-foreground))"
                  tick={{ fill: 'hsl(var(--muted-foreground))' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="messages" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Recent Chats */}
          <Card className="p-6 bg-card border-border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Recent Chats</h2>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate("/chat")}
              >
                View All
              </Button>
            </div>
            <div className="space-y-3">
              {recentChats.map((chat, index) => (
                <div 
                  key={index}
                  onClick={() => navigate("/chat")}
                  className="p-3 rounded-lg bg-background border border-border hover:border-primary/50 transition-smooth cursor-pointer"
                >
                  <h3 className="text-sm font-medium mb-1">{chat.title}</h3>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{chat.time}</span>
                    <span>{chat.messages} messages</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Active Projects */}
        <Card className="p-6 bg-card border-border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Active Projects</h2>
            <Button className="gradient-primary hover:opacity-90 transition-smooth">
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((project, index) => (
              <div 
                key={index}
                onClick={() => navigate("/chat")}
                className="p-4 rounded-xl bg-background border border-border hover:border-primary/50 transition-smooth cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg gradient-primary flex items-center justify-center group-hover:glow-primary transition-smooth">
                    <Folder className="w-5 h-5 text-white" />
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    project.status === "Active" 
                      ? "bg-primary/10 text-primary" 
                      : "bg-muted text-muted-foreground"
                  }`}>
                    {project.status}
                  </span>
                </div>
                
                <h3 className="font-semibold mb-1">{project.name}</h3>
                <p className="text-sm text-muted-foreground mb-3">Last active {project.lastActive}</p>
                
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="w-full group-hover:bg-primary/10 transition-smooth"
                >
                  Open Project
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-smooth" />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
