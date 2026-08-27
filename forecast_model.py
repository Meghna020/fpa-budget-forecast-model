from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent


def build_scenario(df: pd.DataFrame, name: str, volume_factor: float, price_factor: float, cogs_factor: float) -> pd.DataFrame:
    out = df.copy()
    out["scenario"] = name
    out["forecast_units"] = (out["budget_units"] * volume_factor).round()
    out["forecast_price"] = out["budget_price"] * price_factor
    out["forecast_revenue"] = out["forecast_units"] * out["forecast_price"]
    out["forecast_cogs"] = out["forecast_revenue"] * out["budget_cogs_pct"] * cogs_factor
    out["forecast_gross_profit"] = out["forecast_revenue"] - out["forecast_cogs"]
    out["forecast_opex"] = out["budget_opex"] * (1.02 if name == "Base" else 1.00)
    out["forecast_ebitda"] = out["forecast_gross_profit"] - out["forecast_opex"]
    out["budget_revenue"] = out["budget_units"] * out["budget_price"]
    out["budget_cogs"] = out["budget_revenue"] * out["budget_cogs_pct"]
    out["budget_ebitda"] = out["budget_revenue"] - out["budget_cogs"] - out["budget_opex"]
    out["revenue_variance"] = out["forecast_revenue"] - out["budget_revenue"]
    out["ebitda_variance"] = out["forecast_ebitda"] - out["budget_ebitda"]
    return out


def main() -> None:
    assumptions = pd.read_csv(ROOT / "monthly_assumptions.csv")
    scenarios = [
        build_scenario(assumptions, "Base", 1.00, 1.01, 1.00),
        build_scenario(assumptions, "Upside", 1.08, 1.02, 0.98),
        build_scenario(assumptions, "Downside", 0.92, 0.99, 1.04),
    ]
    detail = pd.concat(scenarios, ignore_index=True)
    summary = (
        detail.groupby("scenario", as_index=False)
        .agg(
            revenue=("forecast_revenue", "sum"),
            gross_profit=("forecast_gross_profit", "sum"),
            opex=("forecast_opex", "sum"),
            ebitda=("forecast_ebitda", "sum"),
            revenue_variance=("revenue_variance", "sum"),
            ebitda_variance=("ebitda_variance", "sum"),
        )
    )
    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    detail.to_csv(output_dir / "monthly_forecast.csv", index=False)
    summary.to_csv(output_dir / "scenario_summary.csv", index=False)
    print(summary.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
