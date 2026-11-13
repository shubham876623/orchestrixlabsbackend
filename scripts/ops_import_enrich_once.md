# One-shot portfolio import / enrich (do NOT put back on Procfile boot)

These commands rewrite project fields. Run **manually** only when intentionally syncing from CSV:

```bash
python manage.py import_contracts --csv contracts.csv
python manage.py enrich_projects
```

Procfile no longer runs them on every deploy (prevents overwriting dashboard edits).
