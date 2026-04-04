import glob
from pathlib import Path
from sqlalchemy import create_engine, text


def run_sql_files(engine, files):
    for file_path in sorted(files):
        print(f"Executing {file_path}")
        sql = Path(file_path).read_text(encoding="utf-8")
        with engine.begin() as conn:
            conn.execute(text(sql))


if __name__ == "__main__":
    # configure for your database
    db_url = "postgresql://huseyn@localhost:5432/b2b_credit_risk"
    engine = create_engine(db_url)

    paths = {
        "ddl": "sql/ddl/*.sql",
        "staging": "sql/staging/*.sql",
        "load": "sql/load/*.sql",
        "views": "sql/views/*.sql",
        "quality_checks": "sql/quality_checks/*.sql",
    }

    # ensure both schemas exist (ddl creates credit_risk_dw, staging uses credit_risk)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS credit_risk;"))

    # run in order
    run_sql_files(engine, glob.glob(paths["ddl"]))
    run_sql_files(engine, glob.glob(paths["staging"]))
    run_sql_files(engine, glob.glob(paths["load"]))
    run_sql_files(engine, glob.glob(paths["views"]))

    print("Optional: run quality checks now if you want:")
    for qf in sorted(glob.glob(paths["quality_checks"])):
        print("  ", qf)

    print("Done. Refresh DBeaver connection and data catalog.")
