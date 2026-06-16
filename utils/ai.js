import OpenAI from "openai";
import fetch from "node-fetch";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function callOpenAI(message, history, context) {
  return openai.chat.completions.create({
    model: "gpt-4.1",
    messages: [
      ...history,
      { role: "user", content: `${context}\n\n${message}` }
    ],
    max_tokens: 2000,
    temperature: 0.7
  });
}

export async function callClaude(message, history, context) {
  const body = {
    model: "claude-3-5-sonnet-20240620",
    max_tokens: 2000,
    messages: [
      ...history,
      { role: "user", content: `${context}\n\n${message}` }
    ]
  };

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json"
    },
    body: JSON.stringify(body)
  });

  return res.json();
}
