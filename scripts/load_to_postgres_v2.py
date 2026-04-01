"""
Load Phase 2 data into PostgreSQL from CSV files using pandas and SQL.
This script creates tables dynamically based on CSV structure.
"""

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, inspect, MetaData, text
from sqlalchemy.types import (
    Integer, BigInteger, Float, String, Date, Boolean, DateTime, Text
)
import sys

# Database connection string
DATABASE_URL = "postgresql://huseyn@localhost:5432/b2b_credit_risk"

# Load order - dimensions first, then facts
LOAD_ORDER = [
    'dim_date',
    'dim_country',
    'dim_industry',
    'dim_risk_rating',
    'dim_customer',
    'fact_exposure_snapshot',
    'fact_invoice',
    'fact_payment',
    'fact_default_event',
    'fact_rating_history',
]


def infer_column_type(df, col):
    """Infer SQLAlchemy column type from DataFrame column."""
    dtype = df[col].dtype
    
    # Check column name patterns for hints
    col_lower = col.lower()
    
    if col_lower == 'rating_bucket':
        return String(50)

    if 'key' in col_lower:
        if 'payment_key' in col_lower or 'invoice_key' in col_lower or col_lower == 'exposure_snapshot_key' or col_lower == 'default_event_key' or col_lower == 'rating_history_key':
            return BigInteger()
        else:
            return Integer()
    
    if col_lower in ['is_month_start', 'is_month_end', 'is_quarter_end', 'is_year_end', 'eur_currency_flag', 'cyclical_flag', 'insured_flag', 'partial_payment_flag', 'recovered_after_default_flag', 'downgrade_flag']:
        return Boolean()
    
    if col_lower in ['full_date', 'onboarding_date_key']:
        return Date()
    
    if 'date' in col_lower and 'key' in col_lower:
        return Integer()
    
    if dtype == 'object':
        return String(500)
    elif dtype == 'float64':
        return Float()
    elif dtype == 'int64':
        return BigInteger() if col_lower.endswith('_key') else Integer()
    elif dtype == 'bool':
        return Boolean()
    else:
        return String(500)


def create_engine_connection():
    """Create SQLAlchemy engine connection."""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✓ Connected to PostgreSQL: {DATABASE_URL}")
        return engine
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)


def drop_schema(engine):
    """Drop existing schema if it exists."""
    with engine.begin() as conn:
        try:
            conn.execute(text("DROP SCHEMA IF EXISTS credit_risk_dw CASCADE;"))
            print("✓ Dropped existing schema")
        except Exception as e:
            print(f"Note: {e}")


def load_all_data(engine, data_dir):
    """Load all CSV files from Phase 2 output directory."""
    data_path = Path(data_dir)
    
    print("\n=== Loading Data ===")
    
    for table_name in LOAD_ORDER:
        csv_file = data_path / f"{table_name}.csv"
        
        if not csv_file.exists():
            print(f"✗ CSV file not found: {csv_file}")
            continue
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Clean data - convert numpy types to Python types
            for col in df.columns:
                if df[col].dtype == 'float64':
                    # Try to convert to int where appropriate
                    if col.endswith('_key') or col.endswith('_flag'):
                        if df[col].notna().all() or df[col].isna().sum() == 0:
                            df[col] = df[col].astype('Int64')  # Nullable int
            
            # Replace NaN with None for proper NULL handling
            df = df.where(pd.notna(df), None)
            
            # Load to database - pandas handles schema creation
            df.to_sql(
                table_name,
                engine,
                schema='credit_risk_dw',
                if_exists='append',  # Will fail if table doesn't exist (first load)
                index=False,
                dtype={col: infer_column_type(df, col) for col in df.columns},
                method='multi',
                chunksize=5000
            )
            
            print(f"✓ Loaded {len(df):,} rows into '{table_name}'")
            
        except Exception as e:
            print(f"✗ Error loading '{table_name}': {e}")
            continue


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "processed" / "phase2"
    
    print("=" * 70)
    print("PostgreSQL Data Warehouse Loader (Automated Schema)")
    print("=" * 70)
    print(f"Database: {DATABASE_URL.split('/')[-1]}")
    print(f"Data Directory: {data_dir}")
    print()
    
    # Create engine
    engine = create_engine_connection()
    
    # Drop existing schema
    drop_schema(engine)
    
    # Create schema
    print("\n=== Creating Schema ===")
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS credit_risk_dw;"))
    print("✓ Schema 'credit_risk_dw' created")
    
    # Load data
    load_all_data(engine, data_dir)
    
    # Close engine
    engine.dispose()
    
    print("\n" + "=" * 70)
    print("Data warehouse loading completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Open DBeaver and connect to 'b2b_credit_risk' database")
    print("2. Verify tables are loaded under 'credit_risk_dw' schema")
    print("3. Run analytics queries from sql/analytics/")


if __name__ == "__main__":
    main()
