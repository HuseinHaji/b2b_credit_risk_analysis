from pathlib import Path
from subprocess import run, CalledProcessError


def run_command(cmd):
    print(f"Running: {cmd}")
    res = run(cmd, shell=True, check=True)
    return res


def run_all_views():
    from sqlalchemy import create_engine, text

    engine = create_engine("postgresql://huseyn@localhost:5432/b2b_credit_risk")
    view_files = sorted(Path('sql/views').glob('*.sql'))

    for vf in view_files:
        print(f"Creating view: {vf.name}")
        sql = vf.read_text(encoding='utf-8')
        try:
            with engine.begin() as conn:
                conn.execute(text(sql))
            print(f"✓ View created: {vf.name}")
        except Exception as e:
            print(f"⚠ Skipping view {vf.name} due to: {e}")
    engine.dispose()
    print('View creation step complete. Some views may have been skipped.')


if __name__ == '__main__':
    try:
        run_command('python scripts/run_phase2.py')
        run_command('python scripts/load_to_postgres_v2.py')
        run_all_views()
        print('\n✅ Full pipeline complete. Refresh DBeaver and inspect schema credit_risk_dw with tables and views.')
    except CalledProcessError as err:
        print(f'\n❌ Command failed: {err}')
        print('Check prior output and ensure DB server is running and data folders exist.')
