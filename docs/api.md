# API – Nassim Systems Agent  
Enterprise‑Grade Intelligence Orchestration Layer

## 1. Executive Summary
The `/api/ask` endpoint is the **central intelligence orchestrator** of the Nassim Systems Agent framework.  
It transforms raw user input into **structured, consultant‑grade reasoning**, leveraging a multi‑model architecture and a fully isolated client intelligence layer.

This API is engineered for:
- enterprise reliability  
- predictable behavior  
- multi‑tenant scalability  
- strict separation of concerns  
- high‑performance reasoning at global scale  

It is the backbone that enables agencies and consultants to deploy **high‑value AI agents** across multiple clients without modifying the core system.

---

## 2. High‑Level Responsibilities
The API performs five critical functions:

1. **Payload intake & validation**  
2. **Client intelligence loading**  
3. **Prompt construction (multi‑layered)**  
4. **Model orchestration (primary + fallback)**  
5. **Structured response formatting**  

Each step is designed to ensure **consistency, safety, and enterprise‑grade reasoning**.

---

## 3. Request Payload Structure
The widget sends a complete intelligence payload:

{
"message": "User message",
"history": [...],
"client": "client_name",
"context": "...",
"rules": "...",
"knowledge_base": "...",
"prompt_system": "...",
"style": "..."
}

Code

### Key Principles
- **No intelligence is stored server‑side.**  
  Everything is loaded dynamically from `/clients/<client>/`.
- **The backend never trusts the frontend.**  
  All fields are validated and sanitized.
- **History is trimmed** to maintain performance and avoid prompt inflation.

---

## 4. Internal Processing Pipeline (Enterprise‑Grade)

### **4.1 Step 1 — Payload Validation**
- required fields check  
- type validation  
- length limits  
- history trimming  
- sanitization of user input  

This ensures the system remains stable even under malformed or malicious requests.

---

### **4.2 Step 2 — Client Intelligence Loading**
The API loads the full intelligence profile for the selected client:

- system prompt  
- rules  
- knowledge base  
- context  
- style  

This enables **deep customization** without modifying backend logic.

---

### **4.3 Step 3 — Prompt Construction**
The final prompt is built using a **multi‑layered consultant‑grade structure**:

1. **System layer** → global behavior, reasoning style  
2. **Rules layer** → strict constraints, compliance boundaries  
3. **Context layer** → identity, mission, domain positioning  
4. **Knowledge layer** → domain‑specific information  
5. **Style layer** → tone, formatting, communication style  
6. **History layer** → trimmed conversation context  
7. **User message** → the actual query  

This layered approach ensures:
- predictable reasoning  
- consistent tone  
- domain‑aware answers  
- enterprise‑level reliability  

---

### **4.4 Step 4 — Model Orchestration**
The API uses a **dual‑model strategy**:

#### **Primary Model**
- **Claude 3 Opus**  
  - deep reasoning  
  - strategic analysis  
  - consultant‑grade output  

#### **Fallback Model**
- **GPT‑4.1‑mini**  
  - fast  
  - resilient  
  - cost‑efficient  

#### Orchestration Logic Includes:
- automatic fallback  
- error recovery  
- deterministic formatting  
- token usage tracking  
- latency optimization  

This ensures **zero downtime** and **consistent quality**.

---

### **4.5 Step 5 — Response Formatting**
The API returns a **clean, predictable, structured JSON**:

{
"answer": "Generated response",
"sources": [],
"tokens": {
"input": 0,
"output": 0
}
}

Code

### Guarantees:
- no hallucinated structure  
- consistent formatting  
- safe output  
- enterprise‑ready integration  

---

## 5. Security Architecture

### **5.1 Server‑Side Secrets**
- API keys are stored server‑side only  
- never exposed to the frontend  

### **5.2 Input Sanitization**
- removes unsafe patterns  
- trims excessive context  
- prevents injection attempts  

### **5.3 Multi‑Tenant Isolation**
Each client is fully isolated:
- no shared context  
- no shared knowledge  
- no cross‑contamination  

### **5.4 Controlled Output**
- deterministic formatting  
- safe response shaping  
- optional compliance filters  

---

## 6. Reliability & Resilience

- automatic fallback model  
- structured error handling  
- consistent JSON output  
- predictable behavior  
- optional logging for audits  
- zero cold starts (Edge runtime)  

This API is engineered for **enterprise deployments**, not hobby projects.

---

## 7. Why This API Architecture Sells at 20k–30k

- multi‑tenant by design  
- zero backend modification per client  
- consultant‑grade reasoning  
- enterprise reliability  
- predictable outputs  
- scalable to dozens or hundreds of clients  
- extremely fast (Edge)  
- clean separation of concerns  
- easy to maintain  
- perfect for agencies and consultants  

This API is the **core asset** that transforms your GitHub into a **high‑value AI product**.