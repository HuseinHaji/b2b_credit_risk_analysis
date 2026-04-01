"""
Load Phase 2 data into PostgreSQL from CSV files.
This script creates the data warehouse schema and loads all tables.
"""

from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2 import sql, extras
import sys

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'database': 'b2b_credit_risk',
    'user': 'huseyn',
    'password': '',  # Empty password for local development
    'port': 5432
}

# Schema definition - maps table names to their column types
SCHEMA_DEFINITIONS = {
    'dim_date': {
        'date_key': 'INT PRIMARY KEY',
        'full_date': 'DATE',
        'year_num': 'INT',
        'quarter_num': 'INT',
        'month_num': 'INT',
        'month_name': 'VARCHAR(20)',
        'year_month': 'VARCHAR(10)',
        'week_of_year': 'INT',
        'day_of_month': 'INT',
        'day_name': 'VARCHAR(20)',
        'is_month_start': 'BOOLEAN',
        'is_month_end': 'BOOLEAN',
        'is_quarter_end': 'BOOLEAN',
        'is_year_end': 'BOOLEAN'
    },
    'dim_country': {
        'country_key': 'INT PRIMARY KEY',
        'country_name': 'VARCHAR(100)',
        'country_code': 'VARCHAR(3)',
        'region': 'VARCHAR(50)',
        'is_active': 'BOOLEAN',
        'load_timestamp': 'TIMESTAMP'
    },
    'dim_industry': {
        'industry_key': 'INT PRIMARY KEY',
        'industry_name': 'VARCHAR(100)',
        'industry_code': 'VARCHAR(10)',
        'is_active': 'BOOLEAN',
        'load_timestamp': 'TIMESTAMP'
    },
    'dim_risk_rating': {
        'rating_key': 'INT PRIMARY KEY',
        'rating_code': 'VARCHAR(5)',
        'rating_description': 'VARCHAR(100)',
        'min_score': 'FLOAT',
        'max_score': 'FLOAT',
        'is_active': 'BOOLEAN',
        'load_timestamp': 'TIMESTAMP'
    },
    'dim_customer': {
        'customer_key': 'INT PRIMARY KEY',
        'customer_id': 'VARCHAR(20)',
        'company_name': 'VARCHAR(200)',
        'country_key': 'INT',
        'industry_key': 'INT',
        'company_size': 'VARCHAR(20)',
        'establishment_year': 'INT',
        'revenue_eur_millions': 'FLOAT',
        'num_employees': 'INT',
        'credit_limit_eur': 'FLOAT',
        'first_transaction_date': 'DATE',
        'is_active': 'BOOLEAN',
        'load_timestamp': 'TIMESTAMP',
        'country_name': 'VARCHAR(100)',
        'industry_name': 'VARCHAR(100)'
    },
    'fact_exposure_snapshot': {
        'exposure_key': 'BIGINT PRIMARY KEY',
        'customer_key': 'INT',
        'snapshot_date_key': 'INT',
        'snapshot_month': 'VARCHAR(10)',
        'current_exposure': 'FLOAT',
        'overdue_exposure': 'FLOAT',
        'num_active_invoices': 'INT',
        'num_overdue_invoices': 'INT',
        'avg_dso': 'FLOAT',
        'utilization_ratio': 'FLOAT',
        'risk_rating_key': 'INT',
        'utilization_trend': 'FLOAT',
        'payment_velocity': 'FLOAT',
        'default_flag': 'INT',
        'is_month_start': 'BOOLEAN',
        'is_month_end': 'BOOLEAN',
        'load_timestamp': 'TIMESTAMP',
        'country_key': 'INT',
        'industry_key': 'INT',
        'company_size': 'VARCHAR(20)',
        'risk_rating_code': 'VARCHAR(5)'
    },
    'fact_invoice': {
        'invoice_key': 'BIGINT PRIMARY KEY',
        'invoice_id': 'VARCHAR(30)',
        'customer_key': 'INT',
        'invoice_date_key': 'INT',
        'due_date_key': 'INT',
        'invoice_amount_eur': 'FLOAT',
        'currency': 'VARCHAR(3)',
        'invoice_status': 'VARCHAR(20)',
        'payment_received_eur': 'FLOAT',
        'days_overdue': 'INT',
        'snapshot_month': 'VARCHAR(10)'
    },
    'fact_payment': {
        'payment_key': 'BIGINT PRIMARY KEY',
        'payment_id': 'VARCHAR(30)',
        'invoice_key': 'BIGINT',
        'payment_date_key': 'INT',
        'payment_amount_eur': 'FLOAT',
        'currency': 'VARCHAR(3)',
        'payment_method': 'VARCHAR(50)'
    },
    'fact_default_event': {
        'default_key': 'BIGINT PRIMARY KEY',
        'customer_key': 'INT',
        'default_date_key': 'INT',
        'default_month': 'VARCHAR(10)',
        'default_severity': 'VARCHAR(20)',
        'exposure_at_default_eur': 'FLOAT',
        'recovery_rate': 'FLOAT',
        'days_in_default': 'INT'
    },
    'fact_rating_history': {
        'rating_history_key': 'BIGINT PRIMARY KEY',
        'customer_key': 'INT',
        'rating_date_key': 'INT',
        'rating_month': 'VARCHAR(10)',
        'rating_key': 'INT',
        'rating_code': 'VARCHAR(5)',
        'risk_score': 'FLOAT',
        'load_timestamp': 'TIMESTAMP'
    }
}


def connect_to_postgres():
    """Establish connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)


def create_schema(conn):
    """Create credit_risk_dw schema."""
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS credit_risk_dw;")
        conn.commit()
        print("✓ Schema 'credit_risk_dw' created")
    except psycopg2.Error as e:
        print(f"Error creating schema: {e}")
        conn.rollback()
    finally:
        cursor.close()


def create_tables(conn):
    """Create all dimension and fact tables."""
    cursor = conn.cursor()
    
    for table_name, columns in SCHEMA_DEFINITIONS.items():
        col_defs = [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS credit_risk_dw.{table_name} (
                {', '.join(col_defs)}
            );
        """
        
        try:
            cursor.execute(create_table_sql)
            conn.commit()
            print(f"✓ Table '{table_name}' created")
        except psycopg2.Error as e:
            print(f"✗ Error creating table '{table_name}': {e}")
            conn.rollback()
    
    # Add foreign key constraints after all tables are created
    print("\n=== Adding Foreign Key Constraints ===")
    fk_constraints = [
        ("fact_invoice", "invoice_date_key", "dim_date", "date_key"),
        ("fact_invoice", "due_date_key", "dim_date", "date_key"),
        ("fact_invoice", "customer_key", "dim_customer", "customer_key"),
        ("fact_payment", "payment_date_key", "dim_date", "date_key"),
        ("fact_default_event", "default_date_key", "dim_date", "date_key"),
        ("fact_default_event", "customer_key", "dim_customer", "customer_key"),
        ("fact_rating_history", "rating_date_key", "dim_date", "date_key"),
        ("fact_rating_history", "customer_key", "dim_customer", "customer_key"),
        ("fact_exposure_snapshot", "snapshot_date_key", "dim_date", "date_key"),
        ("fact_exposure_snapshot", "customer_key", "dim_customer", "customer_key"),
        ("fact_exposure_snapshot", "risk_rating_key", "dim_risk_rating", "rating_key"),
    ]
    
    for fk_table, fk_col, ref_table, ref_col in fk_constraints:
        constraint_name = f"fk_{fk_table}_{fk_col}"
        try:
            cursor.execute(f"""
                ALTER TABLE credit_risk_dw.{fk_table}
                ADD CONSTRAINT {constraint_name} 
                FOREIGN KEY ({fk_col}) REFERENCES credit_risk_dw.{ref_table}({ref_col})
                ON DELETE CASCADE
            """)
            conn.commit()
            print(f"✓ Foreign key constraint added: {fk_table}.{fk_col} -> {ref_table}.{ref_col}")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                print(f"✓ Constraint {constraint_name} already exists")
            else:
                print(f"✗ Error adding FK constraint {constraint_name}: {e}")
            conn.rollback()
    
    cursor.close()


def load_csv_to_table(conn, table_name, csv_path):
    """Load CSV file into PostgreSQL table."""
    cursor = conn.cursor()
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Data type conversions for numpy types
        for col in df.columns:
            if 'key' in col.lower() or col in ['is_active', 'is_month_start', 'is_month_end', 'is_quarter_end', 'is_year_end']:
                # Convert integer types
                if df[col].dtype == 'int64':
                    df[col] = df[col].astype('int32')
                elif df[col].dtype == 'float64' and col.endswith('_key'):
                    df[col] = df[col].astype('int32').astype('float64')
        
        # Replace NaN with None for NULL insertion
        df = df.where(pd.notna(df), None)
        
        # Get column names from DataFrame
        columns = df.columns.tolist()
        
        # Prepare insert query
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"""
            INSERT INTO credit_risk_dw.{table_name} ({', '.join(columns)})
            VALUES ({placeholders})
        """
        
        # Insert data in batches
        data = [tuple(row) for row in df.values]
        extras.execute_batch(cursor, insert_query, data, page_size=1000)
        conn.commit()
        
        print(f"✓ Loaded {len(df)} rows into '{table_name}'")
        return True
        
    except FileNotFoundError:
        print(f"✗ File not found: {csv_path}")
        return False
    except psycopg2.Error as e:
        print(f"✗ Error loading data into '{table_name}': {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"✗ Unexpected error loading '{table_name}': {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def load_all_data(conn, data_dir):
    """Load all CSV files from Phase 2 output directory."""
    data_path = Path(data_dir)
    
    # Order matters - load dimensions first, then facts
    load_order = [
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
    
    print("\n=== Loading Data ===")
    for table_name in load_order:
        csv_file = data_path / f"{table_name}.csv"
        if csv_file.exists():
            load_csv_to_table(conn, table_name, csv_file)
        else:
            print(f"✗ CSV file not found: {csv_file}")


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "processed" / "phase2"
    
    print("=" * 60)
    print("PostgreSQL Data Warehouse Loader")
    print("=" * 60)
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Data Directory: {data_dir}")
    print()
    
    # Connect to database
    conn = connect_to_postgres()
    
    # Create schema
    create_schema(conn)
    
    # Create tables
    print("\n=== Creating Tables ===")
    create_tables(conn)
    
    # Load data
    load_all_data(conn, data_dir)
    
    # Close connection
    conn.close()
    
    print("\n" + "=" * 60)
    print("Data warehouse loading completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
