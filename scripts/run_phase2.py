from pathlib import Path
from b2b_credit_risk_analysis.warehouse.run_phase2 import run_phase2


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    input_dir = project_root / "data" / "processed" / "phase1"
    output_dir = project_root / "data" / "processed" / "phase2"
    
    run_phase2(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        save_parquet=False,
    )