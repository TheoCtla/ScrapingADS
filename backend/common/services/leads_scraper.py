"""
Scraping automatique des leads depuis les sheets leads clients.
Lit les données brutes, compte les leads Google/Meta/Générés par mois,
et écrit les résultats dans le sheet principal du client.
"""

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Any, Optional

# Spreadsheet IDs des sheets leads (source)
LEADS_SHEETS = {
    "kozeo": {
        "spreadsheet_id": "1AZQsbPIn4_UDajcicIEQ7rdE4L-kNOeUS-69RZTejiM",
        "tab_name": "KOZÉO",
        "date_col": 26,      # AA (0-indexed = 26)
        "provenance_col": 7,  # H
        "statut_col": 8,      # I
        "q_col": 16,          # Q
        "r_col": 17,          # R
        "worksheet_name": "Kozeo",
    },
    "riviera_grass": {
        "spreadsheet_id": "1mUkL-p7PK9guPq4AnVozIcWAazTCp-1pLeJfoCvIY8M",
        "tab_name": "Riviera Grass Leads",
        "date_col": 0,       # A
        "provenance_col": 7,  # H
        "statut_col": 8,      # I
        "q_col": 16,          # Q (fbclid)
        "r_col": 17,          # R (gclid)
        "worksheet_name": "Riviera Grass",
    },
    "sud_gazon": {
        "spreadsheet_id": "1JUTWFvwhj3C72Zpk9hcjz3PUD1pxOD9TewcH-9aeNTs",
        "tab_name": "SudGazon Leads",
        "date_col": 0,       # A
        "provenance_col": 8,  # I
        "statut_col": 9,      # J
        "q_col": 17,          # R (fbclid)
        "r_col": 18,          # S (gclid)
        "worksheet_name": "SUD GAZON SYNTHETIQUE",
    },
    "univers_construction": {
        "spreadsheet_id": "1VS9kSgN9tCfnIIl7ZdkpVIgS9BX2zBOAXIj6MrYIUdk",
        "tab_name": "Univers Construction",
        "date_col": 0,       # A
        "provenance_col": 7,  # H
        "statut_col": 8,      # I
        "q_col": 15,          # P (fbclid)
        "r_col": 16,          # Q (gclid)
        "worksheet_name": "Univers Construction",
    },
    "tairmic": {
        "spreadsheet_id": "1GQAQnlpxVsdPBIq-xcEEEXtiLQtBg_Em_61n8WGUuJE",
        "tab_name": "Tairmic",
        "date_col": 0,       # A
        "provenance_col": 7,  # H
        "statut_col": 8,      # I
        "q_col": 16,          # Q (fbclid)
        "r_col": 17,          # R (gclid)
        "worksheet_name": "TAIRMIC",
    },
    "eco_systeme_durable": {
        "spreadsheet_id": "1FaWG8mjnfJGkIpY3Ksh4H8cVuqzOxSGg8CeCwE-9Dvw",
        "tab_name": "Eco Système Durable",
        "date_col": 0,        # A
        "provenance_col": 8,  # I
        "statut_col": 9,      # J
        "q_col": 17,          # R (fbclid)
        "r_col": 18,          # S (gclid)
        "worksheet_name": "Eco Système Durable",
    },
    "univers_gazon": {
        "spreadsheet_id": "1tZcLPeTAxl0vfshCigvH4WffSxv0MxanqSSOIAaqmPw",
        "tab_name": "Univers Gazons",
        "date_col": 0,        # A
        "provenance_col": 8,  # I
        "statut_col": 9,      # J
        "q_col": 17,          # R (fbclid)
        "r_col": 18,          # S (gclid)
        "worksheet_name": "Univers Gazon",
    },
}

# Mapping mois anglais → notre sheet
MONTH_NAMES_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _parse_date(value: str) -> Optional[datetime]:
    """Parse une date depuis le sheet leads. Supporte plusieurs formats."""
    if not value or not value.strip():
        return None
    value = value.strip()
    # Nettoyer le format ISO avec T et Z
    if "T" in value:
        value = value.split("T")[0]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y %H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d %B %Y %H:%M", "%d %B %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    # Essayer le format serial Google Sheets (nombre de jours depuis 1899-12-30)
    try:
        serial = float(value)
        if 1000 < serial < 100000:
            return datetime(1899, 12, 30) + relativedelta(days=int(serial))
    except (ValueError, TypeError):
        pass
    return None


def _get_target_months(reference_month: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retourne les 3 mois cibles (M-1, M-2, M-3 par rapport à maintenant,
    ou basé sur reference_month si fourni).

    Returns:
        Liste de dicts avec year, month, month_en (ex: "March 2026").
    """
    if reference_month:
        # Parse "February 2026" → datetime
        dt = datetime.strptime(reference_month, "%B %Y")
    else:
        dt = datetime.now() - relativedelta(months=1)

    months = []
    for i in range(3):
        target = dt - relativedelta(months=i)
        months.append({
            "year": target.year,
            "month": target.month,
            "month_en": f"{MONTH_NAMES_EN[target.month - 1]} {target.year}",
        })
    return months


def count_leads_for_month(
    rows: List[List[str]],
    year: int,
    month: int,
    config: Dict[str, int],
) -> Dict[str, int]:
    """
    Compte les leads Google, Meta et Générés pour un mois donné.

    Args:
        rows: Données brutes du sheet leads.
        year: Année cible.
        month: Mois cible (1-12).
        config: Config avec les indices de colonnes.

    Returns:
        {"leads_google": X, "leads_meta": Y, "leads_generes": Z, "leads_qualifies": W}
    """
    date_col = config["date_col"]
    provenance_col = config["provenance_col"]
    statut_col = config["statut_col"]
    q_col = config["q_col"]
    r_col = config["r_col"]

    leads_google = 0
    leads_meta = 0
    leads_total = 0
    leads_qualifies = 0

    for row in rows:
        # Vérifier que la ligne a assez de colonnes
        def get_cell(idx: int) -> str:
            return row[idx].strip() if idx < len(row) and row[idx] else ""

        # Filtrer par date
        date_str = get_cell(date_col)
        dt = _parse_date(date_str)
        if dt is None or dt.year != year or dt.month != month:
            continue

        statut = get_cell(statut_col).lower()

        # Exclure les doublons
        if statut == "doublon":
            continue

        provenance = get_cell(provenance_col).lower()
        q_val = get_cell(q_col)
        r_val = get_cell(r_col)
        is_media = "google" in provenance or "meta" in provenance or q_val or r_val

        # Ce lead est valide (non-doublon, bon mois)
        if is_media:
            leads_total += 1

        # Lead Google : H contient "google" OU R non vide
        if "google" in provenance or r_val:
            leads_google += 1

        # Lead Meta : H contient "meta" OU Q non vide
        if "meta" in provenance or q_val:
            leads_meta += 1

        # Lead qualifié : statut "qualifié" ou "converti", peu importe la source (média ou organique)
        if statut in ("qualifié", "converti"):
            leads_qualifies += 1

    return {
        "leads_google": leads_google,
        "leads_meta": leads_meta,
        "leads_generes": leads_total,
        "leads_qualifies": leads_qualifies,
    }


def _scrape_leads_client(
    sheets_service,
    client_key: str,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scrape les leads d'un client et écrit les résultats dans le sheet principal.

    Args:
        sheets_service: Instance GoogleSheetsService (pour écrire).
        client_key: Clé dans LEADS_SHEETS (ex: "kozeo", "riviera_grass").
        reference_month: Mois de référence (ex: "February 2026"). Si None, M-1.

    Returns:
        Dict avec le résumé des résultats.
    """
    config = LEADS_SHEETS[client_key]
    spreadsheet_id = config["spreadsheet_id"]
    tab_name = config["tab_name"]
    worksheet_name = config["worksheet_name"]
    # Déterminer la plage de lecture selon la colonne date
    max_col = "AA" if config["date_col"] >= 26 else chr(ord('A') + max(config["date_col"], config["r_col"]) + 1)

    logging.info(f"📊 Scraping leads '{client_key}' depuis '{tab_name}'...")

    # 1. Lire toutes les données du sheet leads
    data_range = f"'{tab_name}'!A2:{max_col}10000"
    result = sheets_service.service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=data_range,
    ).execute()
    rows = result.get("values", [])
    logging.info(f"  {len(rows)} lignes lues depuis le sheet leads")

    # 2. Calculer les 3 mois cibles
    target_months = _get_target_months(reference_month)
    logging.info(f"  Mois cibles : {[m['month_en'] for m in target_months]}")

    # 3. Compter les leads pour chaque mois
    results_by_month = {}
    for m in target_months:
        counts = count_leads_for_month(rows, m["year"], m["month"], config)
        results_by_month[m["month_en"]] = counts
        logging.info(
            f"  {m['month_en']}: Google={counts['leads_google']}, "
            f"Meta={counts['leads_meta']}, Générés={counts['leads_generes']}, "
            f"Qualifiés={counts['leads_qualifies']}"
        )

    # 4. Écrire dans le sheet principal
    headers_range = f"'{worksheet_name}'!2:2"
    headers_result = sheets_service.service.spreadsheets().values().get(
        spreadsheetId=sheets_service.sheet_id,
        range=headers_range,
    ).execute()
    headers_raw = headers_result.get("values", [[]])
    headers = [h.strip() if h else "" for h in headers_raw[0]] if headers_raw else []

    col_leads_google = None
    col_leads_meta = None
    col_leads_generes = None
    col_leads_qualifies = None
    for i, h in enumerate(headers):
        if h == "Leads Google":
            col_leads_google = i
        elif h == "Leads Meta":
            col_leads_meta = i
        elif h == "Leads Générés":
            col_leads_generes = i
        elif h == "Leads Qualifiés":
            col_leads_qualifies = i

    if col_leads_google is None or col_leads_meta is None or col_leads_generes is None or col_leads_qualifies is None:
        raise ValueError(
            f"Colonnes leads introuvables dans '{worksheet_name}'. "
            f"Headers trouvés: {headers}. "
            f"Attendus: 'Leads Google', 'Leads Meta', 'Leads Générés', 'Leads Qualifiés'"
        )

    month_range = f"'{worksheet_name}'!A3:A50"
    month_result = sheets_service.service.spreadsheets().values().get(
        spreadsheetId=sheets_service.sheet_id,
        range=month_range,
    ).execute()
    month_rows = month_result.get("values", [])

    def col_letter(idx: int) -> str:
        result_str = ""
        while idx >= 0:
            result_str = chr(idx % 26 + ord('A')) + result_str
            idx = idx // 26 - 1
        return result_str

    updates = []
    for row_idx, row_data in enumerate(month_rows):
        if not row_data or not row_data[0]:
            continue
        month_cell = row_data[0].strip()
        if month_cell in results_by_month:
            counts = results_by_month[month_cell]
            sheet_row = row_idx + 3

            updates.append({
                "range": f"{col_letter(col_leads_google)}{sheet_row}",
                "value": counts["leads_google"],
            })
            updates.append({
                "range": f"{col_letter(col_leads_meta)}{sheet_row}",
                "value": counts["leads_meta"],
            })
            updates.append({
                "range": f"{col_letter(col_leads_generes)}{sheet_row}",
                "value": counts["leads_generes"],
            })
            updates.append({
                "range": f"{col_letter(col_leads_qualifies)}{sheet_row}",
                "value": counts["leads_qualifies"],
            })

    if updates:
        sheets_service.update_sheet_data(worksheet_name, updates)
        logging.info(f"  ✅ {len(updates)} cellules mises à jour dans '{worksheet_name}'")
    else:
        logging.warning(f"  ⚠️ Aucune ligne trouvée pour les mois cibles dans '{worksheet_name}'")

    return {
        "client": worksheet_name,
        "months": results_by_month,
        "updates_count": len(updates),
    }


def scrape_leads_kozeo(
    sheets_service,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Scrape les leads Kozéo."""
    return _scrape_leads_client(sheets_service, "kozeo", reference_month)


def scrape_leads_riviera(
    sheets_service,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Scrape les leads Riviera Grass."""
    return _scrape_leads_client(sheets_service, "riviera_grass", reference_month)


def scrape_leads_sud_gazon(
    sheets_service,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Scrape les leads Sud Gazon."""
    return _scrape_leads_client(sheets_service, "sud_gazon", reference_month)


def scrape_leads_univers(
    sheets_service,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Scrape les leads Univers Construction."""
    return _scrape_leads_client(sheets_service, "univers_construction", reference_month)


def scrape_leads_tairmic(
    sheets_service,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Scrape les leads Tairmic."""
    return _scrape_leads_client(sheets_service, "tairmic", reference_month)


def scrape_leads_eco_systeme_durable(
    sheets_service,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Scrape les leads Eco Système Durable."""
    return _scrape_leads_client(sheets_service, "eco_systeme_durable", reference_month)


def scrape_leads_univers_gazon(
    sheets_service,
    reference_month: Optional[str] = None,
) -> Dict[str, Any]:
    """Scrape les leads Univers Gazon."""
    return _scrape_leads_client(sheets_service, "univers_gazon", reference_month)
