// Update this page (the content is just a fallback if you fail to update the page)

const Index = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background" style={{
      backgroundImage: 
        "radial-gradient(at 0% 0%, hsl(220 15% 10% / 0.3) 0px, transparent 50%), " +
        "radial-gradient(at 100% 100%, hsl(217 91% 60% / 0.05) 0px, transparent 50%)",
      backgroundAttachment: "fixed",
    }}>
      <div className="text-center">
        <div className="inline-block p-8 rounded-xl bg-black/50 backdrop-blur-md mb-6 border border-border/40">
          <h1 className="mb-4 text-4xl font-bold text-foreground drop-shadow-sm">Welcome to Your Blank App</h1>
        </div>
        <p className="text-xl text-muted-foreground">Start building your amazing project here!</p>
      </div>
    </div>
  );
};

export default Index;
