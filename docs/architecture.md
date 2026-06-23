# Architecture

Document de haut niveau décrivant l'architecture du framework d'agent AI premium.

- Runtime: Edge-friendly serverless (Vercel, Cloudflare Workers, etc.)
- Backend: API endpoint `/api/ask` pour orchestration et logique métier
- Frontend: widget embeddable léger (widget-v2.js)
- Clients: profils séparés stockant prompts, règles et knowledge bases
