# B2B Credit Risk Analysis

This repository provides an end-to-end synthetic B2B credit risk pipeline.

## 1. Install dependencies

```bash
python -m pip install -e .
# or with extras
python -m pip install -e "[db,modeling]"
```

## 2. Phase 1: data generation

```bash
python scripts/run_data_generation.py
```

Output:
- `data/processed/phase1/dim_customer.csv`
- `data/processed/phase1/customer_month_panel.csv`
- `data/processed/phase1/fact_invoice.csv`
- `data/processed/phase1/fact_payment.csv`
- `data/processed/phase1/fact_default_event.csv`

## 3. Phase 2: warehouse build

```bash
python scripts/run_phase2.py
```

Output:
- `data/processed/phase2/dim_*` and `data/processed/phase2/fact_*`

## 4. Load into PostgreSQL (via DBeaver or script)

Use the built-in loader:

```bash
python scripts/load_to_postgres_v2.py
```

- Schema: `credit_risk_dw`
- Tables: `dim_date`, `dim_country`, `dim_industry`, `dim_risk_rating`, `dim_customer`, `fact_exposure_snapshot`, `fact_invoice`, `fact_payment`, `fact_default_event`, `fact_rating_history`

## 5. Feature engineering

```bash
python scripts/run_feature_pipeline.py
```

Output:
- `data/processed/features/customer_feature_dataset.csv`

## 6. Model training

```bash
python scripts/run_model_training.py
```

Output:
- `models/rf_default_model.pkl`

## 7. Test suite

```bash
pytest -q
```

## 8. Notes

- `data/`, `models/`, and `.coverage` are ignored.
- If `git push` fails with large objects, ensure generated artifacts are not tracked and history is cleaned.
