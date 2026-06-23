# API

Description des endpoints exposés par le backend.

POST /api/ask
- Entrée: { message, history, context, client }
- Auth: header `x-auth-token`
- Retour: payload JSON structuré pour le widget
