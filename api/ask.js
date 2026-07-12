// =============================================================
//  Agent IA Premium — Version Consultant Expert Ultime V7 (KHIRAMI)
//  Node 24 • Edge Runtime • Multi‑IA • Sécurité • Logs Pro
// =============================================================

export const config = {
  runtime: "edge"
};

// =============================================================
//  Config centrale (facile à tuner)
// =============================================================

const CONFIG = {
  provider: process.env.AI_PROVIDER || "hybrid",
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  openaiApiKey: process.env.OPENAI_API_KEY,

  modelClaude: "claude-3-opus-20240229",
  modelOpenAI: "gpt-4.1-mini",

  maxTokens: 800,
  maxHistoryItems: 20,
  maxMessageLength: 4000,
  enableLogging: true
};

// =============================================================
//  Helpers Premium
// =============================================================

function createRequestId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function log(level, message, meta = {}) {
  if (!CONFIG.enableLogging) return;
  console.log(JSON.stringify({
    level,
    message,
    ...meta,
    timestamp: new Date().toISOString()
  }));
}

function safeJson(status, data) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}

function sanitizeHistory(history) {
  if (!Array.isArray(history)) return [];
  return history
    .filter(item => typeof item === "string" && item.trim().length > 0)
    .slice(-CONFIG.maxHistoryItems);
}

function cleanText(text) {
  if (!text) return "";
  return text.toString().trim();
}

// =============================================================
//  System Prompt Premium — KHIRAMI AGENT V7
// =============================================================

function buildSystemPrompt(context) {
  return `
You are KHIRAMI AGENT — an enterprise-grade autonomous AI consultant and execution engine.

IDENTITY:
- You speak as a calm, sharp, high-end AI consultant.
- You adapt instantly to the user's language (French or English).
- You deliver structured, premium-grade, high-impact answers.
- You think clearly, strategically, and autonomously.

CORE ROLE:
You combine two modes:
1) CONSULTANT — analyze, diagnose, structure, strategize.
2) AGENT — plan, decide, execute workflows and actions.

WORKFLOW ENGINE (ALWAYS FOLLOW INTERNALLY):
1) CONTEXT — Identify the user’s goal, constraints, and environment.
2) DIAGNOSIS — Analyze the situation like a senior consultant.
3) PLAN — Propose a clear, ordered plan (strategy + execution).
4) EXECUTION — Start executing directly (generate, write, simulate).
5) REVIEW — Check coherence, refine once.
6) SUMMARY — End with a sharp recap + next steps.

STYLE:
- Tone: premium, calm, confident.
- Structure: sections, bullets, clarity.
- Length: enough to be useful, never bloated.
- Tailored answers, no generic fluff.

ENTERPRISE FOCUS:
- Think in KPIs, value delivery, risk management, scalability, governance.
- Connect actions to business impact.

WHEN USER ASKS FOR “AGENT” OR “AUTONOMOUS”:
- Show steps, decisions, branches.
- Behave like an internal operations brain.

WHEN USER IS LOST:
- Slow down.
- Reframe in 2–3 sentences.
- Propose 1 clear next move.

LIMITS:
- Do not invent access to real systems.
- Simulate responsibly.
- No vague motivational talk.

CLIENT CONTEXT:
${context || "No client context provided."}

You are KHIRAMI AGENT V7.
Your job: turn messy goals into clear, executable, high-value workflows and outputs.
`;
}

// =============================================================
//  IA Calls Premium (OpenAI + Claude)
// =============================================================

async function callOpenAI(message, history, context, config, requestId) {
  const body = {
    model: config.modelOpenAI,
    messages: [
      { role: "system", content: buildSystemPrompt(context) },
      ...history.map(h => ({ role: "user", content: h })),
      { role: "user", content: message }
    ],
    max_tokens: config.maxTokens
  };

  log("info", "Calling OpenAI", { requestId, model: config.modelOpenAI });

  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.openaiApiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  const json = await res.json();

  if (!res.ok) {
    log("error", "OpenAI API error", { requestId, status: res.status, body: json });
    throw new Error("OpenAI API error");
  }

  const reply = json.choices?.[0]?.message?.content || "No response.";
  log("info", "OpenAI reply received", { requestId });
  return reply;
}

async function callClaude(message, history, context, config, requestId) {
  const body = {
    model: config.modelClaude,
    max_tokens: config.maxTokens,
    messages: [
      { role: "system", content: buildSystemPrompt(context) },
      ...history.map(h => ({ role: "user", content: h })),
      { role: "user", content: message }
    ]
  };

  log("info", "Calling Claude", { requestId, model: config.modelClaude });

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": config.anthropicApiKey,
      "anthropic-version": "2023-06-01",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  const json = await res.json();

  if (!res.ok) {
    log("error", "Claude API error", { requestId, status: res.status, body: json });
    throw new Error("Claude API error");
  }

  const reply = json.content?.[0]?.text || "No response.";
  log("info", "Claude reply received", { requestId });
  return reply;
}

// =============================================================
//  Orchestration Premium
// =============================================================

async function generateAnswer({ message, history, context, requestId }) {
  const safeMessage = cleanText(message);
  const safeContext = cleanText(context);
  const safeHistory = sanitizeHistory(history);

  if (!safeMessage || safeMessage.length === 0) {
    throw new Error("Empty message.");
  }

  if (safeMessage.length > CONFIG.maxMessageLength) {
    throw new Error("Message too long.");
  }

  log("info", "Generating answer", {
    requestId,
    provider: CONFIG.provider,
    historyLength: safeHistory.length
  });

  if (CONFIG.provider === "claude") {
    return await callClaude(safeMessage, safeHistory, safeContext, CONFIG, requestId);
  }

  if (CONFIG.provider === "openai") {
    return await callOpenAI(safeMessage, safeHistory, safeContext, CONFIG, requestId);
  }

  try {
    return await callClaude(safeMessage, safeHistory, safeContext, CONFIG, requestId);
  } catch (err) {
    log("warn", "Claude failed, falling back to OpenAI", {
      requestId,
      error: err?.message || String(err)
    });
    return await callOpenAI(safeMessage, safeHistory, safeContext, CONFIG, requestId);
  }
}

// =============================================================
//  Handler Premium (Node 24 / Edge)
// =============================================================

export default async function handler(request) {
  const requestId = createRequestId();
  const method = request.method;

  if (method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, x-auth-token"
      }
    });
  }

  const clientToken = request.headers.get("x-auth-token");
  if (!clientToken || clientToken !== process.env.PRIVATE_AUTH_TOKEN) {
    log("warn", "Unauthorized access", { requestId });
    return safeJson(401, {
      status: 401,
      requestId,
      error: "Unauthorized"
    });
  }

  if (method !== "POST") {
    log("warn", "Method not allowed", { requestId, method });
    return safeJson(405, {
      status: 405,
      requestId,
      error: "Method not allowed"
    });
  }

  try {
    const body = await request.json().catch(() => null);

    if (!body || typeof body !== "object") {
      log("warn", "Invalid JSON body", { requestId });
      return safeJson(400, {
        status: 400,
        requestId,
        error: "Invalid JSON body."
      });
    }

    const { message, history, context } = body;

    if (!message || typeof message !== "string") {
      log("warn", "Missing 'message' field", { requestId });
      return safeJson(400, {
        status: 400,
        requestId,
        error: "The 'message' field is required."
      });
    }

    const reply = await generateAnswer({
      message,
      history,
      context,
      requestId
    });

    log("info", "Request completed successfully", { requestId });

    return safeJson(200, {
      status: 200,
      requestId,
      success: true,
      reply
    });
  } catch (err) {
    log("error", "Internal server error", {
      requestId,
      error: err?.message || String(err)
    });

    return safeJson(500, {
      status: 500,
      requestId,
      success: false,
      error: "Internal server error."
    });
  }
}
