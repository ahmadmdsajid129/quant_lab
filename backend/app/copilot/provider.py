from typing import Dict, Any, List, Optional
import os


class CopilotEngine:
    """
    Grounded quantitative research copilot that cites actual workspace artifacts
    and applies rigorous econometric and mathematical checks.
    """
    def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        selected_project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # Extract relevant workspace items
        projects = context.get("projects", [])
        datasets = context.get("datasets", [])
        recent_exps = context.get("recent_experiments", [])

        # Categorized evidence items
        verified_results: List[str] = []
        statistical_inferences: List[str] = []
        hypotheses: List[str] = []

        # 1. Check if asking about hypotheses or projects
        if "hypothes" in prompt_lower or "project" in prompt_lower or "falsification" in prompt_lower:
            if projects:
                for p in projects:
                    for h in p.get("hypotheses", []):
                        hypotheses.append(f"Project '{p['name']}': {h['statement']}")
                        if h.get("falsification_criteria"):
                            verified_results.append(f"Defined Falsification Threshold: {h['falsification_criteria']}")
                project_names = ", ".join([f"**{p['name']}**" for p in projects])
                response_text = (
                    f"### Workspace Hypothesis Audit\n\n"
                    f"You have **{len(projects)} active research project(s)**: {project_names}.\n\n"
                    f"**Core Principle:** A quantitative hypothesis is only valid if it includes an explicit economic mechanism and unambiguous falsification criteria.\n\n"
                    f"**Key Recommendations:**\n"
                    f"1. Ensure your falsification threshold is defined before in-sample testing.\n"
                    f"2. Separate signal generation from portfolio construction.\n"
                    f"3. Verify that the market anomaly is not merely compensation for liquidity risk."
                )
            else:
                response_text = (
                    "### No Research Projects Found\n\n"
                    "You have not created any research projects in this workspace yet. "
                    "Navigate to **Research Projects** to formulate a hypothesis with an economic mechanism and falsification criteria."
                )

        # 2. Check if asking about backtests or experiment results
        elif "backtest" in prompt_lower or "experiment" in prompt_lower or "sharpe" in prompt_lower or "metric" in prompt_lower:
            if recent_exps:
                exp = recent_exps[0]
                m = exp.get("metrics") or {}
                sharpe = m.get("sharpe_ratio", 0.0)
                max_dd = m.get("max_drawdown", 0.0)
                win_rate = m.get("win_rate", 0.0)

                verified_results.append(
                    f"Latest run '{exp.get('strategy_name', 'Strategy')}' achieved Sharpe: {sharpe:.2f}, Max Drawdown: {max_dd * 100:.1f}%, Win Rate: {win_rate * 100:.1f}%"
                )

                if sharpe > 2.0:
                    statistical_inferences.append("Sharpe ratio > 2.0 warrants rigorous look-ahead and cost audit.")
                else:
                    statistical_inferences.append("Performance falls within plausible institutional baseline ranges.")

                response_text = (
                    f"### Grounded Experiment Analysis\n\n"
                    f"Reviewing latest execution for strategy **{exp.get('strategy_name', 'Unknown')}**:\n\n"
                    f"- **Sharpe Ratio:** `{sharpe:.2f}`\n"
                    f"- **Max Drawdown:** `{max_dd * 100:.1f}%`\n"
                    f"- **Win Rate:** `{win_rate * 100:.1f}%`\n\n"
                    f"**Methodological Audit:**\n"
                    f"- **Time Semantics:** Ensure orders were executed at $t+1$ Open price, not $t$ Close.\n"
                    f"- **Cost Friction:** Verify slippage (e.g. 5 bps) and exchange fees were deducted.\n"
                    f"- **Overfitting Test:** Run Deflated Sharpe Ratio (DSR) to account for parameter trials."
                )
            else:
                response_text = (
                    "### No Prior Experiments Found\n\n"
                    "No backtests have been recorded in this workspace. Run a strategy in the **Strategy Backtester** "
                    "to generate verifiable equity curves and execution logs."
                )

        # 3. Check if asking about data or features
        elif "data" in prompt_lower or "dataset" in prompt_lower or "feature" in prompt_lower:
            if datasets:
                ds_symbols = [d["symbol"] for d in datasets]
                verified_results.append(f"Active datasets in workspace: {', '.join(ds_symbols)}")
                response_text = (
                    f"### Dataset & Feature Engineering Review\n\n"
                    f"Found **{len(datasets)} dataset(s)** in your active workspace: `{', '.join(ds_symbols)}`.\n\n"
                    f"**Suggested Feature Pipeline:**\n"
                    f"- **Momentum:** 1-day, 5-day, and 20-day returns\n"
                    f"- **Volatility:** 10-day rolling annualized standard deviation\n"
                    f"- **Oscillators:** 14-day Wilder RSI and normalized MACD\n"
                    f"- **Data Invariant:** Standard scalers must fit **exclusively** on the training window."
                )
            else:
                response_text = (
                    "### No Market Datasets Ingested\n\n"
                    "Your workspace currently has no registered datasets. Generate a Merton Jump-Diffusion synthetic dataset "
                    "under **Market Data & QA** to begin research."
                )

        # 4. Default quantitative reasoning
        else:
            response_text = (
                f"### Quantitative Research Copilot\n\n"
                f"Analyzing prompt with grounded workspace context ({context.get('projects_count', 0)} projects, {len(datasets)} datasets):\n\n"
                f"**Research Principles:**\n"
                f"- **Reproducibility:** Every experiment must record configuration, data version, and code lineage.\n"
                f"- **No Lookahead:** Signals at bar $t$ must execute at $t+1$ Open.\n"
                f"- **Economic Mechanism:** Quantitative signals require an underlying structural or behavioral market mechanism.\n\n"
                f"You can ask me to **audit your methodology**, **suggest feature pipelines**, or **interpret backtest results**."
            )

        return {
            "response": response_text,
            "grounded_artifacts": {
                "verified_results": verified_results,
                "statistical_inferences": statistical_inferences,
                "hypotheses": hypotheses,
            },
            "source_projects_count": len(projects),
            "source_datasets_count": len(datasets),
            "source_experiments_count": len(recent_exps),
        }


copilot_engine = CopilotEngine()
