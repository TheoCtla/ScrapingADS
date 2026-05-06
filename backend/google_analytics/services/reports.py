"""
Service de récupération des métriques Google Analytics 4.
"""

import logging
from typing import Dict, List

from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    Metric,
    RunReportRequest,
)

from backend.google_analytics.services.authentication import GoogleAnalyticsAuthService


class GoogleAnalyticsReportsService:
    """Récupère les vues de pages GA4 pour une liste de paths donnée."""

    def __init__(self):
        self._auth = GoogleAnalyticsAuthService()
        self._client = self._auth.get_client()

    def get_page_views(
        self,
        property_id: str,
        paths: List[str],
        start_date: str,
        end_date: str,
    ) -> Dict[str, int]:
        """
        Retourne le nombre de vues GA4 pour chaque path demandé.

        Args:
            property_id: ID numérique de la propriété GA4 (ex: "407081207")
            paths: Liste des chemins d'URL à filtrer (ex: ["/", "/canapes"])
            start_date: Date de début au format YYYY-MM-DD
            end_date: Date de fin au format YYYY-MM-DD

        Returns:
            Dict {path: nombre_de_vues}. Les paths absents du résultat sont à 0.
        """
        if not property_id or not paths:
            return {p: 0 for p in paths}

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="pagePath",
                    in_list_filter=Filter.InListFilter(values=paths),
                )
            ),
        )

        try:
            response = self._client.run_report(request)
        except Exception as e:
            logging.error(f"❌ Erreur appel GA4 (property={property_id}): {e}")
            raise

        results: Dict[str, int] = {p: 0 for p in paths}
        for row in response.rows:
            path = row.dimension_values[0].value
            views = int(row.metric_values[0].value or 0)
            results[path] = views

        logging.info(
            f"📊 GA4 property={property_id} période={start_date}→{end_date} "
            f"paths={len(paths)} → résultats={results}"
        )
        return results
