"""
Portuguese lexicon — data only, no logic.

Khirami Agent reads requests in several languages by matching keyword markers.
This module holds the Portuguese surface forms; every key is a canonical English
category shared by all languages, so a request produces the same framing
whatever language it is written in. Markers are lower-case and accent-folded,
because they are matched against normalized text.
"""

# Function words used by the request framer to detect the language.
FUNCTION_WORDS = (
    "os",
    "as",
    "uma",
    "um",
    "ao",
    "aos",
    "do",
    "da",
    "dos",
    "das",
    "no",
    "na",
    "nos",
    "nas",
    "com",
    "para",
    "em",
    "voce",
    "nao",
    "sao",
    "esta",
    "muito",
    "tambem",
    "isso",
    "pelo",
    "pela",
    "seja",
    "favor",
    "preciso",
    "precisamos",
    "quero",
    "agora",
    "depois",
    "antes",
    "sobre",
    "escreva",
    "faca",
)


# What the request asks for.
OBJECTIVES = {
    "analyze": (
        "analisa",
        "analisar",
        "analise",
        "diagnostico",
        "auditoria",
        "avalia",
        "avaliar",
        "examina",
        "estuda",
        "compara",
        "comparar",
        "por que",
        "porque",
        "causa",
        "causas",
    ),
    "plan": (
        "plano",
        "planeja",
        "planejar",
        "planifica",
        "roteiro",
        "etapas",
        "passos",
        "organiza",
        "prioriza",
        "calendario",
        "marcos",
        "sequencia",
    ),
    "produce": (
        "cria",
        "criar",
        "escreve",
        "escreva",
        "escrever",
        "redige",
        "redigir",
        "gera",
        "gerar",
        "implementa",
        "implementar",
        "desenvolve",
        "constroi",
        "prepara",
        "modifica",
        "modificar",
        "corrige",
        "corrigir",
        "adiciona",
        "configura",
        "instala",
    ),
    "summarize": (
        "resume",
        "resumir",
        "resumo",
        "sintese",
        "sintetiza",
        "recapitula",
        "em resumo",
        "essencial",
        "condensa",
    ),
    "explain": (
        "explica",
        "explicar",
        "explicacao",
        "esclarece",
        "clarifica",
        "define",
        "definicao",
        "entender",
        "compreender",
        "como",
    ),
    "decide": (
        "devo",
        "deveria",
        "e preciso",
        "e melhor",
        "o que escolher",
        "recomenda",
        "aconselha",
        "decide",
        "decidir",
        "arbitra",
        "qual opcao",
        "pros e contras",
    ),
    "verify": (
        "verifica",
        "verificar",
        "revisa",
        "revisar",
        "controla",
        "valida",
        "validar",
        "testa",
        "testar",
        "confere",
        "depura",
    ),
}


# What the request is about.
SUBJECTS = {
    "client": (
        "cliente",
        "clientes",
        "prospecto",
        "usuario",
        "usuarios",
        "utilizador",
        "destinatario",
        "parceiro",
    ),
    "team": (
        "equipe",
        "equipa",
        "colega",
        "colegas",
        "colaborador",
        "nosso",
        "nossa",
        "interno",
        "time",
    ),
    "system": (
        "sistema",
        "servidor",
        "api",
        "base de dados",
        "infraestrutura",
        "modulo",
        "script",
        "arquivo",
        "ficheiro",
        "codigo",
        "classe",
        "funcao",
        "pipeline",
        "aplicacao",
    ),
    "self": ("eu", "meu", "minha", "meus", "para mim", "quero"),
}


# Directional markers: who the deliverable is addressed to.
RECIPIENTS = {
    "client": (
        "para o cliente",
        "para os clientes",
        "para os nossos clientes",
        "para o utilizador",
    ),
    "team": (
        "para a equipe",
        "para a equipa",
        "para o time",
        "para a nossa equipe",
        "para o pessoal",
        "para o departamento",
        "para o grupo",
        "com a equipe",
        "com a equipa",
        "para a direcao",
    ),
    "self": ("para mim", "preciso", "quero"),
}


# Weak signal: first-person plural places the work in-house.
INTERNAL = {
    "team": ("nos", "nosso", "nossa", "internamente"),
}


# Requested tone.
TONES = {
    "technical": ("tecnico", "tecnica", "rigoroso", "senior", "especialista", "exato", "preciso"),
    "executive": (
        "executivo",
        "direcao",
        "comite",
        "formal",
        "profissional",
        "alto padrao",
        "institucional",
    ),
    "educational": ("pedagogico", "didatico", "simples", "acessivel", "iniciante", "explica me"),
    "direct": ("direto", "ao ponto", "sem rodeios", "franco", "objetivo", "informal", "amigavel"),
}


# Requested depth.
DEPTHS = {
    "in_depth": (
        "em profundidade",
        "profundo",
        "profunda",
        "detalhado",
        "detalhada",
        "exaustivo",
        "exaustiva",
        "completo",
        "completa",
        "passo a passo",
        "nivel especialista",
    ),
    "condensed": (
        "curto",
        "curta",
        "breve",
        "brevemente",
        "conciso",
        "concisa",
        "em uma frase",
        "em duas palavras",
        "nao muito longo",
        "rapido",
        "alto nivel",
    ),
}


# Explicit constraints.
CONSTRAINTS = {
    "brevity": (
        "curto",
        "curta",
        "breve",
        "brevemente",
        "conciso",
        "concisa",
        "em uma frase",
        "em duas palavras",
        "nao muito longo",
        "sem rodeios",
    ),
    "speed": (
        "rapido",
        "rapidamente",
        "urgente",
        "urgencia",
        "asap",
        "o quanto antes",
        "imediatamente",
        "com urgencia",
    ),
    "precision": (
        "preciso",
        "precisa",
        "exato",
        "exatamente",
        "rigoroso",
        "confiavel",
        "sem erros",
        "verificavel",
        "fontes",
        "estritamente",
    ),
    "restricted_scope": (
        "unicamente",
        "somente",
        "apenas",
        "sem modificar",
        "sem tocar",
        "nao modifique",
        "nao mude",
        "nao toque",
    ),
    "no_implementation": (
        "sem codigo",
        "nenhum codigo",
        "sem logica",
        "nenhuma logica",
        "apenas estrutura",
        "apenas arquitetura",
    ),
    "imposed_format": (
        "tabela",
        "lista",
        "marcadores",
        "markdown",
        "json",
        "csv",
        "secoes",
        "colunas",
    ),
    "language": ("em portugues", "em ingles", "em frances", "traduza", "bilingue"),
}


# Words that can neither open nor close a focus phrase.
STOPWORDS = frozenset(
    (
        "a",
        "antes",
        "as",
        "com",
        "depois",
        "e",
        "ela",
        "ele",
        "eles",
        "em",
        "era",
        "esta",
        "este",
        "eu",
        "mas",
        "meu",
        "muito",
        "nao",
        "nos",
        "nossa",
        "nosso",
        "o",
        "os",
        "ou",
        "para",
        "por",
        "precisamos",
        "preciso",
        "queremos",
        "quero",
        "sao",
        "sem",
        "seu",
        "tem",
        "todo",
        "tu",
        "um",
        "uma",
    )
)


# Prepositions that link words inside one focus phrase.
LINKING_WORDS = frozenset(("da", "das", "do", "dos"))


# Verbs that state the direction of a measurable target.
DIRECTIONS = {
    "decrease": ("reduzir", "reducao", "diminuir", "baixar", "encurtar"),
    "increase": ("aumentar", "crescer", "duplicar", "melhorar", "ampliar"),
}


# Numbers written as words.
NUMBER_WORDS = ("dois", "tres", "quatro", "cinco", "dez", "doze", "vinte", "metade")


# Month names, used to detect a deadline.
MONTHS = (
    "janeiro",
    "fevereiro",
    "marco",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


# Duration units that turn a number into a deadline.
DURATION_UNITS = frozenset(("ano", "anos", "dia", "dias", "mes", "meses", "semana", "semanas"))


# Quarter and half-year labels.
PERIODS = frozenset(())


# Markers the engagement router uses to infer an execution mode.
ENGAGEMENT_MODES = {
    "quick_scan": ("visao geral",),
    "automation_focus": ("automatizacao",),
    "follow_up": ("acompanhamento",),
}


# Markers the engagement router uses to infer the business sector.
SECTORS = {
    "sales": ("vendas",),
    "support": ("atendimento",),
    "operations": ("operacoes",),
    "recruiting": ("recrutamento",),
    "administration": ("administracao",),
}


# Hype vocabulary the consultant guard flags in a deliverable.
HYPE_TERMS = ()


# Function words used by the constraint extractor to detect the language.
EXTRACTOR_FUNCTION_WORDS = (
    "os",
    "as",
    "uma",
    "do",
    "da",
    "dos",
    "das",
    "no",
    "na",
    "nos",
    "nas",
    "com",
    "para",
    "em",
    "voce",
    "nao",
    "sao",
    "muito",
    "tambem",
    "isso",
    "pelo",
    "pela",
    "seja",
    "favor",
    "preciso",
    "quero",
    "agora",
    "depois",
    "antes",
    "escreva",
    "faca",
    "obrigado",
)


# Constraint extractor markers, grouped by family then category.
EXTRACTOR_LEXICON = {
    "constraints": {
        "word-limit": (
            "palavras",
            "palavra",
            "limite de palavras",
            "no maximo",
            "nao mais de",
            "caracteres",
        ),
        "max-bullets": ("marcadores", "pontos", "elementos", "itens"),
        "briefly": ("brevemente", "breve", "em resumo", "rapidamente"),
        "concisely": ("conciso", "concisa", "sem rodeios", "direto ao ponto"),
    },
    "registers": {
        "executive": ("executivo", "direcao", "comite", "conselho"),
        "consultant": ("consultor", "consultoria", "senior"),
        "technical": ("tecnico", "tecnica", "engenharia"),
        "plain": ("didatico", "simples", "acessivel"),
    },
    "tones": {
        "formal": ("formal", "oficial", "institucional"),
        "neutral": ("neutro", "neutral", "factual", "objetivo"),
        "dynamic": ("dinamico", "impactante", "energico"),
        "synthetic": ("sintetico", "condensado", "comprimido"),
    },
    "depths": {
        "brief": ("panorama", "alto nivel", "vista geral"),
        "medium": ("padrao", "normal", "medio", "intermediario"),
        "detailed": ("completo", "completa", "exaustivo", "integral"),
        "expert": (
            "detalhado",
            "detalhada",
            "em profundidade",
            "aprofundado",
            "especialista",
            "nivel especialista",
            "avancado",
        ),
    },
    "formats": {
        "table": ("tabela", "grade", "matriz", "colunas"),
        "list": ("lista", "enumeracao", "marcadores"),
        "plan": ("plano", "roteiro", "etapas", "cronograma"),
        "analysis": ("analise", "diagnostico", "auditoria"),
        "synthesis": ("sintese", "resumo", "nota"),
    },
    "targets": {
        "client": ("cliente", "clientes", "prospecto", "usuario"),
        "team": ("equipe", "equipa", "colega", "colegas", "interno"),
        "management": ("direcao", "comite", "diretoria", "conselho"),
        "system": ("sistema", "servidor", "api", "modulo", "script"),
    },
}
