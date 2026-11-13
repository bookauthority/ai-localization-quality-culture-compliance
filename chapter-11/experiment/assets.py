from typing import Dict, List

# Simplified in-memory translation memories (TMs), termbases, and style
# examples. In a real system these would be loaded from TMX/TBX/CSV/etc.

# Translation memories are keyed by language pair, then a list of entries.
# Each entry includes source, target, and an optional domain.

TMS: Dict[str, List[Dict[str, str]]] = {
    "en->fr": [
        {
            "source": "Welcome to CloudSync, the secure way to protect your data.",
            "target": "Bienvenue dans CloudSync, le moyen sécurisé de protéger vos données.",
            "domain": "marketing",
        },
        {
            "source": "CloudSync keeps your files safe across every device.",
            "target": "CloudSync garde vos fichiers en sécurité sur tous vos appareils.",
            "domain": "marketing",
        },
    ],
    "en->es": [
        {
            "source": "Open CloudSync settings",
            "target": "Abrir la configuración de CloudSync",
            "domain": "ui",
        },
        {
            "source": "CloudSync backup failed. Try again.",
            "target": "La copia de seguridad de CloudSync falló. Inténtalo de nuevo.",
            "domain": "ui",
        },
    ],
    "en->de": [
        {
            "source": "CloudSync stores encrypted copies of your files in our data centers.",
            "target": "CloudSync speichert verschlüsselte Kopien Ihrer Dateien in unseren Rechenzentren.",
            "domain": "kb",
        },
        {
            "source": "CloudSync Pro customers can contact premium support via chat.",
            "target": "CloudSync Pro-Kunden können den Premium-Support per Chat kontaktieren.",
            "domain": "kb",
        },
    ],
}

# Termbase entries include required (preferred) target terms and forbidden
# alternatives. Non-translatable product names are also listed.

TERMBASE: List[Dict[str, str]] = [
    {
        "language_pair": "en->fr",
        "source_term": "CloudSync",
        "target_term": "CloudSync",
        "status": "preferred",
        "forbidden_flag": "0",
    },
    {
        "language_pair": "en->fr",
        "source_term": "CloudSync Pro",
        "target_term": "CloudSync Pro",
        "status": "preferred",
        "forbidden_flag": "0",
    },
    {
        "language_pair": "en->es",
        "source_term": "CloudSync",
        "target_term": "CloudSync",
        "status": "preferred",
        "forbidden_flag": "0",
    },
    {
        "language_pair": "en->es",
        "source_term": "CloudSync Pro",
        "target_term": "CloudSync Pro",
        "status": "preferred",
        "forbidden_flag": "0",
    },
    {
        "language_pair": "en->de",
        "source_term": "CloudSync",
        "target_term": "CloudSync",
        "status": "preferred",
        "forbidden_flag": "0",
    },
    {
        "language_pair": "en->de",
        "source_term": "CloudSync Pro",
        "target_term": "CloudSync Pro",
        "status": "preferred",
        "forbidden_flag": "0",
    },
]

FORBIDDEN_TERMS: List[Dict[str, str]] = [
    {
        "language_pair": "en->fr",
        "source_term": "Cloud Sync",
        "target_term": "Cloud Sync",
        "status": "forbidden",
        "forbidden_flag": "1",
    },
    {
        "language_pair": "en->es",
        "source_term": "Cloud Sync",
        "target_term": "Cloud Sync",
        "status": "forbidden",
        "forbidden_flag": "1",
    },
    {
        "language_pair": "en->de",
        "source_term": "Cloud Sync",
        "target_term": "Cloud Sync",
        "status": "forbidden",
        "forbidden_flag": "1",
    },
]

NON_TRANSLATABLES: List[str] = [
    "CloudSync",
    "CloudSync Pro",
]

# Style examples emulate a vector-searchable corpus where each entry contains
# a source, target, language pair, and domain tag.

STYLE_EXAMPLES: List[Dict[str, str]] = [
    {
        "language_pair": "en->fr",
        "domain": "marketing",
        "source": "Sync your world with CloudSync.",
        "target": "Synchronisez votre univers avec CloudSync.",
    },
    {
        "language_pair": "en->es",
        "domain": "ui",
        "source": "Start CloudSync backup now",
        "target": "Iniciar la copia de seguridad de CloudSync ahora",
    },
    {
        "language_pair": "en->de",
        "domain": "kb",
        "source": "CloudSync automatically saves your changes.",
        "target": "CloudSync speichert Ihre Änderungen automatisch.",
    },
]

# Thresholds mimic those in the original spec but are adapted for this
# simplified environment.

TM_MATCH_THRESHOLDS = {
    "exact": 1.0,  # normalized similarity 1.0
    "high_fuzzy_min": 0.85,
    "low_fuzzy_min": 0.75,
}

VECTOR_SIMILARITY_THRESHOLD = 0.8
VECTOR_TOP_K = 3
