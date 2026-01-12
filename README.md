# FounderGPT - AI Co-Founder Assistant

A powerful RAG (Retrieval-Augmented Generation) application with document management, chat interface, and smart conversation features.

## 📁 Project Structure

```
founder-ai-workspace/
├── src/                    # Frontend React/TypeScript application
├── rag-backend/            # FastAPI backend with RAG implementation
├── docs/                   # 📚 All project documentation
├── supabase/               # 🗄️ Database schemas and SQL scripts
└── README.md              # This file
```

## 🚀 Quick Links

- **[Documentation](./docs/)** - Comprehensive guides and architecture docs
- **[Supabase Setup](./supabase/)** - Database configuration and SQL scripts
- **[Backend Docs](./rag-backend/)** - API documentation and implementation guides

## Project info

**URL**: https://lovable.dev/projects/de6d5772-e3d2-44f3-904b-92dc7f5514ce

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/de6d5772-e3d2-44f3-904b-92dc7f5514ce) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

### Frontend
- **React** + **TypeScript** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn-ui** - UI components
- **React Router** - Navigation
- **Supabase** - Authentication & Database

### Backend
- **FastAPI** - Python web framework
- **Groq API** - LLM for AI responses
- **Sentence Transformers** - Text embeddings
- **Supabase** - PostgreSQL database with vector search
- **Clean Architecture** - Domain-driven design pattern

## How can I deploy this project?

### Option 1: Deploy via Lovable
Simply open [Lovable](https://lovable.dev/projects/de6d5772-e3d2-44f3-904b-92dc7f5514ce) and click on Share -> Publish.

### Option 2: Deploy to Vercel (Frontend) + Render (Backend)
For production deployment, see the comprehensive deployment guide:

- **[📘 Full Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Step-by-step instructions
- **[✅ Quick Checklist](./QUICK_DEPLOY_CHECKLIST.md)** - Deployment checklist

**Quick Start:**
1. Push code to GitHub
2. Deploy frontend to [Vercel](https://vercel.com)
3. Deploy backend to [Render](https://render.com)
4. Configure environment variables
5. Test your deployment

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
