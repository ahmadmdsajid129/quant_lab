from typing import Dict, Any, List


def audit_research_methodology(
    strategy_description: str,
    slippage_pct: float = 0.0,
    commission_bps: float = 0.0,
    num_trials_tested: int = 1,
    reported_sharpe: float = 1.0,
    uses_chronological_split: bool = True,
    execution_at_next_bar_open: bool = True,
) -> Dict[str, Any]:
    """
    Rigorously audit quantitative research methodology against common statistical pitfalls.
    """
    findings: List[Dict[str, str]] = []
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    # 1. Lookahead / execution leakage check
    if not execution_at_next_bar_open:
        findings.append({
            "category": "Lookahead Bias",
            "severity": "HIGH",
            "title": "Same-Bar Execution Leakage Detected",
            "description": "Executing orders at the closing price of the signal generation bar assumes instant fill without market latency. Signals at bar t must execute at open of bar t+1.",
        })
        severity_counts["HIGH"] += 1

    # 2. Chronological data split
    if not uses_chronological_split:
        findings.append({
            "category": "Data Leakage",
            "severity": "HIGH",
            "title": "Non-Chronological Train/Test Partitioning",
            "description": "Standard random K-Fold cross validation leaks future market regimes into past training sets. Purged Walk-Forward or Purged K-Fold with embargo is strictly required.",
        })
        severity_counts["HIGH"] += 1

    # 3. Transaction cost realism
    if slippage_pct <= 0.0 and commission_bps <= 0.0:
        findings.append({
            "category": "Cost Unrealistic",
            "severity": "HIGH",
            "title": "Zero Transaction Cost & Slippage Assumption",
            "description": "Backtest assumes zero commission and zero market impact slippage. High-frequency or high-turnover strategies will drastically degrade under institutional friction.",
        })
        severity_counts["HIGH"] += 1
    elif commission_bps < 2.0:
        findings.append({
            "category": "Cost Unrealistic",
            "severity": "MEDIUM",
            "title": "Sub-Institutional Commission Assumptions",
            "description": "Commission assumption of < 2 bps may underestimate exchange taker fees and clearing costs.",
        })
        severity_counts["MEDIUM"] += 1

    # 4. Multiple testing p-hacking check
    if num_trials_tested >= 10:
        findings.append({
            "category": "Multiple Testing",
            "severity": "MEDIUM",
            "title": f"Selection Bias Warning ({num_trials_tested} Trials Tested)",
            "description": f"Testing {num_trials_tested} strategy variations inflates the probability of backtest overfitting. A Deflated Sharpe Ratio (DSR) haircut must be applied.",
        })
        severity_counts["MEDIUM"] += 1

    # 5. Sharpe credibility check
    if reported_sharpe > 3.0:
        findings.append({
            "category": "Plausibility",
            "severity": "HIGH",
            "title": f"Suspiciously High Reported Sharpe Ratio ({reported_sharpe:.2f})",
            "description": "Annualized Sharpe ratios > 3.0 over long horizons almost always indicate undetected lookahead bias, survivorship bias, or extreme illiquidity.",
        })
        severity_counts["HIGH"] += 1

    is_compliant = severity_counts["HIGH"] == 0
    score = max(0, 100 - (severity_counts["HIGH"] * 30 + severity_counts["MEDIUM"] * 15))

    return {
        "is_methodologically_sound": is_compliant,
        "methodology_health_score": score,
        "severity_summary": severity_counts,
        "findings": findings,
        "recommended_next_experiments": [
            "Run Purged K-Fold validation with 5-day embargo window",
            "Perform Monte Carlo trade shuffle test",
            "Stress-test against 2x slippage and 5x commission",
        ],
    }
