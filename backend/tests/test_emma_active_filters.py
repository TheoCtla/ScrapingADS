import types

from backend.google.services.reports import GoogleAdsReportsService
from backend.meta.services.reports import MetaAdsReportsService


def _fake_row(status_name: str = "ENABLED"):
    row = types.SimpleNamespace()
    row.campaign = types.SimpleNamespace()
    row.campaign.advertising_channel_type = types.SimpleNamespace(name="SEARCH")
    row.metrics = types.SimpleNamespace(clicks=1, impressions=1, ctr=0.1, average_cpc=1.0, cost_micros=1000000, conversions=0, phone_calls=0)
    row.campaign.status = types.SimpleNamespace(name=status_name)
    return row


def test_google_emma_only_enabled(monkeypatch):
    service = GoogleAdsReportsService()

    calls = {}

    def fake_fetch(customer_id, query):
        calls["query"] = query
        # Simuler un itérable de résultats API
        return iter([_fake_row("ENABLED"), _fake_row("PAUSED"), _fake_row("REMOVED")])

    monkeypatch.setattr(service.auth_service, "fetch_report_data", fake_fetch)

    data = service.get_campaign_data("6090621431", "2025-01-01", "2025-01-31", only_enabled=True)

    assert "campaign.status = 'ENABLED'" in calls["query"], "Le filtre ENABLED doit être présent dans la GAQL"
    # Nous ne validons pas le filtrage côté client, juste l'ajout de la clause GAQL
    assert len(list(data)) == 3


def test_meta_emma_only_active_insights(monkeypatch):
    service = MetaAdsReportsService()

    captured = {}

    def fake_request(url, params=None, max_retries=3):
        captured["params"] = params
        class Resp:
            status_code = 200
            def json(self):
                return {"data": [{"campaign_name": "C1", "impressions": 1, "clicks": 1, "spend": 1}]}
        return Resp()

    monkeypatch.setattr(service, "_make_meta_request_with_retry", fake_request)

    res = service.get_meta_insights("2569730083369971", "2025-01-01", "2025-01-31", only_active=True)
    assert res is not None
    assert captured["params"].get("effective_status") == ["ACTIVE"]


def test_meta_emma_only_active_contacts(monkeypatch):
    service = MetaAdsReportsService()

    captured = {}

    def fake_request(url, params=None, max_retries=3):
        captured["params"] = params
        class Resp:
            status_code = 200
            def json(self):
                return {"data": [{"campaign_id": "1", "campaign_name": "C1", "results": []}]}
        return Resp()

    monkeypatch.setattr(service, "_make_meta_request_with_retry", fake_request)

    res = service.getContactsResults("2569730083369971", "2025-01-01", "2025-01-31", only_active=True)
    assert isinstance(res, list)
    assert captured["params"].get("effective_status") == ["ACTIVE"]


def test_other_clients_unchanged_google(monkeypatch):
    service = GoogleAdsReportsService()

    def fake_fetch(customer_id, query):
        assert "campaign.status = 'ENABLED'" not in query
        return iter([_fake_row("PAUSED")])

    monkeypatch.setattr(service.auth_service, "fetch_report_data", fake_fetch)

    list(service.get_campaign_data("1111111111", "2025-01-01", "2025-01-31", only_enabled=False))


def test_other_clients_unchanged_meta(monkeypatch):
    service = MetaAdsReportsService()

    def fake_request(url, params=None, max_retries=3):
        assert not params.get("effective_status"), "Pas de filtre ACTIVE pour non-Emma"
        class Resp:
            status_code = 200
            def json(self):
                return {"data": []}
        return Resp()

    monkeypatch.setattr(service, "_make_meta_request_with_retry", fake_request)

    service.get_meta_insights("000000000000", "2025-01-01", "2025-01-31", only_active=False)
    service.getContactsResults("000000000000", "2025-01-01", "2025-01-31", only_active=False)


