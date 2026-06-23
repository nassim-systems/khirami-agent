# Client Setup – Nassim Systems Agent  
Enterprise‑Grade Multi‑Client Configuration

## 1. Purpose of the Client Layer
The client layer is where each customer gets their **own dedicated intelligence profile** without ever touching the core engine.

This design allows you to:
- onboard new clients in minutes  
- customize behavior deeply per client  
- keep the backend stable and identical for everyone  
- scale to dozens or hundreds of clients cleanly  

Every client lives in its own folder under:

`/clients/<client_name>/`

---

## 2. Client Folder Structure

A typical client folder looks like this:

```text
/clients/<client_name>/
  ├─ context.js
  ├─ prompt_system.txt
  ├─ rules.txt
  ├─ knowledge_base.txt
  └─ style.txt
```

Each file has a very specific role:

- **context.js** → defines identity, role, mission, positioning  
- **prompt_system.txt** → defines global behavior and reasoning style  
- **rules.txt** → defines strict constraints and boundaries  
- **knowledge_base.txt** → defines domain‑specific information  
- **style.txt** → defines tone, voice, and formatting  

Together, they form the **client’s intelligence profile**.

---

## 3. Creating a New Client (Step‑by‑Step)

### **Step 1 — Duplicate the Template**

Start from the base template:

```text
/client-template/
```

Copy it into the clients directory:

```text
/clients/<client_name>/
```

Example:

```text
/clients/acme-corp/
```

---

### **Step 2 — Configure `context.js`**
In `context.js`, you define:

- who the agent is  
- who it serves  
- what its mission is  
- what it must always prioritize  

This makes the agent feel like a **dedicated consultant** for that client.

---

### **Step 3 — Configure `prompt_system.txt`**
In `prompt_system.txt`, you define:

- global behavior  
- reasoning style  
- decision‑making patterns  
- formatting expectations  

This ensures the agent behaves like a **senior advisor**, not a generic chatbot.

---

### **Step 4 — Configure `rules.txt`**
In `rules.txt`, you define **hard constraints**:

- what the agent must never do  
- what topics are off‑limits  
- compliance and legal boundaries  
- tone and brand boundaries  

This is critical for **enterprise and regulated environments**.

---

### **Step 5 — Configure `knowledge_base.txt`**
In `knowledge_base.txt`, you add:

- product information  
- services  
- processes  
- FAQs  
- internal policies  
- domain‑specific insights  

This is what makes the agent **actually useful** for that client’s business.

---

### **Step 6 — Configure `style.txt`**
In `style.txt`, you define:

- tone (formal, friendly, expert, etc.)  
- voice (brand personality)  
- formatting (bullets, sections, summaries)  

This ensures the agent **sounds like the client’s brand**, not like a generic AI.

---

## 4. Connecting the Client to the Widget

To activate a specific client, set the `client` field in the widget configuration:

```js
window.NassimAgentConfig = {
  client: "acme-corp",
  theme: "dark",
  position: "bottom-right",
  placeholder: "Ask our AI consultant…",
};
```

No backend change.  
No redeploy.  
No code modification.

Just a **configuration switch**.

---

## 5. Onboarding Workflow for New Clients

A recommended onboarding flow:

1. Create `/clients/<client_name>/` from the template  
2. Fill in:  
   - context  
   - system prompt  
   - rules  
   - knowledge base  
   - style  
3. Test internally using the widget  
4. Refine rules and knowledge  
5. Deploy on the client’s website  
6. Iterate based on real usage  

This is the exact workflow used by **agencies and consultants** to deliver high‑value AI agents.

---

## 6. Why This Client Setup Sells at 20k–30k

- clear separation between engine and client logic  
- scalable multi‑tenant architecture  
- deep customization without backend changes  
- fast onboarding for new clients  
- enterprise‑ready structure  
- perfect for agencies managing multiple accounts  

This client setup is what turns Nassim Systems Agent into a **real agency‑grade AI platform**, not just a chatbot.
