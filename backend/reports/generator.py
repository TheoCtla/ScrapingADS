"""
Générateur de rapports PPTX.
Orchestre le flux complet : lecture Sheet → routage template → génération → upload Drive.
"""

import io
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any, Optional

from backend.reports.template_router import (
    resolve_template,
    get_route_name,
    is_template_implemented,
)


def _compute_target_month() -> str:
    """Calcule le mois M-1 en anglais. Ex: si on est en mars 2026 → 'February 2026'."""
    now = datetime.now()
    target = now - relativedelta(months=1)
    return target.strftime("%B %Y")


def _compute_drive_folder_name() -> str:
    """Nom du dossier Drive au format YYYY-MM pour M-1. Ex: '2026-02'."""
    now = datetime.now()
    target = now - relativedelta(months=1)
    return target.strftime("%Y-%m")


def _sanitize_filename(name: str) -> str:
    """Nettoie un nom pour l'utiliser dans un nom de fichier."""
    return name.replace("/", "-").replace("\\", "-").replace(":", "-").strip()


def _build_report_filename(sheet_name: str, month_fr: str) -> str:
    """
    Construit le nom du fichier PPTX.
    Ex: 'Rapport FL Bordeaux Février 2026.pptx'
    """
    clean_name = _sanitize_filename(sheet_name)
    clean_month = _sanitize_filename(month_fr)
    return f"Rapport {clean_name} {clean_month}.pptx"


def _generate_single_report(
    sheet_name: str,
    month: str,
    sheets_service,
    drive_service,
    drive_folder_id: str,
) -> Dict[str, Any]:
    """
    Génère un rapport PPTX pour un seul onglet et l'uploade sur Drive.

    Returns:
        Dict avec le résultat : client, status, drive_link, error.
    """
    route_name = get_route_name(sheet_name)

    if not is_template_implemented(sheet_name):
        return {
            "client": sheet_name,
            "route": route_name,
            "status": "skipped",
            "reason": f"Template '{route_name}' pas encore implémenté",
        }

    from backend.reports.data_reader import read_report_data_by_worksheet

    # 1. Lire les données du Sheet
    data = read_report_data_by_worksheet(
        worksheet_name=sheet_name,
        month=month,
        sheets_service=sheets_service,
    )

    # 2. Instancier le bon template et générer le PPTX
    template_class = resolve_template(sheet_name)
    template = template_class()
    presentation = template.generate(data)

    # 3. Sérialiser en bytes
    buffer = io.BytesIO()
    presentation.save(buffer)
    pptx_bytes = buffer.getvalue()

    # 4. Upload sur Drive
    filename = _build_report_filename(sheet_name, data.get("month_fr", month))
    file_id = drive_service.upload_pptx(pptx_bytes, filename, drive_folder_id)
    drive_link = drive_service.get_file_link(file_id)

    return {
        "client": sheet_name,
        "route": route_name,
        "status": "success",
        "filename": filename,
        "drive_link": drive_link,
        "file_id": file_id,
    }


def generate_all_reports(
    month: Optional[str] = None,
    filter_name: Optional[str] = None,
    filter_template: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Génère les rapports PPTX pour tous les onglets visibles du Sheet
    et les uploade sur Google Drive.

    Args:
        month: Mois cible en anglais (ex: 'February 2026').
               Si None, calcule automatiquement M-1.
        filter_name: Filtre optionnel sur le nom de l'onglet (case-insensitive).
        filter_template: Filtre optionnel sur le nom de la route/template (ex: 'autres').
    """
    target_month = month or _compute_target_month()
    folder_name = _compute_drive_folder_name() if month is None else None

    if folder_name is None:
        from backend.reports.data_reader import _parse_month
        dt = _parse_month(target_month)
        folder_name = dt.strftime("%Y-%m") if dt else "rapports"

    logging.info(f"Génération des rapports pour '{target_month}' → dossier '{folder_name}'")

    # Initialiser les services une seule fois
    from backend.common.services.google_sheets import GoogleSheetsService
    from backend.reports.drive_report_service import DriveReportService

    sheets_service = GoogleSheetsService()
    drive_service = DriveReportService()

    # Créer le dossier mensuel sur Drive
    drive_folder_id = drive_service.find_or_create_month_folder(folder_name)

    # Lister les onglets visibles
    visible_sheets = sheets_service.get_visible_worksheet_names()
    if filter_name:
        filter_lower = filter_name.lower()
        visible_sheets = [s for s in visible_sheets if filter_lower in s.lower()]
        logging.info(f"{len(visible_sheets)} onglets après filtre nom '{filter_name}'")
    if filter_template:
        filter_tpl_lower = filter_template.lower()
        visible_sheets = [s for s in visible_sheets if get_route_name(s) == filter_tpl_lower]
        logging.info(f"{len(visible_sheets)} onglets après filtre template '{filter_template}'")
    if not filter_name and not filter_template:
        logging.info(f"{len(visible_sheets)} onglets visibles trouvés")

    results: List[Dict[str, Any]] = []

    for sheet_name in visible_sheets:
        try:
            result = _generate_single_report(
                sheet_name=sheet_name,
                month=target_month,
                sheets_service=sheets_service,
                drive_service=drive_service,
                drive_folder_id=drive_folder_id,
            )
            results.append(result)

            if result["status"] == "success":
                logging.info(f"[OK] {sheet_name} → {result['filename']}")
            else:
                logging.info(f"[SKIP] {sheet_name} → {result.get('reason', '')}")

        except Exception as e:
            logging.error(f"[ERREUR] {sheet_name}: {e}", exc_info=True)
            results.append({
                "client": sheet_name,
                "route": get_route_name(sheet_name),
                "status": "error",
                "error": str(e),
            })

    # Résumé
    success_count = sum(1 for r in results if r["status"] == "success")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")
    error_count = sum(1 for r in results if r["status"] == "error")

    summary = {
        "month": target_month,
        "drive_folder": folder_name,
        "drive_folder_id": drive_folder_id,
        "total": len(results),
        "success": success_count,
        "skipped": skipped_count,
        "errors": error_count,
    }

    logging.info(
        f"Génération terminée : {success_count} OK, "
        f"{skipped_count} skippés, {error_count} erreurs"
    )

    return {
        "summary": summary,
        "reports": results,
    }
