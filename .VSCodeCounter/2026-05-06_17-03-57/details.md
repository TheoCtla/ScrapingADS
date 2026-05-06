# Details

Date : 2026-05-06 17:03:57

Directory /Users/theocatala/Documents/Tarmaac/Projets/scrappingRapport

Total : 115 files,  21765 codes, 1696 comments, 4213 blanks, all 27674 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [Dockerfile](/Dockerfile) | Docker | 7 | 6 | 6 | 19 |
| [README.md](/README.md) | Markdown | 82 | 0 | 27 | 109 |
| [backend/__init__.py](/backend/__init__.py) | Python | 5 | 0 | 1 | 6 |
| [backend/common/__init__.py](/backend/common/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/common/auth_utils.py](/backend/common/auth_utils.py) | Python | 71 | 8 | 18 | 97 |
| [backend/common/services/__init__.py](/backend/common/services/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/common/services/client_resolver.py](/backend/common/services/client_resolver.py) | Python | 119 | 2 | 34 | 155 |
| [backend/common/services/google_drive.py](/backend/common/services/google_drive.py) | Python | 212 | 13 | 56 | 281 |
| [backend/common/services/google_sheets.py](/backend/common/services/google_sheets.py) | Python | 158 | 4 | 39 | 201 |
| [backend/common/services/leads_scraper.py](/backend/common/services/leads_scraper.py) | Python | 330 | 17 | 56 | 403 |
| [backend/common/services/light_scraper.py](/backend/common/services/light_scraper.py) | Python | 151 | 0 | 31 | 182 |
| [backend/common/utils/__init__.py](/backend/common/utils/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/common/utils/concurrency_manager.py](/backend/common/utils/concurrency_manager.py) | Python | 105 | 10 | 20 | 135 |
| [backend/common/utils/memory_manager.py](/backend/common/utils/memory_manager.py) | Python | 0 | 0 | 1 | 1 |
| [backend/config/__init__.py](/backend/config/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/config/client_allowlist.json](/backend/config/client_allowlist.json) | JSON | 560 | 0 | 0 | 560 |
| [backend/config/client_mappings.json](/backend/config/client_mappings.json) | JSON | 155 | 0 | 0 | 155 |
| [backend/config/meta_mappings.json](/backend/config/meta_mappings.json) | JSON | 118 | 0 | 0 | 118 |
| [backend/config/settings.py](/backend/config/settings.py) | Python | 74 | 14 | 24 | 112 |
| [backend/google_ads_wrapper/__init__.py](/backend/google_ads_wrapper/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/google_ads_wrapper/services/__init__.py](/backend/google_ads_wrapper/services/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/google_ads_wrapper/services/authentication.py](/backend/google_ads_wrapper/services/authentication.py) | Python | 79 | 0 | 16 | 95 |
| [backend/google_ads_wrapper/services/conversions.py](/backend/google_ads_wrapper/services/conversions.py) | Python | 3,791 | 378 | 834 | 5,003 |
| [backend/google_ads_wrapper/services/google_ads_creative.py](/backend/google_ads_wrapper/services/google_ads_creative.py) | Python | 305 | 18 | 67 | 390 |
| [backend/google_ads_wrapper/services/reports.py](/backend/google_ads_wrapper/services/reports.py) | Python | 257 | 31 | 64 | 352 |
| [backend/google_ads_wrapper/utils/__init__.py](/backend/google_ads_wrapper/utils/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/google_ads_wrapper/utils/mappings.py](/backend/google_ads_wrapper/utils/mappings.py) | Python | 134 | 11 | 41 | 186 |
| [backend/google_analytics/__init__.py](/backend/google_analytics/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [backend/google_analytics/services/__init__.py](/backend/google_analytics/services/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [backend/google_analytics/services/authentication.py](/backend/google_analytics/services/authentication.py) | Python | 24 | 0 | 9 | 33 |
| [backend/google_analytics/services/reports.py](/backend/google_analytics/services/reports.py) | Python | 65 | 0 | 14 | 79 |
| [backend/google_analytics/utils/__init__.py](/backend/google_analytics/utils/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [backend/main.py](/backend/main.py) | Python | 1,188 | 180 | 283 | 1,651 |
| [backend/meta/__init__.py](/backend/meta/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/meta/services/__init__.py](/backend/meta/services/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/meta/services/authentication.py](/backend/meta/services/authentication.py) | Python | 229 | 12 | 53 | 294 |
| [backend/meta/services/meta_ads_creative.py](/backend/meta/services/meta_ads_creative.py) | Python | 259 | 26 | 70 | 355 |
| [backend/meta/services/reports.py](/backend/meta/services/reports.py) | Python | 795 | 82 | 167 | 1,044 |
| [backend/meta/utils/__init__.py](/backend/meta/utils/__init__.py) | Python | 3 | 0 | 0 | 3 |
| [backend/meta/utils/mappings.py](/backend/meta/utils/mappings.py) | Python | 112 | 3 | 28 | 143 |
| [backend/reports/__init__.py](/backend/reports/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [backend/reports/charts.py](/backend/reports/charts.py) | Python | 487 | 38 | 102 | 627 |
| [backend/reports/data_reader.py](/backend/reports/data_reader.py) | Python | 351 | 17 | 73 | 441 |
| [backend/reports/drive_report_service.py](/backend/reports/drive_report_service.py) | Python | 105 | 0 | 22 | 127 |
| [backend/reports/generator.py](/backend/reports/generator.py) | Python | 158 | 8 | 38 | 204 |
| [backend/reports/styles.py](/backend/reports/styles.py) | Python | 201 | 28 | 41 | 270 |
| [backend/reports/template_router.py](/backend/reports/template_router.py) | Python | 147 | 6 | 33 | 186 |
| [backend/reports/templates/__init__.py](/backend/reports/templates/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [backend/reports/templates/base.py](/backend/reports/templates/base.py) | Python | 301 | 37 | 54 | 392 |
| [backend/reports/templates/template_bedroom.py](/backend/reports/templates/template_bedroom.py) | Python | 124 | 13 | 32 | 169 |
| [backend/reports/templates/template_cuisinistes.py](/backend/reports/templates/template_cuisinistes.py) | Python | 783 | 52 | 143 | 978 |
| [backend/reports/templates/template_denteva.py](/backend/reports/templates/template_denteva.py) | Python | 345 | 30 | 83 | 458 |
| [backend/reports/templates/template_emma.py](/backend/reports/templates/template_emma.py) | Python | 414 | 36 | 95 | 545 |
| [backend/reports/templates/template_evopro.py](/backend/reports/templates/template_evopro.py) | Python | 530 | 50 | 120 | 700 |
| [backend/reports/templates/template_laserel.py](/backend/reports/templates/template_laserel.py) | Python | 397 | 37 | 92 | 526 |
| [backend/reports/templates/template_leadgen.py](/backend/reports/templates/template_leadgen.py) | Python | 452 | 36 | 97 | 585 |
| [backend/reports/templates/template_litiers.py](/backend/reports/templates/template_litiers.py) | Python | 654 | 81 | 131 | 866 |
| [backend/reports/templates/template_lyleoo.py](/backend/reports/templates/template_lyleoo.py) | Python | 384 | 33 | 91 | 508 |
| [backend/reports/templates/template_sachs.py](/backend/reports/templates/template_sachs.py) | Python | 554 | 45 | 126 | 725 |
| [backend/requirements.txt](/backend/requirements.txt) | pip requirements | 27 | 60 | 33 | 120 |
| [backend/run.py](/backend/run.py) | Python | 20 | 4 | 5 | 29 |
| [backend/test_france_literie_narbonne.py](/backend/test_france_literie_narbonne.py) | Python | 0 | 0 | 1 | 1 |
| [backend/test_france_literie_perpignan.py](/backend/test_france_literie_perpignan.py) | Python | 0 | 0 | 1 | 1 |
| [backend/tests/test_client_resolver.py](/backend/tests/test_client_resolver.py) | Python | 169 | 18 | 45 | 232 |
| [backend/tests/test_emma_active_filters.py](/backend/tests/test_emma_active_filters.py) | Python | 67 | 2 | 35 | 104 |
| [backend/tests/test_performance.py](/backend/tests/test_performance.py) | Python | 206 | 25 | 56 | 287 |
| [frontend/eslint.config.js](/frontend/eslint.config.js) | JavaScript | 22 | 0 | 2 | 24 |
| [frontend/index.html](/frontend/index.html) | HTML | 20 | 1 | 3 | 24 |
| [frontend/package-lock.json](/frontend/package-lock.json) | JSON | 1,480 | 0 | 1 | 1,481 |
| [frontend/package.json](/frontend/package.json) | JSON | 23 | 0 | 1 | 24 |
| [frontend/public/site.webmanifest](/frontend/public/site.webmanifest) | JSON | 24 | 0 | 1 | 25 |
| [frontend/public/vite.svg](/frontend/public/vite.svg) | XML | 1 | 0 | 0 | 1 |
| [frontend/src/App.css](/frontend/src/App.css) | CSS | 66 | 3 | 10 | 79 |
| [frontend/src/App.tsx](/frontend/src/App.tsx) | TypeScript JSX | 19 | 0 | 3 | 22 |
| [frontend/src/assets/react.svg](/frontend/src/assets/react.svg) | XML | 1 | 0 | 0 | 1 |
| [frontend/src/components/ExportDrive/ExportDrive.css](/frontend/src/components/ExportDrive/ExportDrive.css) | CSS | 423 | 6 | 67 | 496 |
| [frontend/src/components/ExportDrive/ExportDrive.tsx](/frontend/src/components/ExportDrive/ExportDrive.tsx) | TypeScript JSX | 131 | 46 | 23 | 200 |
| [frontend/src/components/HomePage/HomePage.css](/frontend/src/components/HomePage/HomePage.css) | CSS | 123 | 1 | 24 | 148 |
| [frontend/src/components/HomePage/HomePage.tsx](/frontend/src/components/HomePage/HomePage.tsx) | TypeScript JSX | 31 | 0 | 6 | 37 |
| [frontend/src/components/ScrapingRapports/ScrapingRapports.tsx](/frontend/src/components/ScrapingRapports/ScrapingRapports.tsx) | TypeScript JSX | 570 | 86 | 118 | 774 |
| [frontend/src/components/SuccessModal/SuccessModal.css](/frontend/src/components/SuccessModal/SuccessModal.css) | CSS | 191 | 7 | 30 | 228 |
| [frontend/src/components/SuccessModal/SuccessModal.tsx](/frontend/src/components/SuccessModal/SuccessModal.tsx) | TypeScript JSX | 90 | 0 | 9 | 99 |
| [frontend/src/components/google/GoogleCustomersSelect/GoogleCustomersSelect.css](/frontend/src/components/google/GoogleCustomersSelect/GoogleCustomersSelect.css) | CSS | 152 | 2 | 26 | 180 |
| [frontend/src/components/google/GoogleCustomersSelect/GoogleCustomersSelect.tsx](/frontend/src/components/google/GoogleCustomersSelect/GoogleCustomersSelect.tsx) | TypeScript JSX | 104 | 9 | 16 | 129 |
| [frontend/src/components/google/GoogleDownloadButton/DownloadButton.css](/frontend/src/components/google/GoogleDownloadButton/DownloadButton.css) | CSS | 0 | 1 | 0 | 1 |
| [frontend/src/components/google/GoogleDownloadButton/DownloadButton.tsx](/frontend/src/components/google/GoogleDownloadButton/DownloadButton.tsx) | TypeScript JSX | 21 | 0 | 2 | 23 |
| [frontend/src/components/google/GoogleMetricsSelector/MetricsSelector.css](/frontend/src/components/google/GoogleMetricsSelector/MetricsSelector.css) | CSS | 125 | 2 | 25 | 152 |
| [frontend/src/components/google/GoogleMetricsSelector/MetricsSelector.tsx](/frontend/src/components/google/GoogleMetricsSelector/MetricsSelector.tsx) | TypeScript JSX | 81 | 0 | 11 | 92 |
| [frontend/src/components/meta/MetaAccountsSelect/MetaAccountsSelect.css](/frontend/src/components/meta/MetaAccountsSelect/MetaAccountsSelect.css) | CSS | 150 | 2 | 25 | 177 |
| [frontend/src/components/meta/MetaAccountsSelect/MetaAccountsSelect.tsx](/frontend/src/components/meta/MetaAccountsSelect/MetaAccountsSelect.tsx) | TypeScript JSX | 102 | 8 | 16 | 126 |
| [frontend/src/components/meta/MetaMetricsSelector/MetaMetricsSelector.css](/frontend/src/components/meta/MetaMetricsSelector/MetaMetricsSelector.css) | CSS | 82 | 2 | 12 | 96 |
| [frontend/src/components/meta/MetaMetricsSelector/MetaMetricsSelector.tsx](/frontend/src/components/meta/MetaMetricsSelector/MetaMetricsSelector.tsx) | TypeScript JSX | 70 | 2 | 10 | 82 |
| [frontend/src/components/unified/BulkScrapingProgress/BulkScrapingProgress.css](/frontend/src/components/unified/BulkScrapingProgress/BulkScrapingProgress.css) | CSS | 161 | 0 | 31 | 192 |
| [frontend/src/components/unified/BulkScrapingProgress/BulkScrapingProgress.tsx](/frontend/src/components/unified/BulkScrapingProgress/BulkScrapingProgress.tsx) | TypeScript JSX | 92 | 0 | 11 | 103 |
| [frontend/src/components/unified/BulkScrapingProgress/__tests__/BulkScrapingProgress.test.tsx](/frontend/src/components/unified/BulkScrapingProgress/__tests__/BulkScrapingProgress.test.tsx) | TypeScript JSX | 55 | 0 | 11 | 66 |
| [frontend/src/components/unified/ClientSelector/ClientSelector.css](/frontend/src/components/unified/ClientSelector/ClientSelector.css) | CSS | 135 | 2 | 26 | 163 |
| [frontend/src/components/unified/ClientSelector/ClientSelector.tsx](/frontend/src/components/unified/ClientSelector/ClientSelector.tsx) | TypeScript JSX | 174 | 13 | 26 | 213 |
| [frontend/src/components/unified/DateRangePicker/DateRangePicker.css](/frontend/src/components/unified/DateRangePicker/DateRangePicker.css) | CSS | 50 | 1 | 6 | 57 |
| [frontend/src/components/unified/DateRangePicker/DateRangePicker.tsx](/frontend/src/components/unified/DateRangePicker/DateRangePicker.tsx) | TypeScript JSX | 93 | 5 | 12 | 110 |
| [frontend/src/components/unified/ReportHeader/ReportHeader.css](/frontend/src/components/unified/ReportHeader/ReportHeader.css) | CSS | 10 | 1 | 1 | 12 |
| [frontend/src/components/unified/ReportHeader/ReportHeader.tsx](/frontend/src/components/unified/ReportHeader/ReportHeader.tsx) | TypeScript JSX | 12 | 0 | 2 | 14 |
| [frontend/src/components/unified/UnifiedDownloadButton/UnifiedDownloadButton.css](/frontend/src/components/unified/UnifiedDownloadButton/UnifiedDownloadButton.css) | CSS | 127 | 1 | 18 | 146 |
| [frontend/src/components/unified/UnifiedDownloadButton/UnifiedDownloadButton.tsx](/frontend/src/components/unified/UnifiedDownloadButton/UnifiedDownloadButton.tsx) | TypeScript JSX | 72 | 0 | 9 | 81 |
| [frontend/src/config/quotas.ts](/frontend/src/config/quotas.ts) | TypeScript | 40 | 9 | 9 | 58 |
| [frontend/src/index.css](/frontend/src/index.css) | CSS | 62 | 0 | 8 | 70 |
| [frontend/src/main.tsx](/frontend/src/main.tsx) | TypeScript JSX | 14 | 0 | 3 | 17 |
| [frontend/src/vite-env.d.ts](/frontend/src/vite-env.d.ts) | TypeScript | 0 | 1 | 1 | 2 |
| [frontend/tsconfig.app.json](/frontend/tsconfig.app.json) | JSON | 23 | 2 | 3 | 28 |
| [frontend/tsconfig.json](/frontend/tsconfig.json) | JSON with Comments | 7 | 0 | 1 | 8 |
| [frontend/tsconfig.node.json](/frontend/tsconfig.node.json) | JSON | 21 | 2 | 3 | 26 |
| [frontend/vite.config.ts](/frontend/vite.config.ts) | TypeScript | 5 | 1 | 2 | 8 |
| [gunicorn.conf.py](/gunicorn.conf.py) | Python | 41 | 9 | 14 | 64 |
| [render.yaml](/render.yaml) | YAML | 33 | 0 | 0 | 33 |
| [start_project.sh](/start_project.sh) | Shell Script | 119 | 0 | 62 | 181 |
| [vercel.json](/vercel.json) | JSON | 21 | 0 | 0 | 21 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)