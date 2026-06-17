import { CLIENT_CONTEXT } from "./context.js";

async function send() {
  const message = document.getElementById("msg").value;

  const res = await fetch("https://agent-premium-nassim.vercel.app/api/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-auth-token": "NX-UltimateAgent-2026_Z9FA7!"
    },
    body: JSON.stringify({
      message,
      history: [],
      context: CLIENT_CONTEXT
    })
  });

  const data = await res.json();
  document.getElementById("output").textContent = data.reply;
}

// 🔥 LIGNE QUI MANQUAIT POUR QUE LE BOUTON MARCHE
document.getElementById("sendBtn").addEventListener("click", send);