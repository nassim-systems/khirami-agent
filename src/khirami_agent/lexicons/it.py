"""
Italian lexicon — data only, no logic.

Khirami Agent reads requests in several languages by matching keyword markers.
This module holds the Italian surface forms; every key is a canonical English
category shared by all languages, so a request produces the same framing
whatever language it is written in. Markers are lower-case and accent-folded,
because they are matched against normalized text.
"""

# Function words used by the request framer to detect the language.
FUNCTION_WORDS = (
    "il",
    "lo",
    "gli",
    "della",
    "delle",
    "degli",
    "nella",
    "nel",
    "sul",
    "sui",
    "sulla",
    "alla",
    "dalla",
    "per",
    "con",
    "che",
    "questo",
    "questa",
    "molto",
    "anche",
    "perche",
    "quindi",
    "sono",
    "vorrei",
    "fammi",
    "adesso",
    "subito",
    "dei",
    "dal",
    "col",
    "mi",
    "ti",
    "ci",
    "una",
    "un",
)


# What the request asks for.
OBJECTIVES = {
    "analyze": (
        "analizza",
        "analizzare",
        "analisi",
        "diagnosi",
        "audit",
        "valuta",
        "valutare",
        "esamina",
        "studia",
        "confronta",
        "confrontare",
        "perche",
        "causa",
        "cause",
    ),
    "plan": (
        "piano",
        "pianifica",
        "pianificare",
        "roadmap",
        "tappe",
        "passi",
        "organizza",
        "prioritizza",
        "calendario",
        "milestone",
        "sequenza",
    ),
    "produce": (
        "crea",
        "creare",
        "scrivi",
        "scrivere",
        "redigi",
        "redigere",
        "genera",
        "generare",
        "implementa",
        "implementare",
        "sviluppa",
        "costruisci",
        "prepara",
        "modifica",
        "modificare",
        "correggi",
        "correggere",
        "aggiungi",
        "configura",
        "installa",
    ),
    "summarize": (
        "riassumi",
        "riassumere",
        "riassunto",
        "sintesi",
        "sintetizza",
        "ricapitola",
        "in breve",
        "essenziale",
        "condensa",
    ),
    "explain": (
        "spiega",
        "spiegare",
        "spiegazione",
        "chiarisci",
        "definisci",
        "definizione",
        "capire",
        "comprendere",
        "come",
    ),
    "decide": (
        "devo",
        "dovrei",
        "bisogna",
        "e meglio",
        "quale scegliere",
        "raccomanda",
        "consiglia",
        "decidi",
        "decidere",
        "arbitra",
        "quale opzione",
        "pro e contro",
    ),
    "verify": (
        "verifica",
        "verificare",
        "rileggi",
        "controlla",
        "controllare",
        "valida",
        "validare",
        "testa",
        "testare",
        "revisiona",
        "debug",
    ),
}


# What the request is about.
SUBJECTS = {
    "client": ("cliente", "clienti", "prospect", "utente", "utenti", "destinatario", "partner"),
    "team": (
        "squadra",
        "team",
        "collega",
        "colleghi",
        "collaboratore",
        "noi",
        "nostro",
        "nostra",
        "interno",
    ),
    "system": (
        "sistema",
        "server",
        "api",
        "database",
        "base dati",
        "infrastruttura",
        "modulo",
        "script",
        "file",
        "codice",
        "classe",
        "funzione",
        "pipeline",
        "applicazione",
    ),
    "self": ("io", "mio", "mia", "miei", "per me", "vorrei"),
}


# Directional markers: who the deliverable is addressed to.
RECIPIENTS = {
    "client": ("per il cliente", "per i clienti", "per i nostri clienti", "per l utente"),
    "team": (
        "per la squadra",
        "per il reparto",
        "per il team",
        "per il gruppo",
        "per il personale",
        "con il team",
        "con la squadra",
        "per la direzione",
    ),
    "self": ("per me", "ho bisogno", "vorrei"),
}


# Weak signal: first-person plural places the work in-house.
INTERNAL = {
    "team": ("noi", "nostro", "nostra", "internamente"),
}


# Requested tone.
TONES = {
    "technical": ("tecnico", "tecnica", "rigoroso", "senior", "esperto", "esatto", "preciso"),
    "executive": (
        "esecutivo",
        "direzione",
        "comitato",
        "formale",
        "professionale",
        "alta gamma",
        "istituzionale",
    ),
    "educational": (
        "pedagogico",
        "divulgativo",
        "semplice",
        "accessibile",
        "principiante",
        "spiegami",
    ),
    "direct": (
        "diretto",
        "al punto",
        "senza fronzoli",
        "franco",
        "schietto",
        "informale",
        "amichevole",
    ),
}


# Requested depth.
DEPTHS = {
    "in_depth": (
        "approfondito",
        "approfondita",
        "in profondita",
        "dettagliato",
        "dettagliata",
        "esaustivo",
        "esaustiva",
        "completo",
        "completa",
        "passo passo",
        "livello esperto",
    ),
    "condensed": (
        "corto",
        "breve",
        "brevemente",
        "conciso",
        "concisa",
        "in una frase",
        "in due parole",
        "non troppo lungo",
        "rapido",
        "alto livello",
    ),
}


# Explicit constraints.
CONSTRAINTS = {
    "brevity": (
        "corto",
        "breve",
        "brevemente",
        "conciso",
        "concisa",
        "in una frase",
        "in due parole",
        "non troppo lungo",
        "senza fronzoli",
    ),
    "speed": (
        "veloce",
        "rapido",
        "rapidamente",
        "urgente",
        "urgenza",
        "asap",
        "al piu presto",
        "subito",
        "immediatamente",
    ),
    "precision": (
        "preciso",
        "precisa",
        "esatto",
        "esattamente",
        "rigoroso",
        "affidabile",
        "senza errori",
        "verificabile",
        "fonti",
        "rigorosamente",
    ),
    "restricted_scope": (
        "unicamente",
        "solamente",
        "solo",
        "senza modificare",
        "senza toccare",
        "non modificare",
        "non cambiare",
        "non toccare",
    ),
    "no_implementation": (
        "senza codice",
        "nessun codice",
        "senza logica",
        "nessuna logica",
        "solo struttura",
        "solo architettura",
    ),
    "imposed_format": (
        "tabella",
        "elenco",
        "lista",
        "punti",
        "markdown",
        "json",
        "csv",
        "sezioni",
        "colonne",
    ),
    "language": ("in italiano", "in inglese", "in francese", "traduci", "bilingue"),
}


# Words that can neither open nor close a focus phrase.
STOPWORDS = frozenset(
    (
        "abbiamo",
        "con",
        "da",
        "dopo",
        "e",
        "era",
        "gli",
        "ha",
        "hanno",
        "i",
        "il",
        "in",
        "io",
        "la",
        "le",
        "lei",
        "lo",
        "loro",
        "lui",
        "ma",
        "mio",
        "molto",
        "noi",
        "non",
        "nostra",
        "nostro",
        "o",
        "per",
        "prima",
        "questa",
        "questo",
        "senza",
        "serve",
        "sono",
        "su",
        "suo",
        "tu",
        "tutto",
        "un",
        "una",
        "vogliamo",
        "voglio",
    )
)


# Prepositions that link words inside one focus phrase.
LINKING_WORDS = frozenset(("da", "dei", "del", "della", "delle", "dello", "di"))


# Verbs that state the direction of a measurable target.
DIRECTIONS = {
    "decrease": ("ridurre", "riduzione", "diminuire", "abbassare", "accorciare"),
    "increase": ("aumentare", "crescere", "raddoppiare", "migliorare", "ampliare"),
}


# Numbers written as words.
NUMBER_WORDS = ("due", "tre", "quattro", "cinque", "dieci", "dodici", "venti", "meta")


# Month names, used to detect a deadline.
MONTHS = (
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
)


# Duration units that turn a number into a deadline.
DURATION_UNITS = frozenset(
    ("anni", "anno", "giorni", "giorno", "mese", "mesi", "settimana", "settimane")
)


# Quarter and half-year labels.
PERIODS = frozenset(())


# Markers the engagement router uses to infer an execution mode.
ENGAGEMENT_MODES = {
    "quick_scan": ("panoramica",),
    "automation_focus": ("automatizzare",),
    "follow_up": ("aggiornamento",),
}


# Markers the engagement router uses to infer the business sector.
SECTORS = {
    "sales": ("vendite",),
    "support": ("assistenza",),
    "operations": ("operazioni",),
    "recruiting": ("assunzione",),
    "administration": ("amministrazione",),
}


# Hype vocabulary the consultant guard flags in a deliverable.
HYPE_TERMS = ()


# Function words used by the constraint extractor to detect the language.
EXTRACTOR_FUNCTION_WORDS = (
    "il",
    "lo",
    "gli",
    "della",
    "delle",
    "degli",
    "nella",
    "nel",
    "sul",
    "sui",
    "sulla",
    "alla",
    "dalla",
    "per",
    "con",
    "che",
    "questo",
    "questa",
    "molto",
    "anche",
    "perche",
    "quindi",
    "sono",
    "vorrei",
    "fammi",
    "adesso",
    "subito",
    "dei",
    "dal",
    "col",
    "mi",
    "ti",
    "ci",
)


# Constraint extractor markers, grouped by family then category.
EXTRACTOR_LEXICON = {
    "constraints": {
        "word-limit": (
            "parole",
            "parola",
            "limite di parole",
            "al massimo",
            "non piu di",
            "caratteri",
        ),
        "max-bullets": ("punti", "elenchi", "elementi", "bullet"),
        "briefly": ("brevemente", "breve", "in breve", "rapidamente"),
        "concisely": ("conciso", "concisa", "senza fronzoli", "al punto"),
    },
    "registers": {
        "executive": ("esecutivo", "direzione", "comitato", "consiglio"),
        "consultant": ("consulente", "consulenza", "senior"),
        "technical": ("tecnico", "tecnica", "ingegneria"),
        "plain": ("divulgativo", "semplice", "accessibile"),
    },
    "tones": {
        "formal": ("formale", "ufficiale", "istituzionale"),
        "neutral": ("neutro", "neutrale", "fattuale", "oggettivo"),
        "dynamic": ("dinamico", "incisivo", "energico"),
        "synthetic": ("sintetico", "condensato", "compresso"),
    },
    "depths": {
        "brief": ("panoramica", "alto livello", "sguardo"),
        "medium": ("standard", "normale", "medio", "intermedio"),
        "detailed": ("completo", "completa", "esaustivo", "integrale"),
        "expert": (
            "dettagliato",
            "dettagliata",
            "in profondita",
            "approfondito",
            "esperto",
            "livello esperto",
            "avanzato",
        ),
    },
    "formats": {
        "table": ("tabella", "griglia", "matrice", "colonne"),
        "list": ("elenco", "lista", "enumerazione"),
        "plan": ("piano", "roadmap", "tappe", "calendario"),
        "analysis": ("analisi", "diagnosi", "audit"),
        "synthesis": ("sintesi", "riassunto", "nota"),
    },
    "targets": {
        "client": ("cliente", "clienti", "utente", "prospect"),
        "team": ("squadra", "team", "collega", "colleghi", "interno"),
        "management": ("direzione", "comitato", "dirigenti", "consiglio"),
        "system": ("sistema", "server", "api", "modulo", "script"),
    },
}
