# Widget – Nassim Systems Agent

## 1. Purpose of the Widget
The widget is the user-facing interface that connects the end-user to the intelligence engine.  
It is designed to be:
- lightweight  
- fast  
- easy to integrate  
- fully customizable  
- compatible with any website (HTML, React, Next.js, Shopify, Webflow, etc.)

It handles:
- UI rendering  
- sending messages  
- local history management  
- loading/error states  
- communication with the `/api/ask` endpoint  

---

## 2. Basic Integration (copy–paste)
The widget can be added to any website with a single script tag:

```html
<script src="https://cdn.nassim-systems.com/widget-v2.js" defer></script>
Then add the anchor element:

html
<div id="nassim-agent"></div>
The widget loads automatically.

3. Configuration Options
The widget accepts a simple global configuration:

js
window.NassimAgentConfig = {
  client: "default",
  theme: "dark",
  position: "bottom-right",
  placeholder: "Ask me anything…",
};
Available options:

client → name of the client folder

theme → light, dark, or custom

position → bottom-right, bottom-left, floating

placeholder → input placeholder text

4. Internal Workflow
a) Initialization
injects HTML

applies theme

loads configuration

initializes local history

b) Sending a Message
The widget sends the following payload:

Code
{
  message,
  history,
  client,
  context,
  rules,
  knowledge_base,
  prompt_system,
  style
}
c) Receiving the Response
parses JSON

displays the answer (streaming optional)

updates local history

5. Security
no API keys exposed in the frontend

no sensitive data stored

history stored locally only

HTTPS communication enforced

6. Advantages
installs in under 10 seconds

works on any website

extremely lightweight

fully customizable

perfect for non-technical clients