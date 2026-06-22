# 🚀 Premium AI Automation Agent — Enterprise‑Grade Architecture & Hybrid Intelligence

This repository showcases **Nassim’s Premium AI Automation Agent**, engineered with the standards, clarity, and reliability expected from a **senior AI consultant** working with founders, SaaS teams, and high‑growth businesses.

The system is built on **Vercel Edge Runtime** for ultra‑low latency, global scalability, and instant cold starts.  
It leverages a **hybrid intelligence engine** combining **Claude 3 Opus** (primary reasoning) and **GPT‑4.1‑mini** (fallback), orchestrated through a clean, secure, and predictable API layer.

This agent is not a “chatbot”.  
It is a **consultant‑grade reasoning engine** designed to deliver structured, actionable, high‑impact answers.

---

## 🧠 Core Value Proposition
This agent is designed to behave like a **senior consultant**:

- Understands context deeply  
- Communicates with clarity and structure  
- Produces high‑impact, business‑oriented insights  
- Adapts instantly to French or English  
- Never hallucinates silently — it warns and proposes clarification  
- Maintains a premium, calm, expert tone  

It is built for **real operational use**, not demos.

---

## 🏗️ Architecture Overview
**Runtime:** Vercel Edge (Web APIs, no Node dependency)  
**Models:**  
- **Claude 3 Opus** — strategic reasoning, deep analysis  
- **GPT‑4.1‑mini** — fast fallback for resilience  

**Key Components:**  
- Hybrid AI orchestration  
- Intelligent fallback logic  
- Structured JSON logging  
- Context sanitization  
- History trimming  
- Secure private token authentication  
- CORS‑safe API gateway  
- Error‑safe execution flow  

This architecture ensures **speed, reliability, and predictable output**.

---

## 📦 Project Structure
```
/api
  └── ask.js        # Main Edge Runtime handler (premium agent logic)
package.json        # Dependencies + scripts
vercel.json         # Routing configuration
```

---

## 🔧 How the Agent Works
1. Receives:
   - message  
   - optional history  
   - optional business context  
   - private auth token  

2. Cleans + validates input  
3. Builds a **consultant‑grade system prompt**  
4. Calls Claude (primary)  
5. Falls back to OpenAI if needed  
6. Logs everything in structured JSON  
7. Returns a clean, predictable JSON response  

This ensures **consistency**, **traceability**, and **premium‑grade output**.

---

## 🔐 Security & Reliability
- Private token required (`x-auth-token`)  
- No execution without valid credentials  
- Sanitized history  
- Strict error handling  
- No uncontrolled model output  
- Fully compatible with Edge Runtime constraints  

---

## 🛠️ Local Development
```
npm install
npm run dev
```

Create a `.env` file:

```
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
PRIVATE_AUTH_TOKEN=your_private_token
AI_PROVIDER=hybrid
```

---

## 🌍 Deployment on Vercel
This project is optimized for **Vercel Edge Runtime**.

Your routing config:

```json
{
  "version": 2,
  "routes": [
    { "src": "/api/ask", "dest": "/api/ask.js" }
  ]
}
```

No Node version is required — the agent runs fully on **Edge Runtime**.

---

## 🧪 Example Request
```bash
curl -X POST https://your-domain.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -H "x-auth-token: YOUR_PRIVATE_TOKEN" \
  -d '{
    "message": "How can I optimize my operations?",
    "context": "Small SaaS team",
    "history": []
  }'
```

---

## 👤 About Nassim — AI Automation Consultant
Nassim builds **practical, reliable, and business‑focused AI systems** for founders, SaaS teams, e‑commerce brands, and agencies.

His work combines:

- strategic thinking  
- clean architecture  
- operational impact  
- premium communication  
- automation expertise  

This agent is part of his **consultant‑grade automation toolkit**, used to help clients remove repetitive work, scale operations, and unlock new capabilities through AI.

---
