"""
Spanish lexicon — data only, no logic.

Khirami Agent reads requests in several languages by matching keyword markers.
This module holds the Spanish surface forms; every key is a canonical English
category shared by all languages, so a request produces the same framing
whatever language it is written in. Markers are lower-case and accent-folded,
because they are matched against normalized text.
"""

# Function words used by the request framer to detect the language.
FUNCTION_WORDS = (
    "el",
    "los",
    "las",
    "una",
    "unos",
    "unas",
    "del",
    "al",
    "para",
    "con",
    "por",
    "sobre",
    "es",
    "son",
    "este",
    "muy",
    "tambien",
    "aqui",
    "ahora",
    "usted",
    "nosotros",
    "hacia",
    "segun",
    "pero",
    "cuando",
    "donde",
    "necesito",
    "necesitamos",
    "quiero",
    "dame",
    "hazme",
    "favor",
    "y",
)


# What the request asks for.
OBJECTIVES = {
    "analyze": (
        "analiza",
        "analizar",
        "analisis",
        "diagnostico",
        "auditoria",
        "evalua",
        "evaluar",
        "examina",
        "estudia",
        "compara",
        "comparar",
        "por que",
        "causa",
        "causas",
    ),
    "plan": (
        "plan",
        "planifica",
        "planificar",
        "hoja de ruta",
        "etapas",
        "pasos",
        "organiza",
        "prioriza",
        "calendario",
        "hitos",
        "secuencia",
    ),
    "produce": (
        "crea",
        "crear",
        "escribe",
        "escriba",
        "escribir",
        "redacta",
        "redactar",
        "genera",
        "generar",
        "implementa",
        "implementar",
        "desarrolla",
        "construye",
        "prepara",
        "modifica",
        "modificar",
        "corrige",
        "corregir",
        "anade",
        "configura",
        "instala",
    ),
    "summarize": (
        "resume",
        "resumir",
        "resumen",
        "sintesis",
        "sintetiza",
        "recapitula",
        "en breve",
        "esencial",
        "condensa",
    ),
    "explain": (
        "explica",
        "explicar",
        "explicacion",
        "aclara",
        "clarifica",
        "define",
        "definicion",
        "entender",
        "comprender",
        "como",
    ),
    "decide": (
        "debo",
        "deberia",
        "hay que",
        "es mejor",
        "que elegir",
        "recomienda",
        "aconseja",
        "decide",
        "decidir",
        "arbitra",
        "que opcion",
        "pros y contras",
    ),
    "verify": (
        "verifica",
        "verificar",
        "revisa",
        "revisar",
        "controla",
        "valida",
        "validar",
        "prueba",
        "probar",
        "comprueba",
        "depura",
    ),
}


# What the request is about.
SUBJECTS = {
    "client": ("cliente", "clientes", "prospecto", "usuario", "usuarios", "destinatario", "socio"),
    "team": (
        "equipo",
        "colega",
        "colegas",
        "companero",
        "companeros",
        "nosotros",
        "nuestro",
        "nuestra",
        "interno",
    ),
    "system": (
        "sistema",
        "servidor",
        "api",
        "base de datos",
        "infraestructura",
        "modulo",
        "script",
        "archivo",
        "fichero",
        "codigo",
        "clase",
        "funcion",
        "pipeline",
        "aplicacion",
    ),
    "self": ("yo", "mi", "mis", "para mi", "necesito", "quiero"),
}


# Directional markers: who the deliverable is addressed to.
RECIPIENTS = {
    "client": ("para el cliente", "para los clientes", "para nuestros clientes", "para el usuario"),
    "team": (
        "para el equipo",
        "al equipo",
        "para nuestro equipo",
        "para el personal",
        "para el departamento",
        "para el grupo",
        "con el equipo",
        "para la direccion",
    ),
    "self": ("para mi", "necesito", "quiero"),
}


# Weak signal: first-person plural places the work in-house.
INTERNAL = {
    "team": ("nosotros", "nuestro", "nuestra", "internamente"),
}


# Requested tone.
TONES = {
    "technical": ("tecnico", "tecnica", "riguroso", "senior", "experto", "exacto", "preciso"),
    "executive": (
        "ejecutivo",
        "direccion",
        "comite",
        "formal",
        "profesional",
        "alta gama",
        "institucional",
    ),
    "educational": (
        "pedagogico",
        "divulgativo",
        "simple",
        "sencillo",
        "accesible",
        "principiante",
        "explicame",
    ),
    "direct": ("directo", "al grano", "sin rodeos", "franco", "informal", "cercano", "amistoso"),
}


# Requested depth.
DEPTHS = {
    "in_depth": (
        "en profundidad",
        "profundo",
        "profunda",
        "detallado",
        "detallada",
        "exhaustivo",
        "exhaustiva",
        "completo",
        "completa",
        "paso a paso",
        "nivel experto",
    ),
    "condensed": (
        "corto",
        "corta",
        "breve",
        "brevemente",
        "conciso",
        "concisa",
        "en una frase",
        "en dos palabras",
        "no muy largo",
        "rapido",
        "alto nivel",
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
        "en una frase",
        "en dos palabras",
        "no muy largo",
        "sin rodeos",
    ),
    "speed": (
        "rapido",
        "rapidamente",
        "urgente",
        "urgencia",
        "asap",
        "cuanto antes",
        "de inmediato",
        "inmediatamente",
    ),
    "precision": (
        "preciso",
        "precisa",
        "exacto",
        "exactamente",
        "riguroso",
        "fiable",
        "sin errores",
        "verificable",
        "fuentes",
        "estrictamente",
    ),
    "restricted_scope": (
        "unicamente",
        "solamente",
        "solo",
        "sin modificar",
        "sin tocar",
        "no modifiques",
        "no cambies",
        "no toques",
    ),
    "no_implementation": (
        "sin codigo",
        "nada de codigo",
        "sin logica",
        "ninguna logica",
        "solo estructura",
        "solo arquitectura",
    ),
    "imposed_format": (
        "tabla",
        "lista",
        "vinetas",
        "markdown",
        "json",
        "csv",
        "secciones",
        "columnas",
    ),
    "language": ("en espanol", "en ingles", "en frances", "traduce", "bilingue"),
}


# Words that can neither open nor close a focus phrase.
STOPWORDS = frozenset(
    (
        "antes",
        "con",
        "despues",
        "el",
        "ella",
        "ellos",
        "en",
        "era",
        "es",
        "esta",
        "este",
        "estos",
        "la",
        "las",
        "los",
        "mi",
        "muy",
        "necesitamos",
        "necesito",
        "no",
        "nosotros",
        "nuestra",
        "nuestro",
        "o",
        "para",
        "pero",
        "por",
        "queremos",
        "quiero",
        "sin",
        "son",
        "su",
        "sus",
        "tiene",
        "tienen",
        "todo",
        "tu",
        "un",
        "una",
        "y",
        "yo",
    )
)


# Prepositions that link words inside one focus phrase.
LINKING_WORDS = frozenset(("de", "del"))


# Verbs that state the direction of a measurable target.
DIRECTIONS = {
    "decrease": ("reducir", "reduccion", "disminuir", "bajar", "acortar"),
    "increase": ("aumentar", "crecer", "duplicar", "mejorar", "ampliar"),
}


# Numbers written as words.
NUMBER_WORDS = ("dos", "tres", "cuatro", "cinco", "diez", "doce", "veinte", "mitad")


# Month names, used to detect a deadline.
MONTHS = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


# Duration units that turn a number into a deadline.
DURATION_UNITS = frozenset(("ano", "anos", "dia", "dias", "mes", "meses", "semana", "semanas"))


# Quarter and half-year labels.
PERIODS = frozenset(())


# Markers the engagement router uses to infer an execution mode.
ENGAGEMENT_MODES = {
    "quick_scan": ("vista rapida",),
    "automation_focus": ("automatizar",),
    "follow_up": ("seguimiento",),
}


# Markers the engagement router uses to infer the business sector.
SECTORS = {
    "sales": ("ventas",),
    "support": ("soporte",),
    "operations": ("operaciones",),
    "recruiting": ("reclutamiento",),
    "administration": ("administracion",),
}


# Hype vocabulary the consultant guard flags in a deliverable.
HYPE_TERMS = ()


# Function words used by the constraint extractor to detect the language.
EXTRACTOR_FUNCTION_WORDS = (
    "el",
    "los",
    "las",
    "una",
    "unos",
    "unas",
    "del",
    "para",
    "con",
    "por",
    "sobre",
    "son",
    "este",
    "esta",
    "muy",
    "tambien",
    "aqui",
    "ahora",
    "usted",
    "nosotros",
    "hacia",
    "segun",
    "pero",
    "cuando",
    "donde",
    "necesito",
    "quiero",
    "dame",
    "hazme",
    "favor",
)


# Constraint extractor markers, grouped by family then category.
EXTRACTOR_LEXICON = {
    "constraints": {
        "word-limit": (
            "palabras",
            "palabra",
            "limite de palabras",
            "como maximo",
            "no mas de",
            "caracteres",
        ),
        "max-bullets": ("vinetas", "puntos", "elementos", "items"),
        "briefly": ("brevemente", "breve", "en breve", "rapidamente"),
        "concisely": ("conciso", "concisa", "sin rodeos", "al grano"),
    },
    "registers": {
        "executive": ("ejecutivo", "direccion", "comite", "consejo"),
        "consultant": ("consultor", "consultoria", "asesoria", "senior"),
        "technical": ("tecnico", "tecnica", "ingenieria"),
        "plain": ("divulgativo", "simple", "sencillo", "accesible"),
    },
    "tones": {
        "formal": ("formal", "protocolario", "institucional"),
        "neutral": ("neutro", "neutral", "factual", "objetivo"),
        "dynamic": ("dinamico", "contundente", "energico"),
        "synthetic": ("sintetico", "condensado", "comprimido"),
    },
    "depths": {
        "brief": ("vistazo", "alto nivel", "panorama", "resumen rapido"),
        "medium": ("estandar", "normal", "medio", "intermedio"),
        "detailed": ("completo", "completa", "exhaustivo", "integral"),
        "expert": (
            "detallado",
            "detallada",
            "en profundidad",
            "profundo",
            "experto",
            "nivel experto",
            "avanzado",
        ),
    },
    "formats": {
        "table": ("tabla", "cuadro", "matriz", "columnas"),
        "list": ("lista", "enumeracion", "vinetas"),
        "plan": ("plan", "hoja de ruta", "etapas", "pasos"),
        "analysis": ("analisis", "diagnostico", "auditoria"),
        "synthesis": ("sintesis", "resumen", "recapitulacion", "nota"),
    },
    "targets": {
        "client": ("cliente", "clientes", "prospecto", "usuario"),
        "team": ("equipo", "colega", "colegas", "interno"),
        "management": ("direccion", "comite", "directivos", "consejo"),
        "system": ("sistema", "servidor", "api", "modulo", "script"),
    },
}
