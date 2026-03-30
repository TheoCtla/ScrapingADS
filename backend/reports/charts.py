"""
Génération de graphiques matplotlib pour les rapports PPTX.
Tous les graphiques sont conçus pour être affichés sur fond noir (dark theme Tarmaac).
"""

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from typing import List, Dict, Any, Optional

from backend.reports.styles import INVERSE_METRICS


# ──────────────────────────────────────────────
# Style global matplotlib (dark theme)
# ──────────────────────────────────────────────

def setup_chart_style():
    """Configure matplotlib pour le dark theme Tarmaac."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Calibri", "Arial", "DejaVu Sans"],
        "text.color": "white",
        "axes.labelcolor": "white",
        "axes.edgecolor": "#3D3D3D",
        "xtick.color": "#B0B0B0",
        "ytick.color": "#B0B0B0",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "#000000",
        "axes.facecolor": "#000000",
        "figure.dpi": 150,
        "savefig.facecolor": "#000000",
    })


def _safe_float(value) -> float:
    """Convertit une valeur en float, retourne 0.0 si impossible."""
    if value is None:
        return 0.0
    try:
        if isinstance(value, str):
            value = value.replace("%", "").replace(",", ".").replace("\u00a0", "").replace(" ", "")
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_bar_value(value: float) -> str:
    """Formate une valeur pour l'affichage au-dessus d'une barre."""
    if value == 0:
        return "0"
    if value == int(value):
        formatted = f"{int(value):,}".replace(",", " ")
    elif value < 10:
        formatted = f"{value:.2f}".replace(".", ",")
    else:
        formatted = f"{value:,.0f}".replace(",", " ")
    return formatted


# ──────────────────────────────────────────────
# 1. Bar chart comparatif M vs M-1
# ──────────────────────────────────────────────

def create_comparison_bar_chart(
    current_values: List[float],
    previous_values: List[float],
    labels: List[str],
    current_label: str,
    previous_label: str,
    output_path: str,
) -> None:
    """Bar chart groupé comparant M vs M-1 — un subplot par métrique, chacun avec sa propre échelle."""
    setup_chart_style()

    current_values = [_safe_float(v) for v in current_values]
    previous_values = [_safe_float(v) for v in previous_values]

    n = len(labels)

    if n == 0 or not current_values:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", color="white", fontsize=14)
        ax.axis("off")
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        return

    fig, axes = plt.subplots(1, n, figsize=(3 * n, 4))
    if n == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        x = np.arange(2)
        vals = [previous_values[i], current_values[i]]
        colors = ["#3D3D3D", "#FFC107"]
        edge_colors = ["#5A5A5A", "#E3C417"]
        bar_labels = [previous_label, current_label]

        bars = ax.bar(x, vals, width=0.6, color=colors, edgecolor=edge_colors, linewidth=0.8)

        # Valeurs au-dessus des barres
        for j, bar in enumerate(bars):
            h = bar.get_height()
            text_color = "#B0B0B0" if j == 0 else "white"
            ax.text(
                bar.get_x() + bar.get_width() / 2, h,
                _format_bar_value(h),
                ha="center", va="bottom", fontsize=10, color=text_color, fontweight="bold",
            )

        ax.set_xticks(x)
        ax.set_xticklabels(bar_labels, fontsize=8)
        ax.set_title(labels[i], fontsize=12, color="white", fontweight="bold", pad=8)
        ax.grid(axis="y", color="#2D2D2D", linewidth=0.5, alpha=0.5)
        ax.set_axisbelow(True)

        # Marge Y pour les valeurs au-dessus
        y_max = max(vals) if max(vals) > 0 else 1
        ax.set_ylim(bottom=0, top=y_max * 1.25)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


# ──────────────────────────────────────────────
# 2. Donut répartition budget par plateforme
# ──────────────────────────────────────────────

def create_budget_donut(
    google_cost: float,
    meta_cost: float,
    output_path: str,
    microsoft_cost: float = 0,
) -> None:
    """Donut chart répartition budget par plateforme (Google, Meta, Microsoft si présent)."""
    setup_chart_style()

    google_cost = _safe_float(google_cost)
    meta_cost = _safe_float(meta_cost)
    microsoft_cost = _safe_float(microsoft_cost)
    total = google_cost + meta_cost + microsoft_cost

    if total == 0:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", color="white", fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        return

    values = []
    labels = []
    colors = []
    costs = []

    if google_cost > 0:
        values.append(google_cost)
        labels.append("Google Ads")
        colors.append("#4CAF50")
        costs.append(google_cost)
    if meta_cost > 0:
        values.append(meta_cost)
        labels.append("Meta Ads")
        colors.append("#03A9F4")
        costs.append(meta_cost)
    if microsoft_cost > 0:
        values.append(microsoft_cost)
        labels.append("Microsoft Ads")
        colors.append("#FF9800")
        costs.append(microsoft_cost)

    fig, ax = plt.subplots(figsize=(4, 4))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.0f%%",
        startangle=90,
        pctdistance=0.78,
        wedgeprops={"width": 0.4, "edgecolor": "none"},
    )

    for text in texts:
        text.set_color("white")
        text.set_fontsize(10)

    # % + montant en dessous
    for i, autotext in enumerate(autotexts):
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(9)
        cost_str = f"{costs[i]:,.0f} €".replace(",", " ")
        autotext.set_text(f"{autotext.get_text()}\n{cost_str}")

    # Total au centre
    total_str = f"{total:,.0f} €".replace(",", " ")
    ax.text(0, 0, total_str, ha="center", va="center", fontsize=18, fontweight="bold", color="white")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


# ──────────────────────────────────────────────
# 3. KPI comparison horizontal
# ──────────────────────────────────────────────

def create_kpi_comparison_chart(
    metrics_data: List[Dict[str, Any]],
    output_path: str,
) -> None:
    """
    Chart horizontal montrant les variations M vs M-1.
    metrics_data = [{"label": "Coût Google", "current": 580, "previous": 520}, ...]
    """
    setup_chart_style()

    if not metrics_data:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", color="white", fontsize=14)
        ax.axis("off")
        plt.savefig(output_path, dpi=150, transparent=True, bbox_inches="tight")
        plt.close()
        return

    labels = []
    variations = []
    colors = []

    for item in metrics_data:
        label = item.get("label", "")
        current = _safe_float(item.get("current", 0))
        previous = _safe_float(item.get("previous", 0))

        if previous == 0:
            var_pct = 100.0 if current > 0 else 0.0
        else:
            var_pct = ((current - previous) / abs(previous)) * 100

        # Déterminer si c'est une amélioration
        is_inverse = label in INVERSE_METRICS
        if is_inverse:
            is_positive = var_pct <= 0  # baisse = bien pour CPC/CPL
        else:
            is_positive = var_pct >= 0  # hausse = bien pour clics, impressions

        labels.append(label)
        variations.append(var_pct)
        colors.append("#4CAF50" if is_positive else "#FF5252")

    y = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(6, max(3, len(labels) * 0.6)))

    ax.barh(y, variations, color=colors, edgecolor="none", height=0.5)

    # Valeurs à côté des barres
    for i, (v, c) in enumerate(zip(variations, colors)):
        sign = "+" if v > 0 else ""
        ax.text(
            v + (1 if v >= 0 else -1), i,
            f"{sign}{v:.1f}%",
            ha="left" if v >= 0 else "right",
            va="center", fontsize=9, color=c,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.axvline(x=0, color="#3D3D3D", linewidth=0.8)
    ax.grid(axis="x", color="#2D2D2D", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.invert_yaxis()

    # Marge pour les labels de %
    x_max = max(abs(v) for v in variations) if variations else 10
    ax.set_xlim(-x_max * 1.4, x_max * 1.4)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


# ──────────────────────────────────────────────
# 4. Donut répartition budget Google par canal
# ──────────────────────────────────────────────

def create_platform_breakdown_chart(
    search_cost: float,
    pmax_cost: float,
    display_cost: float,
    output_path: str,
) -> None:
    """Donut répartition budget Google par canal (Search, PMax, Display)."""
    setup_chart_style()

    search_cost = _safe_float(search_cost)
    pmax_cost = _safe_float(pmax_cost)
    display_cost = _safe_float(display_cost)

    values = []
    labels = []
    colors = []

    if search_cost > 0:
        values.append(search_cost)
        labels.append("Search")
        colors.append("#FFC107")
    if pmax_cost > 0:
        values.append(pmax_cost)
        labels.append("Perf Max")
        colors.append("#FF9800")
    if display_cost > 0:
        values.append(display_cost)
        labels.append("Display")
        colors.append("#402386")

    if not values:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", color="white", fontsize=14)
        ax.axis("off")
        plt.savefig(output_path, dpi=150, transparent=True, bbox_inches="tight")
        plt.close()
        return

    total = sum(values)

    fig, ax = plt.subplots(figsize=(4, 4))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.0f%%",
        startangle=90,
        pctdistance=0.78,
        wedgeprops={"width": 0.4, "edgecolor": "none"},
    )

    for text in texts:
        text.set_color("white")
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")

    # Total au centre
    total_str = f"{total:,.0f} €".replace(",", " ")
    ax.text(0, 0, total_str, ha="center", va="center", fontsize=18, fontweight="bold", color="white")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


# ──────────────────────────────────────────────
# 5. Line chart évolution (1 métrique, 3 mois)
# ──────────────────────────────────────────────

def create_evolution_line_chart(
    history: List[Dict[str, Any]],
    metric_key: str,
    chart_title: str,
    output_path: str,
    line_color: str = None,
) -> None:
    """
    Line chart montrant l'évolution d'une seule métrique sur les derniers mois.

    Args:
        history: Liste de dicts triés chronologiquement, chaque dict a "month_fr" et la métrique.
        metric_key: Nom de colonne Sheet à tracer.
        chart_title: Titre affiché au-dessus du graphique.
        output_path: Chemin du PNG de sortie.
    """
    setup_chart_style()

    if not history:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", color="white", fontsize=14)
        ax.axis("off")
        plt.savefig(output_path, dpi=150, transparent=True, bbox_inches="tight")
        plt.close()
        return

    months = [entry.get("month_fr", "") for entry in history]
    values = [_safe_float(entry.get(metric_key, 0)) for entry in history]

    fig, ax = plt.subplots(figsize=(5, 3))

    ax.plot(
        months, values,
        "o-", color="#FFC107", markersize=8, linewidth=2,
        markeredgecolor="#E3C417", markerfacecolor="#FFC107",
    )

    # Valeurs au-dessus de chaque point
    for i, (x, y) in enumerate(zip(months, values)):
        display_val = _format_bar_value(y)
        ax.text(
            i, y, display_val,
            ha="center", va="bottom", fontsize=12, color="white",
            fontweight="bold",
        )

    ax.set_title(chart_title, fontsize=14, color="white", fontweight="bold", pad=10)
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, fontsize=10)
    ax.grid(axis="y", color="#2D2D2D", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)

    # Ajuster les limites Y pour laisser de la place aux labels
    if values:
        y_max = max(values) if max(values) > 0 else 1
        ax.set_ylim(bottom=0, top=y_max * 1.25)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
