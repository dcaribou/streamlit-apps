import streamlit as st
import pandas as pd

from utils import calculate_yearly_amortization_amounts

TITLE = "Financial Analysis: Buy vs Rent"

st.set_page_config(
   page_title=TITLE,
   page_icon="📊",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.title(TITLE)

st.markdown("""
This is an attempt to model the financial decision of renting vs buying a house according to a set of configurable parameters. The goal is to produce two plots

* Net worth of an individual that decided to rent over the next 30 years
* Net worth of an individual that decided to buy over the next 30 years

The net worth of an individual who rents is calculated as
```
(the net amount they can sell their investments for at a point in time)
    - (the accumulated expenses on the renting scenario)
```

The net worth of an individual who buys a house is calculated as
```
(the net amount they can sell the house for at a point in time) 
    - (the amount that is remaining on the mortgage) 
    - (the accumulated expenses on the renting scenario)
    + (the capital gains on the exceeding budget)
```
"""
)

with st.expander("Model Inputs", expanded=False):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        YEAR_START = st.number_input("Year start", value=2023)
        ANALYSIS_TERM = st.number_input("Analysis term", value=30)
        INFLATION_RATE = st.number_input("Inflation rate", value=0.04)
        BUDGET = st.number_input("Budget", value=350000, format="%d")
    
    with col2:
        NET_ANNUAL_INCOME = st.number_input("Monthly net income", value=3000, step=200) * 12
        INITIAL_RENT_AMOUNT = st.number_input(
            "Initial rent amount", value=1200 * 12
        )
        MARKET_RETURN = st.number_input("Market return", value=0.05)

    with col3:
        HOUSE_APPRECIATION_RATE = st.number_input(
            "House appreciation rate", value=0.02
        )
        HOUSE_MAINTENANCE_COST_RATE = st.number_input(
            "House maintenance cost rate", value=0.01
        )
        DOWN_PAYMENT_RATE = st.number_input(
            "Down payment rate",
            help="The percentage of the house price that is paid initially a down payment.",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.05
        )
    
    with col4:
        CAPIAL_GAINS_TAX_RATE = st.number_input(
            "Capital gains tax rate", value=0.20
        )
        MORTGAGE_INTEREST_RATE = st.number_input(
            "Mortgage interest rate", value=0.03, min_value=0.0, max_value=1.0
        )
        BUYING_TRANSACTION_COST_RATE = st.number_input(
            "Buying transaction cost rate", value=0.15
        )
        SELLING_TRANSACTION_COST_RATE = st.number_input(
            "Selling transaction cost rate", value=0.10
        )

YEAR_END = YEAR_START + ANALYSIS_TERM
HOUSE_PRICE = BUDGET / (1 + BUYING_TRANSACTION_COST_RATE)
BUYING_TRANSACTION_COST = HOUSE_PRICE * BUYING_TRANSACTION_COST_RATE
assert HOUSE_PRICE + BUYING_TRANSACTION_COST == BUDGET
LOAN_AMOUNT = HOUSE_PRICE * (1 - DOWN_PAYMENT_RATE)
EXCEEDING_BUDGET = LOAN_AMOUNT
MORGATGE_TERM = ANALYSIS_TERM

st.info(f"The current settings simulate a house price of ${round(HOUSE_PRICE, 2)}", icon="ℹ️")

mortgage_payment_plan_yearly = calculate_yearly_amortization_amounts(
    year_start=YEAR_START,
    loan_amount=LOAN_AMOUNT,
    mortgage_periods=MORGATGE_TERM,
    mortgage_interest_rate=MORTGAGE_INTEREST_RATE,
)

analysis = pd.DataFrame()

analysis.index = pd.date_range(
    start=f'{YEAR_START}-01-01',
    end=f'{YEAR_END-1}-12-31',
    freq='Y'
)

analysis["inflation_rate"] = INFLATION_RATE
analysis["market_return"] = MARKET_RETURN
analysis["house_appreciation_rate"] = HOUSE_APPRECIATION_RATE
analysis["budget"] = BUDGET
analysis["exceeding_budget"] = EXCEEDING_BUDGET

analysis["cumulative_inflation_rate"] = (1 + analysis["inflation_rate"]).cumprod()
analysis["cumulative_market_return"] = (1 + analysis["market_return"]).cumprod()

analysis["net_annual_income"] = NET_ANNUAL_INCOME * analysis["cumulative_inflation_rate"]

# renter calculations

analysis["rent_amount"] = INITIAL_RENT_AMOUNT * analysis["cumulative_inflation_rate"]
analysis["renter_savings"] = analysis["net_annual_income"] - analysis["rent_amount"]
analysis["cumulative_renter_savings"] = analysis["renter_savings"].cumsum()
analysis["renter_portfolio_value"] = (
    analysis["budget"] * analysis["cumulative_market_return"]
)
analysis["renter_portfolio_value_after_tax"] = (
    analysis["renter_portfolio_value"] - 
    (analysis["renter_portfolio_value"] - analysis["budget"]) * CAPIAL_GAINS_TAX_RATE
)
analysis["renter_net_woth"] = (
    analysis["renter_portfolio_value_after_tax"] + analysis["cumulative_renter_savings"]
)

# buyer calculations

analysis["cumulative_house_appreciation"] = (1 + analysis["house_appreciation_rate"]).cumprod()
analysis["house_value"] = HOUSE_PRICE * analysis["cumulative_house_appreciation"]
analysis["buying_transaction_cost"] = HOUSE_PRICE * BUYING_TRANSACTION_COST_RATE
analysis["mortgage_payment"] = mortgage_payment_plan_yearly["payment"]
analysis["mortgage_principal"] = mortgage_payment_plan_yearly["principal"]
analysis["mortgage_interest"] = mortgage_payment_plan_yearly["interest"]

analysis["house_value_after_tax"] = analysis["house_value"] * (1 - SELLING_TRANSACTION_COST_RATE)
analysis["cumulative_mortgage_principal"] = analysis["mortgage_principal"].cumsum()
analysis["buyer_savings"] = (
    analysis["net_annual_income"] - 
    analysis["mortgage_payment"] - 
    analysis["house_value"] * HOUSE_MAINTENANCE_COST_RATE
)
analysis["cumulative_buyer_savings"] = analysis["buyer_savings"].cumsum()
analysis["buyer_portfolio_value"] = analysis["exceeding_budget"] * analysis["cumulative_market_return"]
analysis["buyer_portfolio_value_after_tax"] = (
    analysis["buyer_portfolio_value"] - 
    (analysis["buyer_portfolio_value"] - analysis["exceeding_budget"]) * CAPIAL_GAINS_TAX_RATE
)
analysis["buyer_net_worth"] = (
    analysis["house_value_after_tax"] -
    analysis["buying_transaction_cost"] -
    (LOAN_AMOUNT - analysis["cumulative_mortgage_principal"]) +
    analysis["cumulative_buyer_savings"] +
    analysis["buyer_portfolio_value_after_tax"]
)

st.line_chart(analysis[["renter_net_woth", "buyer_net_worth"]])

st.dataframe(analysis)
