"""
Lecture des données du Google Sheet pour alimenter les rapports PPTX.
Lit le mois M, M-1, et l'historique des 3 derniers mois.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.reports.styles import (
    GOOGLE_METRICS, META_METRICS, CONVERSION_METRICS,
    GENERAL_METRICS, MICROSOFT_METRICS, IGNORED_COLUMNS,
)

# ──────────────────────────────────────────────
# Mapping mois EN ↔ FR
# ──────────────────────────────────────────────

MONTHS_EN_TO_FR = {
    "January": "Janvier",
    "February": "Février",
    "March": "Mars",
    "April": "Avril",
    "May": "Mai",
    "June": "Juin",
    "July": "Juillet",
    "August": "Août",
    "September": "Septembre",
    "October": "Octobre",
    "November": "Novembre",
    "December": "Décembre",
}

MONTHS_FR_TO_EN = {v: k for k, v in MONTHS_EN_TO_FR.items()}


def _month_to_en(month_str: str) -> str:
    """Convertit un mois FR en EN si nécessaire. Ex: 'Mars 2026' → 'March 2026'."""
    for fr, en in MONTHS_FR_TO_EN.items():
        if fr.lower() in month_str.lower():
            return month_str.replace(fr, en).replace(fr.lower(), en)
    return month_str


def _month_to_fr(month_str: str) -> str:
    """Convertit un mois EN en FR. Ex: 'March 2026' → 'Mars 2026'."""
    for en, fr in MONTHS_EN_TO_FR.items():
        if en.lower() in month_str.lower():
            return month_str.replace(en, fr).replace(en.lower(), fr)
    return month_str


def _parse_month(month_str: str) -> Optional[datetime]:
    """Parse 'March 2026' ou 'Mars 2026' en datetime."""
    en_month = _month_to_en(month_str)
    try:
        return datetime.strptime(en_month.strip(), "%B %Y")
    except ValueError:
        logging.warning(f"⚠️ Impossible de parser le mois : '{month_str}'")
        return None


def _previous_month_str(month_str: str) -> str:
    """Retourne le mois précédent en anglais. Ex: 'March 2026' → 'February 2026'."""
    dt = _parse_month(month_str)
    if not dt:
        return ""
    if dt.month == 1:
        prev = dt.replace(year=dt.year - 1, month=12)
    else:
        prev = dt.replace(month=dt.month - 1)
    return prev.strftime("%B %Y")


def _parse_value(value: str) -> Any:
    """Convertit une valeur string du Sheet en float/int quand c'est numérique."""
    if value is None or value == "":
        return 0

    if isinstance(value, (int, float)):
        return value

    cleaned = str(value).strip()

    # Gérer les pourcentages
    if cleaned.endswith("%"):
        try:
            return cleaned  # Garder les pourcentages comme strings
        except ValueError:
            return 0

    # Gérer les séparateurs de milliers et décimales
    # Le Sheet peut avoir des formats variés : "1,234.56" ou "1234.56" ou "1 234,56"
    cleaned = cleaned.replace("\u00a0", "").replace(" ", "")

    # Si contient virgule et point, la virgule est séparateur de milliers
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    # Si contient uniquement une virgule, c'est le séparateur décimal
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        num = float(cleaned)
        if num == int(num) and "." not in str(value):
            return int(num)
        return num
    except ValueError:
        return value  # Retourner tel quel si pas numérique


def _row_to_dict(headers: List[str], row: List[str]) -> Dict[str, Any]:
    """Convertit une ligne du Sheet en dict {header: valeur parsée}."""
    result = {}
    for i, header in enumerate(headers):
        if not header or header.strip() in IGNORED_COLUMNS:
            continue
        raw_value = row[i] if i < len(row) else ""
        result[header.strip()] = _parse_value(raw_value)
    return result


def _categorize_metrics(flat_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Sépare un dict plat en google_ads / meta_ads / microsoft_ads / conversions / general."""
    google = {}
    meta = {}
    microsoft = {}
    conversions = {}
    general = {}

    for key, value in flat_dict.items():
        if key in ("Mois", "month", "month_fr"):
            continue
        if key in GOOGLE_METRICS:
            google[key] = value
        if key in META_METRICS:
            meta[key] = value
        if key in MICROSOFT_METRICS:
            microsoft[key] = value
        if key in CONVERSION_METRICS:
            conversions[key] = value
        if key in GENERAL_METRICS:
            general[key] = value

    return {
        "google_ads": google,
        "meta_ads": meta,
        "microsoft_ads": microsoft,
        "conversions": conversions,
        "general": general,
    }


def _resolve_worksheet_name(
    client_name: str,
    available_sheets: List[str],
) -> Optional[str]:
    """
    Résout le nom de l'onglet pour un client.
    Logique : mapping Google → mapping Meta → nom du client directement.
    """
    try:
        from backend.google_ads_wrapper.utils.mappings import GoogleAdsMappingService
        from backend.meta.utils.mappings import MetaAdsMappingService
        from backend.common.services.client_resolver import ClientResolverService

        resolver = ClientResolverService()
        client_info = resolver.resolve_client_accounts(client_name)

        if not client_info:
            if client_name in available_sheets:
                return client_name
            return None

        # Essayer mapping Google
        google_customer_id = None
        if client_info.get("googleAds") and client_info["googleAds"].get("customerId"):
            google_customer_id = client_info["googleAds"]["customerId"]
            google_mappings = GoogleAdsMappingService()
            sheet_name = google_mappings.get_sheet_name_for_customer(google_customer_id)
            if sheet_name and sheet_name in available_sheets:
                return sheet_name

        # Essayer mapping Meta
        meta_account_id = None
        if client_info.get("metaAds") and client_info["metaAds"].get("adAccountId"):
            meta_account_id = client_info["metaAds"]["adAccountId"]
            meta_mappings = MetaAdsMappingService()
            sheet_name = meta_mappings.get_sheet_name_for_account(meta_account_id)
            if sheet_name and sheet_name in available_sheets:
                return sheet_name

        # Fallback : nom du client directement
        if client_name in available_sheets:
            return client_name

        logging.warning(f"⚠️ Aucun onglet trouvé pour le client '{client_name}'")
        return None

    except Exception as e:
        logging.error(f"❌ Erreur résolution onglet pour '{client_name}': {e}")
        # Fallback direct
        if client_name in available_sheets:
            return client_name
        return None


def read_report_data(client_name: str, month: str) -> Dict[str, Any]:
    """
    Lit les données du Google Sheet pour un client et un mois donné.
    Résout le nom d'onglet via les mappings client.

    Args:
        client_name: Nom du client (tel que dans client_allowlist.json)
        month: Mois en anglais, ex: 'March 2026'
    """
    from backend.common.services.google_sheets import GoogleSheetsService

    sheets_service = GoogleSheetsService()
    available_sheets = sheets_service.get_worksheet_names()

    worksheet_name = _resolve_worksheet_name(client_name, available_sheets)
    if not worksheet_name:
        raise ValueError(f"Onglet non trouvé pour le client '{client_name}'")

    month_en = _month_to_en(month)
    logging.info(f"Lecture des données pour '{client_name}' → onglet '{worksheet_name}'")

    data = _read_sheet_data(sheets_service, worksheet_name, month_en)
    data["client"] = client_name
    return data


def _read_sheet_data(
    sheets_service,
    worksheet_name: str,
    month_en: str,
) -> Dict[str, Any]:
    """
    Lecture brute d'un onglet Sheet : headers, lignes, catégorisation.
    Factorise la logique commune entre read_report_data et read_report_data_by_worksheet.
    """
    headers_range = f"'{worksheet_name}'!2:2"
    headers_result = sheets_service.service.spreadsheets().values().get(
        spreadsheetId=sheets_service.sheet_id,
        range=headers_range,
    ).execute()
    headers_raw = headers_result.get("values", [[]])
    headers = [h.strip() if h else "" for h in headers_raw[0]] if headers_raw else []

    if not headers:
        raise ValueError(f"Aucun header trouvé dans l'onglet '{worksheet_name}'")

    data_range = f"'{worksheet_name}'!A3:AK"
    data_result = sheets_service.service.spreadsheets().values().get(
        spreadsheetId=sheets_service.sheet_id,
        range=data_range,
    ).execute()
    rows = data_result.get("values", [])

    all_months: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not row or not row[0] or not row[0].strip():
            continue
        month_cell = row[0].strip()
        row_dict = _row_to_dict(headers, row)
        row_dict["month"] = month_cell
        row_dict["month_fr"] = _month_to_fr(month_cell)
        all_months[month_cell] = row_dict

    prev_month_en = _previous_month_str(month_en)
    current_data = all_months.get(month_en, {})
    previous_data = all_months.get(prev_month_en, {})

    if not current_data:
        logging.warning(f"Aucune donnée pour le mois '{month_en}' dans '{worksheet_name}'")

    sorted_months = []
    for m_str, m_data in all_months.items():
        dt = _parse_month(m_str)
        if dt:
            sorted_months.append((dt, m_str, m_data))
    sorted_months.sort(key=lambda x: x[0])

    current_dt = _parse_month(month_en)
    if current_dt:
        eligible = [(dt, name, data) for dt, name, data in sorted_months if dt <= current_dt]
        history_entries = eligible[-3:]
    else:
        history_entries = sorted_months[-3:]

    history = [entry[2] for entry in history_entries]

    current_cats = _categorize_metrics(current_data)
    previous_cats = _categorize_metrics(previous_data)

    month_fr = _month_to_fr(month_en)
    prev_month_fr = _month_to_fr(prev_month_en)

    return {
        "client": worksheet_name,
        "month": month_en,
        "month_fr": month_fr,
        "previous_month": prev_month_en,
        "previous_month_fr": prev_month_fr,
        "google_ads": {
            "current": current_cats["google_ads"],
            "previous": previous_cats["google_ads"],
        },
        "meta_ads": {
            "current": current_cats["meta_ads"],
            "previous": previous_cats["meta_ads"],
        },
        "microsoft_ads": {
            "current": current_cats["microsoft_ads"],
            "previous": previous_cats["microsoft_ads"],
        },
        "conversions": {
            "current": current_cats["conversions"],
            "previous": previous_cats["conversions"],
        },
        "general": {
            "current": current_cats["general"],
            "previous": previous_cats["general"],
        },
        "history": history,
    }


def read_report_data_by_worksheet(
    worksheet_name: str,
    month: str,
    sheets_service=None,
) -> Dict[str, Any]:
    """
    Lit les données d'un onglet Sheet directement par son nom (sans résolution client).
    Utilisé par le generator qui itère sur les onglets visibles.

    Args:
        worksheet_name: Nom exact de l'onglet dans le Sheet.
        month: Mois en anglais, ex: 'February 2026'.
        sheets_service: Instance GoogleSheetsService (optionnel, créé si absent).
    """
    if sheets_service is None:
        from backend.common.services.google_sheets import GoogleSheetsService
        sheets_service = GoogleSheetsService()

    month_en = _month_to_en(month)
    logging.info(f"Lecture des données pour l'onglet '{worksheet_name}' — mois '{month_en}'")

    return _read_sheet_data(sheets_service, worksheet_name, month_en)


def read_mock_data(template_key: str) -> Dict[str, Any]:
    """
    Lit les données mock depuis le fichier de test.

    Args:
        template_key: Clé du jeu de données (ex: 'google_meta_full_mock')

    Returns:
        Dict au même format que read_report_data()
    """
    mock_path = Path(__file__).parent / "tests" / "mock_data.json"
    try:
        with open(mock_path, "r", encoding="utf-8") as f:
            all_mocks = json.load(f)
        if template_key not in all_mocks:
            raise ValueError(
                f"Mock '{template_key}' non trouvé. Disponibles : {list(all_mocks.keys())}"
            )
        return all_mocks[template_key]
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier mock introuvable : {mock_path}")
