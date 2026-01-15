# 📧 Message for Vercel Support

If you need to contact Vercel support, use this message:

---

**Subject:** Need OPTIONS Allowlist for CORS Preflight Requests

**Message:**

Hello Vercel Support,

I'm experiencing a CORS issue with my FastAPI serverless function deployment. OPTIONS preflight requests are being blocked by Deployment Protection before they reach my serverless function.

**Issue:**
- Backend URL: `https://founderai-workspace-backend-dc090ufif.vercel.app`
- OPTIONS requests to `/api/*` paths are blocked
- Error: "No 'Access-Control-Allow-Origin' header is present"
- The request fails completely (net::ERR_FAILED) before reaching the function

**What I need:**
- Enable OPTIONS Allowlist in Deployment Protection
- Allow OPTIONS requests to `/api/*` paths
- Or guidance on how to configure CORS for serverless functions with Deployment Protection enabled

**My setup:**
- FastAPI backend deployed as serverless functions
- CORS middleware configured in code
- Deployment Protection is enabled
- Cannot find "OPTIONS Allowlist" option in settings

**Vercel Plan:** [Your plan - Hobby/Pro/Enterprise]

Could you please help me enable OPTIONS Allowlist or provide an alternative solution?

Thank you!

---

**Copy this message and send to Vercel support if needed.**
