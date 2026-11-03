"""
German lexicon — data only, no logic.

Khirami Agent reads requests in several languages by matching keyword markers.
This module holds the German surface forms; every key is a canonical English
category shared by all languages, so a request produces the same framing
whatever language it is written in. Markers are lower-case and accent-folded,
because they are matched against normalized text.
"""

# Function words used by the constraint extractor to detect the language.
EXTRACTOR_FUNCTION_WORDS = (
    "der",
    "die",
    "das",
    "und",
    "oder",
    "fur",
    "mit",
    "ein",
    "eine",
    "einen",
    "nicht",
    "ist",
    "sind",
    "bitte",
    "mir",
    "mich",
    "sehr",
    "auch",
    "immer",
    "einen",
    "beim",
    "vom",
    "zum",
    "zur",
    "auf",
    "aus",
    "bei",
    "nach",
    "uber",
    "unter",
    "wir",
    "sie",
    "ich",
    "erstelle",
    "schreibe",
    "mach",
    "soll",
)


# Constraint extractor markers, grouped by family then category.
EXTRACTOR_LEXICON = {
    "constraints": {
        "word-limit": (
            "worter",
            "wort",
            "wortlimit",
            "hochstens",
            "maximal",
            "nicht mehr als",
            "zeichen",
        ),
        "max-bullets": ("stichpunkte", "punkte", "elemente", "bullets"),
        "briefly": ("kurz", "kurzfassung", "knapp", "schnell"),
        "concisely": ("pragnant", "auf den punkt", "ohne umschweife"),
    },
    "registers": {
        "executive": ("vorstand", "geschaftsleitung", "fuhrungsebene"),
        "consultant": ("beratung", "berater", "senior"),
        "technical": ("technisch", "technische", "ingenieur"),
        "plain": ("einfach", "verstandlich", "allgemeinverstandlich"),
    },
    "tones": {
        "formal": ("formell", "offiziell", "institutionell"),
        "neutral": ("neutral", "sachlich", "objektiv"),
        "dynamic": ("dynamisch", "pragnant", "energisch"),
        "synthetic": ("verdichtet", "komprimiert", "gestrafft"),
    },
    "depths": {
        "brief": ("uberblick", "grobe linien", "hohes niveau"),
        "medium": ("standard", "normal", "mittel"),
        "detailed": ("vollstandig", "umfassend", "erschopfend"),
        "expert": (
            "detailliert",
            "ausfuhrlich",
            "tiefgehend",
            "vertieft",
            "experte",
            "expertenniveau",
            "fortgeschritten",
        ),
    },
    "formats": {
        "table": ("tabelle", "raster", "matrix", "spalten"),
        "list": ("liste", "aufzahlung", "stichpunkte"),
        "plan": ("plan", "fahrplan", "schritte", "zeitplan"),
        "analysis": ("analyse", "diagnose", "audit"),
        "synthesis": ("zusammenfassung", "synthese", "notiz"),
    },
    "targets": {
        "client": ("kunde", "kunden", "mandant", "nutzer"),
        "team": ("team", "kollege", "kollegen", "intern"),
        "management": ("management", "vorstand", "geschaftsleitung"),
        "system": ("system", "server", "api", "modul", "skript"),
    },
}
