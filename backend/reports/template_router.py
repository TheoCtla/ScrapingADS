"""
Routage client → template PPTX.
Reproduit la logique du blueprint Make : le nom de l'onglet Sheet
détermine quel template utiliser pour générer le rapport.
"""

import logging
from typing import Type

from backend.reports.templates.base import BaseTemplate


# ──────────────────────────────────────────────
# Définition des routes (ordre = priorité)
# ──────────────────────────────────────────────

TEMPLATE_ROUTES = [
    {
        "name": "sachs",
        "keywords": ["sachs"],
        "template": "template_sachs",
    },
    {
        "name": "lyleoo",
        "keywords": ["lyle"],
        "template": "template_lyleoo",
    },
    {
        "name": "cuisinistes",
        "keywords": ["aviva", "addario", "cuisine"],
        "template": "template_cuisinistes",
    },
    {
        "name": "litiers",
        "keywords": ["fl", "meuble", "salon", "literie", "contemporaine", "roche"],
        "template": "template_litiers",
    },
    {
        "name": "leadgen",
        "keywords": ["kaltea", "kozeo", "tairmic"],
        "template": "template_leadgen",
    },
    {
        "name": "denteva",
        "keywords": ["denteva"],
        "template": "template_denteva",
    },
    {
        "name": "laserel",
        "keywords": ["laserel"],
        "template": "template_laserel",
    },
    {
        "name": "evopro",
        "keywords": ["evo"],
        "template": "template_evopro",
    },
    {
        "name": "crozatier",
        "keywords": ["crozatier"],
        "template": "template_cuisinistes",
    },
    {
        "name": "bedroom",
        "keywords": ["bedroom"],
        "template": "template_bedroom",
    },
    {
        "name": "emma",
        "keywords": ["emma"],
        "template": "template_emma",
    },
]

FALLBACK_TEMPLATE = "template_leadgen"


# ──────────────────────────────────────────────
# Templates implémentés (les autres lèvent NotImplementedError)
# ──────────────────────────────────────────────

_IMPLEMENTED_TEMPLATES = {
    "template_litiers",
    "template_sachs",
    "template_lyleoo",
    "template_evopro",
    "template_cuisinistes",
    "template_emma",
    "template_laserel",
    "template_denteva",
    "template_leadgen",
    "template_bedroom",
}


def _match_route(sheet_name: str) -> str:
    """Retourne le nom du template correspondant à un onglet Sheet."""
    lower_name = sheet_name.lower()
    for route in TEMPLATE_ROUTES:
        for keyword in route["keywords"]:
            if keyword in lower_name:
                return route["template"]
    return FALLBACK_TEMPLATE


def _load_template_class(template_name: str) -> Type[BaseTemplate]:
    """Import dynamique de la classe template."""
    if template_name == "template_litiers":
        from backend.reports.templates.template_litiers import TemplateModern
        return TemplateModern

    if template_name == "template_sachs":
        from backend.reports.templates.template_sachs import TemplateSachs
        return TemplateSachs

    if template_name == "template_lyleoo":
        from backend.reports.templates.template_lyleoo import TemplateLyleoo
        return TemplateLyleoo

    if template_name == "template_evopro":
        from backend.reports.templates.template_evopro import TemplateEvopro
        return TemplateEvopro

    if template_name == "template_cuisinistes":
        from backend.reports.templates.template_cuisinistes import TemplateCuisinistes
        return TemplateCuisinistes

    if template_name == "template_emma":
        from backend.reports.templates.template_emma import TemplateEmma
        return TemplateEmma

    if template_name == "template_laserel":
        from backend.reports.templates.template_laserel import TemplateLaserel
        return TemplateLaserel

    if template_name == "template_denteva":
        from backend.reports.templates.template_denteva import TemplateDenteva
        return TemplateDenteva

    if template_name == "template_bedroom":
        from backend.reports.templates.template_bedroom import TemplateBedroom
        return TemplateBedroom

    if template_name == "template_leadgen":
        from backend.reports.templates.template_leadgen import TemplateLeadGen
        return TemplateLeadGen

    raise NotImplementedError(
        f"Le template '{template_name}' n'est pas encore implémenté. "
        f"Templates disponibles : {_IMPLEMENTED_TEMPLATES}"
    )


def resolve_template(sheet_name: str) -> Type[BaseTemplate]:
    """
    Résout le template PPTX à utiliser pour un onglet Sheet.

    Args:
        sheet_name: Nom de l'onglet dans le Google Sheet.

    Returns:
        Classe template (non instanciée) à utiliser pour ce client.

    Raises:
        NotImplementedError: Si le template requis n'est pas encore codé.
    """
    template_name = _match_route(sheet_name)
    logging.info(f"Onglet '{sheet_name}' → template '{template_name}'")
    return _load_template_class(template_name)


def get_route_name(sheet_name: str) -> str:
    """Retourne le nom de la route pour un onglet (pour le logging)."""
    lower_name = sheet_name.lower()
    for route in TEMPLATE_ROUTES:
        for keyword in route["keywords"]:
            if keyword in lower_name:
                return route["name"]
    return "leadgen"


def is_template_implemented(sheet_name: str) -> bool:
    """Vérifie si le template pour cet onglet est implémenté."""
    template_name = _match_route(sheet_name)
    return template_name in _IMPLEMENTED_TEMPLATES
