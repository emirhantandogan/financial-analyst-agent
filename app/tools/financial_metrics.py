import math

import yfinance as yf


def _to_float(value):
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if math.isnan(number) or math.isinf(number):
        return None

    return number


def _get_latest_statement_value(statement, row_names):
    if statement is None or statement.empty:
        return None

    for row_name in row_names:
        if row_name not in statement.index:
            continue

        values = statement.loc[row_name].dropna()

        if values.empty:
            continue

        try:
            values = values.sort_index(ascending=False)
        except TypeError:
            pass

        return _to_float(values.iloc[0])

    return None


def get_financial_metrics(ticker: str) -> dict:
    normalized_ticker = ticker.strip().upper()

    try:
        stock = yf.Ticker(normalized_ticker)

        info = stock.get_info()

        quarterly_income = stock.get_income_stmt(
            freq="quarterly"
        )

        earnings_history = stock.get_earnings_history()

        earnings_estimate = stock.get_earnings_estimate()

        revenue_estimate = stock.get_revenue_estimate()

        latest_quarter_revenue = _get_latest_statement_value(
            quarterly_income,
            [
                "TotalRevenue",
                "OperatingRevenue",
            ],
        )

        latest_reported_eps = None
        latest_eps_estimate = None
        latest_eps_surprise_percent = None

        if (
            earnings_history is not None
            and not earnings_history.empty
            and "epsActual" in earnings_history.columns
        ):
            reported_earnings = earnings_history.dropna(
                subset=["epsActual"]
            )

            if not reported_earnings.empty:
                reported_earnings = reported_earnings.sort_index(
                    ascending=False
                )

                latest_earnings = reported_earnings.iloc[0]

                latest_reported_eps = _to_float(
                    latest_earnings.get("epsActual")
                )

                latest_eps_estimate = _to_float(
                    latest_earnings.get("epsEstimate")
                )

                latest_eps_surprise_percent = _to_float(
                    latest_earnings.get("surprisePercent")
                )

        current_quarter_eps_consensus = None

        if (
            earnings_estimate is not None
            and not earnings_estimate.empty
            and "0q" in earnings_estimate.index
        ):
            current_quarter_eps_consensus = _to_float(
                earnings_estimate.loc["0q"].get("avg")
            )

        current_quarter_revenue_consensus = None

        if (
            revenue_estimate is not None
            and not revenue_estimate.empty
            and "0q" in revenue_estimate.index
        ):
            current_quarter_revenue_consensus = _to_float(
                revenue_estimate.loc["0q"].get("avg")
            )

        total_debt = _to_float(
            info.get("totalDebt")
        )

        ebitda = _to_float(
            info.get("ebitda")
        )

        debt_to_ebitda = None

        if (
            total_debt is not None
            and ebitda is not None
            and ebitda != 0
        ):
            debt_to_ebitda = total_debt / ebitda

        return {
            "ticker": normalized_ticker,
            "company_name": (
                info.get("longName")
                or info.get("shortName")
            ),
            "currency": info.get("currency"),
            "latest_quarter_revenue": latest_quarter_revenue,
            "latest_reported_eps": latest_reported_eps,
            "latest_eps_estimate": latest_eps_estimate,
            "latest_eps_surprise_percent": (
                latest_eps_surprise_percent
            ),
            "trailing_pe": _to_float(
                info.get("trailingPE")
            ),
            "total_debt": total_debt,
            "ebitda": ebitda,
            "debt_to_ebitda": debt_to_ebitda,
            "current_quarter_eps_consensus": (
                current_quarter_eps_consensus
            ),
            "current_quarter_revenue_consensus": (
                current_quarter_revenue_consensus
            ),
        }

    except Exception as exc:
        raise RuntimeError(
            f"Failed to fetch financial metrics for "
            f"{normalized_ticker}: {exc}"
        ) from exc

# ==============================================================================
# Financial Metrics Overview & Descriptions
# ==============================================================================
#
# 1. Company Identifiers:
#    - ticker: The stock market symbol used to trade the shares.
#    - company_name: Official legal or registered business name of the entity.
#    - currency: Reporting currency for all financial figures (USD, EUR, etc.).
#
# 2. Revenue & Top-Line Performance:
#    - latest_quarter_revenue: Total sales generated in the most recently reported
#      fiscal quarter. Indicates top-line size and recent operational scale.
#    - current_quarter_revenue_consensus: Average Wall Street analyst revenue
#      forecast for the ongoing quarter. Reflects near-term growth expectations.
#
# 3. Earnings Per Share (EPS) & Profitability:
#    - latest_reported_eps: Actual net income earned per outstanding share in the
#      most recent quarter. Measures bottom-line shareholder profitability.
#    - latest_eps_estimate: Consensus analyst EPS forecast prior to the latest release.
#    - latest_eps_surprise_percent: Percentage difference between actual EPS and
#      the analyst estimate. Positive values reflect an earnings beat; negative values
#      indicate missed expectations.
#    - current_quarter_eps_consensus: Average consensus analyst EPS estimate for
#      the active quarter, signaling future profitability trends.
#
# 4. Valuation:
#    - trailing_pe (P/E Ratio): Current share price divided by trailing 12-month
#      earnings per share. Assesses relative valuation and market pricing premium.
#
# 5. Leverage & Financial Solvency:
#    - total_debt: Combined short-term and long-term interest-bearing obligations.
#    - ebitda: Earnings Before Interest, Taxes, Depreciation, and Amortization.
#      Serves as a clean proxy for recurring operating cash generation.
#    - debt_to_ebitda: Leverage ratio measuring total debt relative to annual EBITDA.
#      Estimates how many years of operating earnings are required to extinguish
#      outstanding debt, indicating balance sheet risk.
# ==============================================================================