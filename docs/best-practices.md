# Best Practices – Nassim Systems Agent  
Enterprise‑Grade Standards for High‑Value AI Deployments

## 1. Purpose of This Document
This guide defines the **operational best practices** required to maintain a stable, predictable, and enterprise‑grade AI agent across multiple clients.

It ensures:
- consistent consultant‑level output  
- safe and compliant behavior  
- scalable multi‑tenant operations  
- predictable performance  
- long‑term maintainability  

These best practices are modeled after the standards used by **top consulting firms and enterprise AI teams**.

---

# 2. Prompt Engineering Best Practices

## 2.1 Use Layered Prompting
Always rely on the five‑layer architecture:
1. System prompt  
2. Rules  
3. Context  
4. Knowledge base  
5. Style  

This ensures:
- deterministic reasoning  
- consistent tone  
- domain‑aware answers  

---

## 2.2 Keep Rules Strict and Explicit
Rules must be:
- unambiguous  
- non‑negotiable  
- easy to audit  
- aligned with client constraints  

Rules override all other layers.

---

## 2.3 Keep Knowledge Factual and Updated
The knowledge base must:
- reflect real client information  
- avoid speculation  
- be updated regularly  
- stay concise and structured  

This reduces hallucinations and ensures accuracy.

---

# 3. Client Management Best Practices

## 3.1 One Folder = One Client
Never mix client data.  
Each client must have:

```text
/clients/<client_name>/
```

This guarantees:
- isolation  
- security  
- predictable behavior  
- easy maintenance  

---

## 3.2 Use the Template for Every New Client
Always start from:

```text
/client-template/
```

This ensures:
- consistent structure  
- no missing files  
- faster onboarding  

---

## 3.3 Keep Style Consistent With the Client’s Brand
The `style.txt` file must reflect:
- tone  
- vocabulary  
- formatting  
- brand personality  

This ensures the agent **sounds like the client**, not like a generic AI.

---

# 4. Knowledge Base Best Practices

## 4.1 Structure Knowledge Clearly
Recommended sections:
- Company overview  
- Products & services  
- Processes  
- FAQs  
- Industry insights  

---

## 4.2 Avoid Overloading the Knowledge Base
Do NOT include:
- irrelevant details  
- outdated information  
- unverified claims  
- long paragraphs  

Keep it:
- concise  
- factual  
- structured  

---

## 4.3 Update Knowledge Regularly
Review and update:
- product changes  
- new processes  
- updated policies  
- new FAQs  

This keeps the agent aligned with the client’s reality.

---

# 5. API & Backend Best Practices

## 5.1 Never Modify the Core Engine for a Client
The backend must remain:
- stable  
- identical for all clients  
- predictable  

All customization happens in `/clients/<client_name>/`.

---

## 5.2 Validate and Sanitize All Inputs
Always ensure:
- required fields exist  
- history is trimmed  
- user input is sanitized  

This protects the system from malformed or malicious requests.

---

## 5.3 Use Model Fallbacks for Reliability
Primary model: **Claude 3 Opus**  
Fallback model: **GPT‑4.1‑mini**

This ensures:
- zero downtime  
- consistent quality  
- enterprise reliability  

---

# 6. Widget & Frontend Best Practices

## 6.1 Keep the Widget Lightweight
Avoid:
- unnecessary scripts  
- heavy assets  
- blocking operations  

The widget must remain fast and frictionless.

---

## 6.2 Use Clear Placeholders and Branding
Example:

```js
placeholder: "Ask our AI consultant…"
```

This improves user experience and adoption.

---

## 6.3 Maintain Local History Responsibly
History should:
- stay local  
- be trimmed  
- never expose sensitive data  

---

# 7. Operational Best Practices

## 7.1 Test Each Client Before Deployment
Checklist:
- rules validated  
- knowledge accurate  
- style aligned  
- context correct  
- widget configured  

---

## 7.2 Monitor Real Usage
Track:
- common questions  
- failure patterns  
- missing knowledge  
- tone consistency  

Use this to refine the client’s intelligence profile.

---

## 7.3 Iterate Continuously
Enterprise AI is iterative.  
Refine:
- rules  
- knowledge  
- style  
- context  

This ensures long‑term value.

---

# 8. Why These Best Practices Sell at 20k–30k

- enterprise‑grade methodology  
- predictable consultant‑level reasoning  
- scalable multi‑client architecture  
- strict separation of concerns  
- safe and compliant behavior  
- premium documentation and structure  
- professional onboarding workflow  

These best practices elevate Nassim Systems Agent from a simple chatbot to a **high‑value AI consulting platform**.
