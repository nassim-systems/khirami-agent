"""
English lexicon — data only, no logic.

Khirami Agent reads requests in several languages by matching keyword markers.
This module holds the English surface forms; every key is a canonical English
category shared by all languages, so a request produces the same framing
whatever language it is written in. Markers are lower-case and accent-folded,
because they are matched against normalized text.
"""

# Function words used by the request framer to detect the language.
FUNCTION_WORDS = (
    "the",
    "and",
    "of",
    "with",
    "for",
    "you",
    "your",
    "our",
    "this",
    "that",
    "is",
    "are",
    "be",
    "to",
    "it",
    "we",
    "my",
    "an",
    "from",
    "about",
    "please",
    "should",
    "would",
    "could",
    "give",
    "keep",
    "make",
    "need",
    "want",
    "into",
    "than",
    "then",
    "each",
)


# What the request asks for.
OBJECTIVES = {
    "analyze": (
        "analyze",
        "analyse",
        "analysis",
        "diagnose",
        "diagnostic",
        "diagnosis",
        "audit",
        "evaluate",
        "assess",
        "assessment",
        "examine",
        "study",
        "compare",
        "why",
        "root cause",
        "causes",
    ),
    "plan": (
        "plan",
        "roadmap",
        "schedule",
        "organize",
        "prioritize",
        "milestones",
        "steps",
        "sequence",
        "timeline",
    ),
    "produce": (
        "create",
        "make",
        "write",
        "draft",
        "generate",
        "build",
        "implement",
        "develop",
        "produce",
        "prepare",
        "add",
        "modify",
        "fix",
        "configure",
        "install",
        "rewrite",
    ),
    "summarize": (
        "summarize",
        "summarise",
        "summary",
        "recap",
        "condense",
        "tldr",
        "key points",
        "in short",
    ),
    "explain": (
        "explain",
        "explanation",
        "clarify",
        "define",
        "definition",
        "understand",
        "walk me through",
        "what is",
        "how does",
    ),
    "decide": (
        "should i",
        "must i",
        "better to",
        "which option",
        "recommend",
        "advise",
        "decide",
        "choose",
        "pros and cons",
        "trade off",
    ),
    "verify": ("verify", "check", "review", "validate", "test", "debug", "proofread", "inspect"),
}


# What the request is about.
SUBJECTS = {
    "client": (
        "client",
        "clients",
        "customer",
        "customers",
        "prospect",
        "prospects",
        "user",
        "users",
        "recipient",
        "partner",
        "stakeholder",
    ),
    "team": (
        "team",
        "teammate",
        "colleague",
        "colleagues",
        "coworker",
        "staff",
        "internal",
        "we",
        "our",
    ),
    "system": (
        "system",
        "server",
        "api",
        "database",
        "infrastructure",
        "module",
        "script",
        "file",
        "code",
        "class",
        "function",
        "pipeline",
        "application",
        "app",
    ),
    "self": ("me", "my", "myself", "for me", "i need", "i want"),
}


# Directional markers: who the deliverable is addressed to.
RECIPIENTS = {
    "client": (
        "for the client",
        "for the customer",
        "for our clients",
        "for our customers",
        "to the client",
        "client facing",
        "for the user",
        "for the users",
    ),
    "team": (
        "for the team",
        "give the team",
        "for our team",
        "to the team",
        "for the staff",
        "with the team",
        "for the board",
        "for management",
        "for the department",
        "for the group",
    ),
    "self": ("for me", "i need", "i want", "my own"),
}


# Weak signal: first-person plural places the work in-house.
INTERNAL = {
    "team": ("we", "our", "us", "internally"),
}


# Requested tone.
TONES = {
    "technical": ("technical", "rigorous", "senior", "expert", "exact", "precise", "accurate"),
    "executive": (
        "executive",
        "leadership",
        "board",
        "formal",
        "professional",
        "high end",
        "institutional",
        "c level",
    ),
    "educational": (
        "beginner",
        "simple",
        "accessible",
        "plain",
        "layman",
        "pedagogical",
        "for a novice",
    ),
    "direct": (
        "direct",
        "straight to the point",
        "no fluff",
        "blunt",
        "frank",
        "casual",
        "friendly",
        "informal",
        "relaxed",
    ),
}


# Requested depth.
DEPTHS = {
    "in_depth": (
        "in depth",
        "detailed",
        "thorough",
        "exhaustive",
        "comprehensive",
        "complete",
        "deep",
        "step by step",
        "expert level",
        "in detail",
    ),
    "condensed": (
        "short",
        "brief",
        "briefly",
        "concise",
        "concisely",
        "quick",
        "high level",
        "in one sentence",
        "not too long",
        "overview",
    ),
}


# Explicit constraints.
CONSTRAINTS = {
    "brevity": (
        "short",
        "brief",
        "briefly",
        "concise",
        "concisely",
        "in one sentence",
        "in two words",
        "not too long",
        "no fluff",
    ),
    "speed": (
        "fast",
        "quick",
        "quickly",
        "urgent",
        "urgency",
        "asap",
        "right away",
        "immediately",
        "as soon as possible",
    ),
    "precision": (
        "precise",
        "precisely",
        "exact",
        "exactly",
        "rigorous",
        "reliable",
        "no errors",
        "verifiable",
        "sources",
        "strictly",
        "accurate",
        "factual",
    ),
    "restricted_scope": (
        "only",
        "just",
        "without modifying",
        "without touching",
        "do not modify",
        "do not change",
        "do not touch",
        "nothing else",
    ),
    "no_implementation": (
        "no code",
        "without code",
        "no logic",
        "without logic",
        "structure only",
        "architecture only",
        "no implementation",
    ),
    "imposed_format": (
        "table",
        "list",
        "bullets",
        "bullet points",
        "markdown",
        "json",
        "csv",
        "sections",
        "columns",
    ),
    "language": ("in french", "in english", "in spanish", "translate", "bilingual"),
}


# Words that can neither open nor close a focus phrase.
STOPWORDS = frozenset(
    (
        "a",
        "about",
        "after",
        "all",
        "an",
        "and",
        "are",
        "before",
        "but",
        "by",
        "for",
        "from",
        "had",
        "has",
        "have",
        "he",
        "i",
        "in",
        "is",
        "it",
        "like",
        "my",
        "need",
        "needs",
        "not",
        "on",
        "or",
        "our",
        "she",
        "so",
        "that",
        "the",
        "their",
        "these",
        "they",
        "this",
        "those",
        "to",
        "very",
        "want",
        "wants",
        "was",
        "we",
        "were",
        "with",
        "without",
        "would",
        "you",
        "your",
    )
)


# Prepositions that link words inside one focus phrase.
LINKING_WORDS = frozenset(())


# Verbs that state the direction of a measurable target.
DIRECTIONS = {
    "decrease": (
        "reduce",
        "reduction",
        "cut",
        "shorten",
        "decrease",
        "lower",
        "speed up",
        "remove",
    ),
    "increase": ("increase", "grow", "double", "triple", "improve", "strengthen", "expand", "hire"),
}


# Numbers written as words.
NUMBER_WORDS = (
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "twelve",
    "fifteen",
    "twenty",
    "thirty",
    "fifty",
    "hundred",
    "half",
    "double",
    "triple",
)


# Month names, used to detect a deadline.
MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)


# Duration units that turn a number into a deadline.
DURATION_UNITS = frozenset(
    ("day", "days", "month", "months", "quarter", "week", "weeks", "year", "years")
)


# Quarter and half-year labels.
PERIODS = frozenset(("q1", "q2", "q3", "q4"))


# Markers the engagement router uses to infer an execution mode.
ENGAGEMENT_MODES = {
    "quick_scan": ("quick", "overview"),
    "automation_focus": ("automate", "automation"),
    "follow_up": ("follow up",),
}


# Markers the engagement router uses to infer the business sector.
SECTORS = {
    "sales": ("sales", "revenue", "closing"),
    "support": ("support", "ticket", "tickets", "helpdesk", "customer service"),
    "operations": ("operations", "production", "supply", "planning"),
    "recruiting": ("hiring", "recruiting"),
    "administration": ("billing", "invoicing"),
}


# Hype vocabulary the consultant guard flags in a deliverable.
HYPE_TERMS = (
    "revolutionary",
    "game-changing",
    "game changing",
    "cutting-edge",
    "cutting edge",
    "seamless",
    "state of the art",
)


# Function words used by the constraint extractor to detect the language.
EXTRACTOR_FUNCTION_WORDS = (
    "the",
    "and",
    "of",
    "with",
    "for",
    "you",
    "your",
    "our",
    "this",
    "that",
    "is",
    "are",
    "be",
    "to",
    "it",
    "we",
    "my",
    "an",
    "from",
    "about",
    "please",
    "should",
    "would",
    "could",
    "give",
    "keep",
    "make",
    "need",
    "want",
    "into",
    "then",
    "each",
    "me",
)


# Constraint extractor markers, grouped by family then category.
EXTRACTOR_LEXICON = {
    "constraints": {
        "word-limit": (
            "words",
            "word",
            "word limit",
            "limit",
            "at most",
            "no more than",
            "characters",
        ),
        "max-bullets": ("bullets", "bullet points", "points", "items"),
        "briefly": ("briefly", "brief", "quickly", "in short", "tldr"),
        "concisely": ("concise", "concisely", "no fluff", "straight to the point", "tight"),
    },
    "registers": {
        "executive": ("executive", "leadership", "board", "c level"),
        "consultant": ("consulting", "consultant", "advisory", "senior"),
        "technical": ("technical", "engineering", "specification"),
        "plain": ("plain", "simple", "accessible", "layman", "beginner"),
    },
    "tones": {
        "formal": ("formal", "official", "institutional"),
        "neutral": ("neutral", "factual", "objective"),
        "dynamic": ("dynamic", "punchy", "energetic", "engaging"),
        "synthetic": ("synthetic", "condensed", "compressed"),
    },
    "depths": {
        "brief": ("overview", "high level", "skim", "glance"),
        "medium": ("standard", "normal", "medium", "moderate"),
        "detailed": ("comprehensive", "full", "complete", "exhaustive"),
        "expert": (
            "detailed",
            "in depth",
            "thorough",
            "deep",
            "expert",
            "expert level",
            "advanced",
        ),
    },
    "formats": {
        "table": ("table", "grid", "matrix", "columns"),
        "list": ("list", "enumeration", "bullets"),
        "plan": ("plan", "roadmap", "steps", "schedule"),
        "analysis": ("analysis", "diagnostic", "audit"),
        "synthesis": ("synthesis", "summary", "recap", "brief note"),
    },
    "targets": {
        "client": ("client", "clients", "customer", "prospect", "user"),
        "team": ("team", "colleague", "colleagues", "internal", "staff"),
        "management": ("management", "leadership", "board", "executives"),
        "system": ("system", "server", "api", "module", "script"),
    },
}
