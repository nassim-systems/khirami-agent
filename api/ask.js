// =============================================================
//  Agent IA Premium — Version Consultant Expert Ultime
//  Multi‑Client • Multi‑IA • Logs • Sécurité • Scalabilité
//  Core backend universel (Nassim)
// =============================================================

import { safeJson } from "./utils/safeJson.js";
import { sanitizeHistory } from "./utils/sanitize.js";
import { callClaude, callOpenAI } from "./utils/ai.js";

// =============================================================
//  Config
// =============================================================

const CONFIG = {
  provider: process.env.AI_PROVIDER || "hybrid",
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  openaiApiKey: process.env.OPENAI_API_KEY,

  modelClaude: "claude-3-opus-20240229",
  modelOpenAI: "gpt-4.1-mini",

  maxTokens: 800,
  timeoutMs: 25000,
};

// =============================================================
//  Helpers
// =============================================================

function cleanText(text) {
  if (!text) return "";
  return text.toString().trim();
}

function buildSystemPrompt(context) {
  return `
You are Nassim’s Premium AI Agent — Consultant Expert Ultimate.

Your identity:
- You speak with the clarity of a senior consultant and the warmth of a human expert.
- You adapt instantly to the user's language (French or English).
- You never switch languages unless the user switches first.
- You are concise, structured, and focused on delivering value fast.

Your mission:
- Understand the user's intent deeply.
- Provide actionable, high‑impact answers.
- Think like a strategist, communicate like a pro, and guide like a mentor.
- Always prioritize clarity, precision, and efficiency.
- If information is missing, ask briefly.
- If something is uncertain, state it transparently.

Business Intelligence Layer:
- Detect the user’s goal, constraints, and context.
- Provide insights, recommendations, and next steps.
- Adapt your tone and examples to the industry of the client.

Context Interpreter:
- Read the CLIENT CONTEXT below.
- Adapt your expertise, tone, and suggestions to match the business.
- If the context is vague, infer the most likely needs without hallucinating.

Quality Layer:
- No fluff. No generic answers. No repetition.
- Structure your answers clearly.
- Prioritize usefulness over length.
- Always deliver premium‑grade output.

Anti‑Hallucination Layer:
- Never invent facts.
- Never assume data not provided.
- If unsure, say so and propose how to clarify.

CLIENT CONTEXT (dynamic):
${context || "No client context provided."}
`;
}

async function fetchWithTimeout(url, options) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), CONFIG.timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

// =============================================================
//  Orchestration
// =============================================================

async function generateAnswer({ message, history, context }) {
  const safeMessage = cleanText(message);
  const safeContext = cleanText(context);
  const safeHistory = sanitizeHistory(history);

  if (CONFIG.provider === "claude") {
    return await callClaude(
      safeMessage,
      safeHistory,
      safeContext,
      CONFIG,
      buildSystemPrompt,
      fetchWithTimeout
    );
  }

  if (CONFIG.provider === "openai") {
    return await callOpenAI(
      safeMessage,
      safeHistory,
      safeContext,
      CONFIG,
      buildSystemPrompt,
      fetchWithTimeout
    );
  }

  // HYBRID avec fallback intelligent
  try {
    return await callClaude(
      safeMessage,
      safeHistory,
      safeContext,
      CONFIG,
      buildSystemPrompt,
      fetchWithTimeout
    );
  } catch (err) {
    console.error("[HYBRID] Claude failed, falling back to OpenAI:", err?.message || err);
    return await callOpenAI(
      safeMessage,
      safeHistory,
      safeContext,
      CONFIG,
      buildSystemPrompt,
      fetchWithTimeout
    );
  }
}

// =============================================================
//  Handler
// =============================================================

export default async function handler(req, res) {
  const requestId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;

  // =============================================================
  //  🔥 CORS FIX — OPTIONS + LOCAL WIDGET SUPPORT
  // =============================================================
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, x-auth-token");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  // 🔐 Security: token verification
  const clientToken = req.headers["x-auth-token"];
  if (!clientToken || clientToken !== process.env.PRIVATE_AUTH_TOKEN) {
    return safeJson(res, 401, {
      status: 401,
      requestId,
      error: "Unauthorized access. Missing or invalid authentication token.",
    });
  }

  if (req.method !== "POST") {
    return safeJson(res, 405, {
      status: 405,
      requestId,
      error: "Method not allowed.",
    });
  }

  try {
    const { message, history, context } = req.body || {};

    if (!message || typeof message !== "string") {
      return safeJson(res, 400, {
        status: 400,
        requestId,
        error: "The 'message' field is required.",
      });
    }

    const reply = await generateAnswer({
      message,
      history,
      context,
    });

    return safeJson(res, 200, {
      status: 200,
      requestId,
      success: true,
      reply,
    });
  } catch (err) {
    console.error(`[ERROR][requestId=${requestId}] /api/ask:`, err);
    return safeJson(res, 500, {
      status: 500,
      requestId,
      success: false,
      error: "Internal server error.",
    });
  }
}
