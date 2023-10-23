import streamlit as st
import pandas as pd

from utils import calculate_yearly_amortization_amounts

TITLE = "Finantial Analysis: Buy vs Rent"

st.set_page_config(
   page_title=TITLE,
   page_icon="📊",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.title(TITLE)

with st.expander("Model Inputs", expanded=False):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        YEAR_START = st.number_input("Year start", value=2023)
        ANALYSIS_TERM = st.number_input("Analysis term", value=30)
        INFLATION_RATE = st.number_input("Inflation rate", value=0.04)
    
    with col2:
        INITIAL_RENT_AMOUNT = st.number_input(
            "Initial rent amount", value=1200 * 12
        )
        MARKET_RETURN = st.number_input("Market return", value=0.05)
        HOUSE_PRICE = st.number_input("House price", value=350000, format="%u")

    with col3:
        HOUSE_APPRECIATION_RATE = st.number_input(
            "House appreciation rate", value=0.02
        )
        HOUSE_MAINTENANCE_COST_RATE = st.number_input(
            "House maintenance cost rate", value=0.01
        )
        DOWN_PAYMENT_RATE = st.number_input("Down payment rate", value=0.5)
    
    with col4:
        CAPIAL_GAINS_TAX_RATE = st.number_input(
            "Capital gains tax rate", value=0.20
        )
        MORTGAGE_INTEREST_RATE = st.number_input(
            "Mortgage interest rate", value=0.03
        )
        BUYING_TRANSACTION_COST_RATE = st.number_input(
            "Buying transaction cost rate", value=0.15
        )
        SELLING_TRANSACTION_COST_RATE = st.number_input(
            "Selling transaction cost rate", value=0.10
        )


YEAR_END = YEAR_START + ANALYSIS_TERM
LOAN_AMOUNT = HOUSE_PRICE * (1 - DOWN_PAYMENT_RATE)
MORGATGE_TERM = ANALYSIS_TERM

mortgage_payment_plan_yearly = calculate_yearly_amortization_amounts(
    year_start=YEAR_START,
    loan_amount=LOAN_AMOUNT,
    mortgage_periods=MORGATGE_TERM,
    mortgage_interest_rate=MORTGAGE_INTEREST_RATE,
)

analysis = pd.DataFrame()

analysis.index = range(YEAR_START, YEAR_END)

analysis["inflation_rate"] = INFLATION_RATE
analysis["market_return"] = MARKET_RETURN
analysis["down_payment"] = HOUSE_PRICE * DOWN_PAYMENT_RATE
analysis["house_appreciation_rate"] = HOUSE_APPRECIATION_RATE

analysis["cumulative_inflation_rate"] = (1 + analysis["inflation_rate"]).cumprod()
analysis["cumulative_market_return"] = (1 + analysis["market_return"]).cumprod()

# renter calculations

analysis["rent_amount"] = INITIAL_RENT_AMOUNT * analysis["cumulative_inflation_rate"]
analysis["portfiolio_value"] = analysis["down_payment"] * analysis["cumulative_market_return"]
analysis["portfiolio_value_after_tax"] = analysis["portfiolio_value"] * (1 - CAPIAL_GAINS_TAX_RATE)
analysis["renter_net_woth"] = (
    analysis["portfiolio_value_after_tax"] - analysis["rent_amount"]
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
analysis["buyer_net_worth"] = (
    analysis["house_value_after_tax"] -
    (analysis["house_value"] * HOUSE_MAINTENANCE_COST_RATE) -
    (analysis["buying_transaction_cost"]) -
    (LOAN_AMOUNT - analysis["cumulative_mortgage_principal"])
)


st.line_chart(analysis[["renter_net_woth", "buyer_net_worth"]])
