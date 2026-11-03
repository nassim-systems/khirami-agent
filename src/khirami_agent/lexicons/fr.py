"""
French lexicon — data only, no logic.

Khirami Agent reads requests in several languages by matching keyword markers.
This module holds the French surface forms; every key is a canonical English
category shared by all languages, so a request produces the same framing
whatever language it is written in. Markers are lower-case and accent-folded,
because they are matched against normalized text.
"""

# Function words used by the request framer to detect the language.
FUNCTION_WORDS = (
    "le",
    "les",
    "la",
    "une",
    "des",
    "du",
    "dans",
    "pour",
    "avec",
    "est",
    "sont",
    "cette",
    "nous",
    "vous",
    "je",
    "que",
    "qui",
    "sur",
    "aux",
    "par",
    "sans",
    "moi",
    "mon",
    "ma",
    "mes",
    "ainsi",
    "afin",
    "apres",
    "aussi",
    "toujours",
    "plutot",
    "fais",
    "sois",
    "ceci",
    "cela",
    "donc",
    "chaque",
    "toute",
    "quel",
    "quelle",
)


# What the request asks for.
OBJECTIVES = {
    "analyze": (
        "analyse",
        "analyser",
        "diagnostic",
        "audit",
        "auditer",
        "evalue",
        "evaluer",
        "examine",
        "etudie",
        "compare",
        "comparer",
        "cause",
        "causes",
        "pourquoi",
    ),
    "plan": (
        "plan",
        "planifie",
        "planifier",
        "roadmap",
        "feuille de route",
        "etapes",
        "organise",
        "priorise",
        "calendrier",
        "jalons",
        "sequence",
    ),
    "produce": (
        "cree",
        "creer",
        "ecris",
        "ecrire",
        "redige",
        "rediger",
        "genere",
        "generer",
        "implemente",
        "implementer",
        "developpe",
        "construis",
        "prepare",
        "modifie",
        "modifier",
        "corrige",
        "corriger",
        "ajoute",
        "configure",
        "installe",
    ),
    "summarize": (
        "resume",
        "resumer",
        "synthese",
        "synthetise",
        "recapitule",
        "recap",
        "en bref",
        "essentiel",
        "condense",
    ),
    "explain": (
        "explique",
        "expliquer",
        "explication",
        "vulgarise",
        "clarifie",
        "definis",
        "definition",
        "comprendre",
        "comment",
    ),
    "decide": (
        "dois je",
        "faut il",
        "vaut il mieux",
        "que choisir",
        "recommande",
        "conseille",
        "arbitre",
        "trancher",
        "quelle option",
        "pour ou contre",
    ),
    "verify": (
        "verifie",
        "verifier",
        "relis",
        "relire",
        "controle",
        "valide",
        "valider",
        "teste",
        "tester",
        "debug",
        "revois",
        "audite",
    ),
}


# What the request is about.
SUBJECTS = {
    "client": (
        "client",
        "clients",
        "prospect",
        "prospects",
        "utilisateur",
        "utilisateurs",
        "destinataire",
        "partenaire",
    ),
    "team": (
        "equipe",
        "collegue",
        "collegues",
        "collaborateur",
        "collaborateurs",
        "nous",
        "notre",
        "interne",
    ),
    "system": (
        "systeme",
        "serveur",
        "api",
        "base de donnees",
        "infrastructure",
        "module",
        "script",
        "fichier",
        "code",
        "classe",
        "fonction",
        "pipeline",
        "application",
    ),
    "self": ("moi", "je", "mon", "ma", "mes", "pour moi", "j ai"),
}


# Directional markers: who the deliverable is addressed to.
RECIPIENTS = {
    "client": (
        "pour le client",
        "pour les clients",
        "pour nos clients",
        "pour ce client",
        "a destination du client",
        "a destination des clients",
        "destine au client",
        "cote client",
        "pour l utilisateur",
        "pour les utilisateurs",
    ),
    "team": (
        "pour l equipe",
        "pour les equipes",
        "avec l equipe",
        "avec les equipes",
        "a destination de l equipe",
        "a l equipe",
        "pour le service",
        "pour le personnel",
        "pour le groupe",
        "pour le departement",
        "pour la direction",
        "pour le comite",
        "pour le codir",
        "pour le comex",
    ),
    "self": ("pour moi", "moi", "j ai besoin", "je veux", "mon usage"),
}


# Weak signal: first-person plural places the work in-house.
INTERNAL = {
    "team": ("on", "nous", "notre", "nos", "en interne"),
}


# Requested tone.
TONES = {
    "technical": ("technique", "rigoureux", "senior", "expert", "exact", "precis"),
    "executive": (
        "executif",
        "direction",
        "comite",
        "formel",
        "professionnel",
        "haut de gamme",
        "institutionnel",
    ),
    "educational": (
        "pedagogue",
        "pedagogique",
        "vulgarise",
        "simple",
        "accessible",
        "debutant",
        "explique moi",
    ),
    "direct": ("direct", "droit au but", "sans blabla", "franc", "cash", "brut"),
}


# Requested depth.
DEPTHS = {
    "in_depth": (
        "approfondi",
        "approfondie",
        "en profondeur",
        "exhaustif",
        "exhaustive",
        "complet",
        "complete",
        "detaille",
        "detaillee",
        "en detail",
        "pousse",
        "niveau expert",
    ),
    "condensed": (
        "court",
        "courte",
        "bref",
        "brievement",
        "concis",
        "concise",
        "en une phrase",
        "en deux mots",
        "pas trop long",
        "essentiel",
        "rapidement",
    ),
}


# Explicit constraints.
CONSTRAINTS = {
    "brevity": (
        "court",
        "courte",
        "bref",
        "brievement",
        "concis",
        "concise",
        "en une phrase",
        "en deux mots",
        "pas trop long",
        "sans blabla",
    ),
    "speed": (
        "vite",
        "rapide",
        "rapidement",
        "urgent",
        "urgence",
        "asap",
        "au plus vite",
        "tout de suite",
        "immediatement",
    ),
    "precision": (
        "precis",
        "precise",
        "exact",
        "exactement",
        "rigoureux",
        "fiable",
        "sans erreur",
        "verifiable",
        "sources",
        "strictement",
    ),
    "restricted_scope": (
        "uniquement",
        "seulement",
        "juste",
        "sans modifier",
        "sans toucher",
        "ne touche pas",
        "ne modifie pas",
        "ne change pas",
    ),
    "no_implementation": (
        "sans code",
        "pas de code",
        "aucun code",
        "aucune logique",
        "sans logique",
        "structure uniquement",
        "architecture uniquement",
    ),
    "imposed_format": (
        "tableau",
        "liste",
        "puces",
        "markdown",
        "json",
        "csv",
        "sections",
        "colonnes",
    ),
    "language": ("en francais", "en anglais", "in english", "traduis", "bilingue"),
}


# Words that can neither open nor close a focus phrase.
STOPWORDS = frozenset(
    (
        "afin",
        "ai",
        "aimerais",
        "apres",
        "avant",
        "avec",
        "avons",
        "besoin",
        "bien",
        "car",
        "ce",
        "ces",
        "cet",
        "cette",
        "chez",
        "dans",
        "deja",
        "donc",
        "dont",
        "elle",
        "elles",
        "en",
        "encore",
        "est",
        "et",
        "etait",
        "faut",
        "il",
        "ils",
        "je",
        "la",
        "le",
        "les",
        "leur",
        "leurs",
        "ma",
        "mais",
        "me",
        "mes",
        "moi",
        "moins",
        "mon",
        "ne",
        "nos",
        "notre",
        "nous",
        "on",
        "ont",
        "ou",
        "par",
        "pas",
        "plus",
        "pour",
        "que",
        "qui",
        "quoi",
        "sans",
        "se",
        "si",
        "sont",
        "souhaite",
        "souhaitons",
        "sur",
        "te",
        "tous",
        "tout",
        "toute",
        "toutes",
        "tres",
        "tu",
        "un",
        "une",
        "vers",
        "veulent",
        "veut",
        "veux",
        "vos",
        "votre",
        "voulons",
        "y",
    )
)


# Prepositions that link words inside one focus phrase.
LINKING_WORDS = frozenset(("a", "au", "aux", "d", "de", "des", "du", "l"))


# Verbs that state the direction of a measurable target.
DIRECTIONS = {
    "decrease": (
        "reduire",
        "reduction",
        "diminuer",
        "baisser",
        "raccourcir",
        "accelerer",
        "alleger",
        "limiter",
        "supprimer",
    ),
    "increase": (
        "augmenter",
        "accroitre",
        "doubler",
        "tripler",
        "ameliorer",
        "renforcer",
        "developper",
        "elargir",
        "recruter",
    ),
}


# Numbers written as words.
NUMBER_WORDS = (
    "deux",
    "trois",
    "quatre",
    "cinq",
    "six",
    "sept",
    "huit",
    "neuf",
    "dix",
    "onze",
    "douze",
    "quinze",
    "vingt",
    "trente",
    "cinquante",
    "cent",
    "mille",
    "moitie",
    "double",
    "triple",
)


# Month names, used to detect a deadline.
MONTHS = (
    "janvier",
    "fevrier",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "aout",
    "septembre",
    "octobre",
    "novembre",
    "decembre",
)


# Duration units that turn a number into a deadline.
DURATION_UNITS = frozenset(
    (
        "an",
        "annee",
        "annees",
        "ans",
        "jour",
        "jours",
        "mois",
        "semaine",
        "semaines",
        "trimestre",
        "trimestres",
    )
)


# Quarter and half-year labels.
PERIODS = frozenset(("s1", "s2", "t1", "t2", "t3", "t4"))


# Markers the engagement router uses to infer an execution mode.
ENGAGEMENT_MODES = {
    "quick_scan": ("rapide", "express", "apercu", "premier avis"),
    "automation_focus": ("automatiser", "automatisation", "robotiser"),
    "follow_up": ("suivi", "relance", "mise a jour"),
}


# Markers the engagement router uses to infer the business sector.
SECTORS = {
    "sales": ("vente", "ventes", "commercial", "prospect", "pipeline", "devis"),
    "support": ("sav", "reclamation", "service client"),
    "operations": ("logistique", "ordonnancement"),
    "recruiting": ("recrutement", "candidat", "candidats", "embauche"),
    "administration": ("administratif", "facturation", "comptabilite", "paie", "dossier"),
}


# Hype vocabulary the consultant guard flags in a deliverable.
HYPE_TERMS = ("revolutionnaire", "disruptif", "incontournable")


# Function words used by the constraint extractor to detect the language.
EXTRACTOR_FUNCTION_WORDS = (
    "le",
    "les",
    "la",
    "une",
    "des",
    "du",
    "dans",
    "pour",
    "avec",
    "est",
    "sont",
    "cette",
    "nous",
    "vous",
    "je",
    "que",
    "qui",
    "sur",
    "aux",
    "sans",
    "moi",
    "mon",
    "ma",
    "mes",
    "afin",
    "apres",
    "aussi",
    "fais",
    "sois",
    "cela",
    "donc",
    "chaque",
    "quel",
    "quelle",
    "plutot",
)


# Constraint extractor markers, grouped by family then category.
EXTRACTOR_LEXICON = {
    "constraints": {
        "word-limit": (
            "mots",
            "mot",
            "limite de mots",
            "maximum de mots",
            "pas plus de",
            "au maximum",
            "caracteres",
        ),
        "max-bullets": ("puces", "points", "bullets", "elements", "items"),
        "briefly": ("brievement", "bref", "breve", "en bref", "rapidement", "sans detour"),
        "concisely": ("concis", "concise", "concisement", "sans blabla", "droit au but", "epure"),
    },
    "registers": {
        "executive": ("executif", "direction", "comite", "c level", "board"),
        "consultant": ("consultant", "conseil", "cabinet", "senior"),
        "technical": ("technique", "ingenierie", "specifications"),
        "plain": ("vulgarise", "simple", "accessible", "grand public"),
    },
    "tones": {
        "formal": ("formel", "formelle", "protocolaire", "institutionnel"),
        "neutral": ("neutre", "factuel", "objectif"),
        "dynamic": ("dynamique", "percutant", "energique", "punchy"),
        "synthetic": ("synthetique", "condense", "resserre"),
    },
    "depths": {
        "brief": ("survol", "apercu", "grandes lignes", "haut niveau"),
        "medium": ("standard", "normal", "moyen", "intermediaire"),
        "detailed": ("complet", "complete", "exhaustif", "integral"),
        "expert": (
            "detaille",
            "detaillee",
            "approfondi",
            "approfondie",
            "en profondeur",
            "pointu",
            "niveau expert",
            "expert",
        ),
    },
    "formats": {
        "table": ("tableau", "grille", "matrice", "colonnes"),
        "list": ("liste", "enumeration", "puces"),
        "plan": ("plan", "feuille de route", "roadmap", "etapes"),
        "analysis": ("analyse", "diagnostic", "audit"),
        "synthesis": ("synthese", "resume", "recapitulatif", "note"),
    },
    "targets": {
        "client": ("client", "clients", "prospect", "utilisateur"),
        "team": ("equipe", "collegue", "collegues", "interne"),
        "management": ("direction", "comite", "board", "dirigeants"),
        "system": ("systeme", "serveur", "api", "module", "script"),
    },
}
