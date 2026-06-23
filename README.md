
# Nassim Systems Agent — AI Agent Framework for High‑End Integrations

A professional-grade AI agent framework engineered for consultants, automation experts, and companies seeking premium, scalable, and customizable intelligence systems.  
This repository provides a clean, modular, production-ready foundation for building and deploying specialized AI agents for clients.

---

## 🧭 Strategic Vision

Nassim Systems Agent is designed with a consultant mindset:

- modular architecture  
- client‑specific customization  
- clean separation of concerns  
- predictable behavior through rules & knowledge bases  
- deployable instantly on any website or SaaS  
- scalable for multiple clients without rewriting core logic  

This framework is built to **sell**, **deploy**, and **maintain** AI agents at a professional level.

---

## 🧱 Core Architecture

The system is structured around three pillars:

### 1. Backend Intelligence (Vercel /api/ask)
- receives: message, history, context, rules, knowledge base  
- applies deterministic business logic  
- ensures controlled, consistent responses  
- returns a clean JSON payload for the widget  

### 2. Frontend Widget (widget-v2.js)
- lightweight, embeddable chat widget  
- handles UI state (sending, waiting, errors)  
- loads client-specific files:  
  - prompt_system.txt  
  - rules.txt  
  - knowledge_base.txt  
  - style.txt  
- sends a complete, structured payload to the backend  

### 3. Client Context Layer (clients/)
Each client has its own intelligence profile:

- context.js  
- rules.txt  
- knowledge_base.txt  
- prompt_system.txt  
- style.txt  

This allows you to create **specialized agents** without touching the core engine.

---

## 📂 Project Structure

- `api/` → backend logic  
- `clients/` → client-specific intelligence modules  
- `widget-v2.js` → embeddable chat widget  
- `docs/` → technical documentation  
- `README.md` → main documentation  
- `package.json` → dependencies  
- `vercel.json` → deployment config  

---

## ⚙️ Installation & Deployment

### 1. Clone the repository
```bash
git clone https://github.com/nassim-systems/nassim-systems-agent.git
cd nassim-systems-agent

