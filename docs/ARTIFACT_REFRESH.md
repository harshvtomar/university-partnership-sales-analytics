# Refresh and demonstrate

## Dashboard and data
Use Python 3.12, install requirements.txt, then `python -m streamlit run app.py`. The committed SQLite database is sufficient. Run `python -m src.generate` to rebuild the source CSVs, database, summary and hash manifest. Run `python -m src.export` for reporting inputs. The generator overwrites only this project's generated data files. Restart Streamlit after a source refresh to clear cached data.

## Excel
The workbook is a snapshot, not a live CRM connection. Native formulas calculate summary totals, territory metrics, lead-score sums and priority bands, recognized revenue and scenario-weighted forecasts. Yellow cells Revenue Forecast!K6:K8 are editable multipliers. Change K7 from 1.0 to 1.2 to change base bookings from INR 4,911,800 to INR 5,894,160. This does not change actual signed value.

Source-data refresh rebuilds the workbook and does not retain manual edits. The builder `scripts/build_workbook.mjs` requires the ChatGPT Work bundled `@oai/artifact-tool` authoring runtime, separate from the public Python dashboard. In Work, copy the builder to a temporary directory with a node_modules symlink to CODEX_PRIMARY_RUNTIME_NODE_MODULES, then run it with CODEX_PRIMARY_RUNTIME_NODE and the absolute repository directory as the argument. The committed XLSX can be opened and recalculated without that runtime. Do not imply that the authoring library is an ordinary public npm dependency.

Inputs and row bounds currently match the 600-opportunity release. A different-size dataset requires updating the explicit workbook ranges, then re-running reconciliation. Priority components are imported from Python and editable as component points; they are not a second implementation of the full feature-engineering pipeline. Sorting the lead table does not automatically rerank it after edits: sort Total score descending in Excel.

## Business artifacts
`scripts/build_reports.py` requires python-docx and refreshes the proposal and review from report_inputs.json, with narrative fixed for this release. Review narrative if the seed or business rules change. `scripts/build_deck.mjs` uses the same Work authoring environment as the workbook and its presentation validators. It is not needed to run the app. The editable DOCX/PPTX and PDFs are committed for direct use.

## Demonstration sequence
1. Open Executive Overview and explain bookings versus recognized revenue.
2. Filter Sales Pipeline to a territory; discuss historical stage reach and overdue actions.
3. Open Lead Intelligence, select O0426 and explain the eight score contributions.
4. Open Revenue Forecasting and change the multiplier; note the exclusion of stale dates.
5. Show Management Recommendations and the Excel scenario input. Use the proposal as an example pitch, not an actual client win.
