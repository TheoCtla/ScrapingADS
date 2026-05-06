"""
Constantes de design et fonctions de formatage pour les rapports PPTX.
Palette Tarmaac — dark theme issu des templates Google Slides existants.
"""

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


# ──────────────────────────────────────────────
# Palette Tarmaac (branding réel de l'agence)
# ──────────────────────────────────────────────

PALETTE = {
    "black": "000000",          # fond principal de toutes les slides
    "gold": "FFC107",           # accent principal, bannières, titres accentués
    "dark_gold": "E3C417",      # variante or plus sombre
    "green": "4CAF50",          # Google Ads, indicateurs positifs
    "light_blue": "03A9F4",     # Meta Ads, CTR, CPL
    "orange": "FF9800",         # leads, clics, KPIs de volume
    "purple": "402386",         # bannières secondaires
    "blue_accent": "56AEFF",    # accents légers, dates
    "white": "FFFFFF",          # texte principal et valeurs
    "dark_gray": "1A1A1A",      # fond alternatif légèrement plus clair
    "medium_gray": "2D2D2D",    # fonds de cartes KPI sur fond noir
    "light_gray": "3D3D3D",     # bordures subtiles sur fond sombre
    "text_secondary": "B0B0B0", # texte secondaire/légendes sur fond noir
}

# ──────────────────────────────────────────────
# Couleurs fonctionnelles
# ──────────────────────────────────────────────

FUNCTIONAL_COLORS = {
    "google_color": "4285F4",   # logo/identité Google
    "meta_color": "0668E1",     # logo/identité Meta
    "positive": "4CAF50",       # tendance positive
    "negative": "FF5252",       # tendance négative (rouge vif, lisible sur noir)
    "neutral": "B0B0B0",        # pas de changement
    "chart_1": "FFC107",        # or — première série graphique
    "chart_2": "03A9F4",        # bleu clair — deuxième série
    "chart_3": "FF9800",        # orange — troisième série
    "chart_4": "4CAF50",        # vert — quatrième série
}

# ──────────────────────────────────────────────
# Typographie
# ──────────────────────────────────────────────

FONT_TITLE = "Calibri"
FONT_BODY = "Calibri Light"

FONT_SIZES = {
    "slide_title": Pt(36),
    "section_title": Pt(24),
    "kpi_value": Pt(48),
    "kpi_label": Pt(14),
    "body": Pt(14),
    "caption": Pt(10),
    "tooltip": Pt(9),
    "comparison": Pt(12),
}

# ──────────────────────────────────────────────
# Dimensions (slides 16:9)
# ──────────────────────────────────────────────

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)
MARGIN = Inches(0.5)

KPI_CARD_WIDTH = Inches(2.8)
KPI_CARD_HEIGHT = Inches(1.8)
KPI_CARD_SPACING = Inches(0.3)

CHART_WIDTH = Inches(5.5)
CHART_HEIGHT = Inches(3.5)

# ──────────────────────────────────────────────
# Infobulles métriques
# ──────────────────────────────────────────────

METRIC_TOOLTIPS = {
    "CPC": "Coût par clic → combien vous payez en moyenne pour un clic",
    "CTR": "Taux de clic → % de personnes qui cliquent après avoir vu l'annonce",
    "CPL": "Coût par lead → coût moyen d'acquisition d'un contact",
    "Impressions": "Nombre de fois que vos annonces ont été affichées",
    "CPC Search": "Coût par clic sur les campagnes de recherche Google",
    "CPC Perf Max": "Coût par clic sur les campagnes Performance Max",
    "CPC Display": "Coût par clic sur les campagnes Display Google",
    "CPC Meta": "Coût par clic sur les publicités Meta",
    "CPL Meta": "Coût par lead sur les publicités Meta",
    "CTR Google": "Taux de clic sur les campagnes Google Ads",
    "CTR Meta": "Taux de clic sur les publicités Meta",
    "Total CPC moyen": "Coût par clic moyen toutes campagnes Google confondues",
    "Appels Téléphoniques": "Nombre de clics trackés sur les boutons contacts",
    "Demandes d'itinéraires": "Nombre de clics trackés sur les boutons itinéraires",
    "Formulaires": "Nombre de formulaires remplis par les prospects",
    "Contact Meta": "Nombre de clics trackés sur les boutons contacts",
    "Recherche de lieux": "Nombre de recherches d'itinéraire via Meta",
    "Cout par RDV / Form": "Coût total des campagnes divisé par le nombre de formulaires",
    "Cout par conversion majeure": "Coût total divisé par le nombre total de conversions (formulaires + contacts + itinéraires)",
    "Cout Google ADS": "Budget total dépensé sur Google Ads",
    "Cout Facebook ADS": "Budget total dépensé sur Meta Ads",
    "Cout Search": "Budget dépensé sur les campagnes Search Google",
    "Cout PM": "Budget dépensé sur les campagnes Performance Max",
    "Cout Display": "Budget dépensé sur les campagnes Display Google",
    "Clics search": "Nombre de clics sur les campagnes Search Google. Ces campagnes affichent vos annonces textuelles lorsqu'un utilisateur recherche vos mots-clés sur Google.",
    "Clics Perf Max": "Nombre de clics sur les campagnes Performance Max. Ces campagnes diffusent automatiquement vos annonces sur tous les canaux Google (YouTube, Maps..).",
    "Clics Display": "Nombre de clics sur les campagnes Display Google",
    "Clics Meta": "Nombre de clics sur les publicités Meta",
    "Impressions Search": "Nombre d'impressions sur les campagnes Search Google",
    "Impressions Perf Max": "Nombre d'impressions sur les campagnes Performance Max",
    "Impressions Meta": "Nombre d'impressions sur les publicités Meta",
    "Total Clic": "Nombre total de clics toutes campagnes Google confondues",
    "Total Impressions": "Nombre total d'impressions toutes campagnes Google confondues",
    "Diffusion All": "Impressions totales toutes plateformes confondues",
    "Clics All": "Clics totaux toutes plateformes confondues",
    "COUT ALL": "Budget total toutes plateformes confondues",
}

# ──────────────────────────────────────────────
# Métriques inversées (baisse = positif)
# ──────────────────────────────────────────────

INVERSE_METRICS = {
    "CPC",
    "CPL",
    "CPC Search",
    "CPC Meta",
    "CPL Meta",
    "CPC Perf Max",
    "CPC Display",
    "Total CPC moyen",
    "Cout par RDV / Form",
    "Cout par conversion majeure",
}

# ──────────────────────────────────────────────
# Catégorisation des métriques par section
# ──────────────────────────────────────────────

GOOGLE_METRICS = {
    "Cout Google ADS", "Clics search", "Clics Perf Max", "Clics Display",
    "Impressions Search", "Impressions Perf Max", "Impressions Display",
    "CPC Search", "Cout Search", "Cout PM", "Cout Display",
    "Total Clic", "Total Impressions", "Total CPC moyen", "CTR Google",
    "Contact", "Itinéraires",
}

META_METRICS = {
    "Cout Facebook ADS", "Clics Meta", "Impressions Meta",
    "CTR Meta", "CPL Meta", "CPC Meta", "Contact Meta", "Recherche de lieux",
}

CONVERSION_METRICS = {
    "Appels Téléphoniques", "Demandes d'itinéraires", "Demande d'itineraires",
    "Formulaires", "Contact Meta", "Recherche de lieux",
}

GENERAL_METRICS = {
    "Cout par RDV / Form", "Cout par conversion majeure",
    "COUT ALL", "Diffusion All", "Clics All",
    "Leads Google", "Leads Meta", "Leads Générés", "Leads Qualifiés",
    "Coût par Leads",
    "Montant", "Ajout au panier", "CTR",
    "Montant DTS", "Itinéraires", "CTR DTS",
    "Montant SP", "CTR SP",
}

MICROSOFT_METRICS = {
    "Cout Microsoft ADS", "Clics Micro", "Impressions Micro",
    "CPC Micro",
}

# Colonnes à ignorer dans le Sheet
IGNORED_COLUMNS = {"RDV CALENDLY", "RDV FOC"}


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def hex_to_rgb(hex_str: str) -> RGBColor:
    """Convertit un hex string (sans #) en RGBColor."""
    hex_str = hex_str.lstrip("#")
    return RGBColor(
        int(hex_str[0:2], 16),
        int(hex_str[2:4], 16),
        int(hex_str[4:6], 16),
    )


def format_currency(value, currency: str = "€", decimals: bool = True) -> str:
    """Formate en devise : 1 234,56 € (ou 1 235 € sans centimes)."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return f"0 {currency}" if not decimals else f"0,00 {currency}"
    if decimals:
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", " ").replace(".", ",")
    else:
        formatted = f"{round(value):,}".replace(",", " ")
    return f"{formatted} {currency}"


def format_number(value) -> str:
    """Formate un nombre entier : 12 450"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "0"
    if value == int(value):
        formatted = f"{int(value):,}"
    else:
        formatted = f"{value:,.1f}"
    return formatted.replace(",", " ").replace(".", ",")


def format_percentage(value) -> str:
    """
    Formate un pourcentage.
    Gère les deux cas : 0.0275 → '2,75%' et '2.75%' → '2,75%'
    """
    try:
        if isinstance(value, str):
            value = value.replace("%", "").replace(",", ".").strip()
            value = float(value)
            # Si la valeur string contenait déjà un %, elle est déjà en %
            # Sinon on la traite comme un ratio
        else:
            value = float(value)

        # Si la valeur est < 1, c'est probablement un ratio (0.0275 = 2.75%)
        if abs(value) < 1:
            value = value * 100

        formatted = f"{value:.2f}".replace(".", ",")
        return f"{formatted}%"
    except (TypeError, ValueError):
        return "0,00%"


def calc_variation(current, previous) -> tuple:
    """
    Calcule la variation entre deux valeurs.
    Retourne (variation_pct: float, direction: str).
    direction = "up" | "down" | "neutral"
    """
    try:
        current = float(current)
        previous = float(previous)
    except (TypeError, ValueError):
        return (0.0, "neutral")

    if previous == 0:
        if current > 0:
            return (100.0, "up")
        return (0.0, "neutral")

    variation = ((current - previous) / abs(previous)) * 100

    if abs(variation) < 0.01:
        return (0.0, "neutral")
    elif variation > 0:
        return (round(variation, 1), "up")
    else:
        return (round(abs(variation), 1), "down")
