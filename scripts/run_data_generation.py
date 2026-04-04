"""
Data Generation Script for B2B Credit Risk Analysis

This script orchestrates the generation of synthetic B2B credit data,
including customers, invoices, payments, and default events.
It's designed to create realistic datasets for credit risk modeling.
"""

from pathlib import Path
import os

from b2b_credit_risk_analysis.data_generation.customers import generate_customer_dimension
from b2b_credit_risk_analysis.data_generation.customer_month import generate_customer_month_panel
from b2b_credit_risk_analysis.data_generation.invoices import generate_invoices, attach_due_month_context
from b2b_credit_risk_analysis.data_generation.payments import generate_payments
from b2b_credit_risk_analysis.data_generation.defaults import generate_default_events, apply_default_targets
from b2b_credit_risk_analysis.data_generation.finalize import finalize_invoice_status


def prepare_public_exports(
    dim_customer,
    customer_month_panel,
    fact_invoice,
    fact_payment,
    fact_default_event,
):
    """
    Prepare dataframes for export by removing internal columns that shouldn't be exposed.

    This function cleans up the generated data by dropping columns that are used
    internally during generation but aren't needed for analysis or modeling.
    """
    # Customer dimension - keep as is, it's already clean
    dim_customer_export = dim_customer.copy()

    # Monthly panel - remove latent state variables used for simulation
    customer_month_panel_export = customer_month_panel.copy()
    if "latent_state" in customer_month_panel_export.columns:
        customer_month_panel_export = customer_month_panel_export.drop(columns=["latent_state"])

    # Invoice facts - remove snapshot month as it's redundant with due_date
    fact_invoice_export = fact_invoice.copy()
    if "snapshot_month" in fact_invoice_export.columns:
        fact_invoice_export = fact_invoice_export.drop(columns=["snapshot_month"])

    # Payment facts - keep all columns, they're all relevant
    fact_payment_export = fact_payment.copy()

    # Default events - keep as is
    fact_default_event_export = fact_default_event.copy()

    return {
        "dim_customer": dim_customer_export,
        "customer_month_panel": customer_month_panel_export,
        "fact_invoice": fact_invoice_export,
        "fact_payment": fact_payment_export,
        "fact_default_event": fact_default_event_export,
    }


def save_outputs(outputs: dict, output_dir: str = None):
    """
    Save the generated dataframes to CSV files in the specified directory.

    Args:
        outputs: Dictionary of dataframe names to dataframes
        output_dir: Directory to save files (defaults to data/processed/phase1)
    """
    if output_dir is None:
        # Default to the standard location relative to this script
        project_root = Path(__file__).parent.parent
        output_dir = project_root / "data" / "processed" / "phase1"
    else:
        output_dir = Path(output_dir)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for name, df in outputs.items():
        file_path = output_path / f"{name}.csv"
        df.to_csv(file_path, index=False)
        print(f"Saved {name}: {df.shape} -> {file_path}")


def run_phase1_generation():
    """
    Main function to generate all phase 1 data.

    This orchestrates the entire data generation pipeline:
    1. Generate customer base
    2. Create monthly customer states
    3. Generate invoices based on customer behavior
    4. Simulate payments
    5. Create default events
    6. Finalize invoice statuses

    Returns:
        Dictionary of cleaned dataframes ready for export
    """
    # Start with the customer foundation
    dim_customer = generate_customer_dimension(n_customers=10_000, seed=42)

    # Generate monthly snapshots of customer financial state
    customer_month_panel = generate_customer_month_panel(
        dim_customer=dim_customer,
        start="2022-01-31",
        end="2025-12-31",
        seed=42,
    )

    # Create invoices based on customer credit behavior
    fact_invoice = generate_invoices(customer_month_panel, seed=42)
    invoices_with_context = attach_due_month_context(fact_invoice, customer_month_panel)

    # Simulate payment behavior
    fact_payment = generate_payments(invoices_with_context, seed=42)

    # Generate default events based on customer risk profiles
    fact_default_event = generate_default_events(customer_month_panel, seed=42)
    customer_month_panel = apply_default_targets(customer_month_panel, fact_default_event)

    # Update invoice statuses based on payments and defaults
    fact_invoice = finalize_invoice_status(fact_invoice, fact_payment, fact_default_event)

    # Prepare clean exports
    public_exports = prepare_public_exports(
        dim_customer=dim_customer,
        customer_month_panel=customer_month_panel,
        fact_invoice=fact_invoice,
        fact_payment=fact_payment,
        fact_default_event=fact_default_event,
    )

    return public_exports


if __name__ == "__main__":
    # Run the full data generation pipeline
    outputs = run_phase1_generation()
    save_outputs(outputs)