import streamlit as st
import pandas as pd

from utils import (
    buy_forecasts,
    rent_forecasts
)

TITLE = "🏡 Financial Analysis: Buy vs Rent"

st.set_page_config(
   page_title=TITLE,
   page_icon="📊",
   initial_sidebar_state="expanded",
)

st.title(TITLE)

with st.expander("Problem statement", expanded=False):

    st.markdown("""
    This is an attempt to model the financial decision of renting vs buying a house according to a set of configurable parameters. The goal is to produce two plots

    * Net worth of an individual that decided to rent over the next X years
    * Net worth of an individual that decided to buy over the next X years


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
        TIME_PERIOD = st.number_input("Time period (years)", value=30)
        INFLATION_RATE = st.number_input("Inflation (rate)", value=0.04)
        BUDGET = st.number_input("Budget (€)", value=350000, step=10000)
    
    with col2:
        NET_ANNUAL_INCOME = st.number_input("Monthly net income (€)", value=0, step=200) * 12
        RENT_INITIAL_AMOUNT = st.number_input(
            "Initial rent amount (€)", value=1200, step=200
        ) * 12
        MARKET_RETURN = st.number_input("Market return (rate)", value=0.05)

    with col3:
        HOUSE_APPRECIATION_RATE = st.number_input(
            "House appreciation (rate)", value=0.02
        )
        HOUSE_MAINTENANCE_COST_RATE = st.number_input(
            "House maintenance cost (rate)",
            value=0.005,
            min_value=0.000,
            step=0.005,
            format="%.3f"
        )
        DOWN_PAYMENT_RATE = st.number_input(
            "Down payment (rate)",
            help="The percentage of the house price that is paid initially a down payment.",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.05
        )
    
    with col4:
        CAPIAL_GAINS_TAX_RATE = st.number_input(
            "Capital gains tax (rate)", value=0.20
        )
        MORTGAGE_INTEREST_RATE = st.number_input(
            "Mortgage interest (rate)", value=0.03, min_value=0.0, max_value=1.0
        )
        TRANSACTION_COST_RATE = st.number_input(
            "Transaction cost (rate)", value=0.15,
            help="The cost of buying / selling a house as a percentage of the price.",
        )

HOUSE_PRICE = BUDGET / (1 + TRANSACTION_COST_RATE)
TRANSACTION_COST = HOUSE_PRICE * TRANSACTION_COST_RATE
assert round(HOUSE_PRICE + TRANSACTION_COST) == BUDGET
LOAN_AMOUNT = HOUSE_PRICE * (1 - DOWN_PAYMENT_RATE)
EXCEEDING_BUDGET = LOAN_AMOUNT
MORGATGE_TERM = TIME_PERIOD

st.info(f"""
Some additional variables that derive from the inputs above are
* the **maximum house price** affordable → {round(HOUSE_PRICE, 2)}€
* the **transaction cost** → {round(TRANSACTION_COST, 2)}€
* the **required loan amount** → {round(LOAN_AMOUNT, 2)}€
* the **exceeding budget** → {round(EXCEEDING_BUDGET, 2)}€
""",
 icon="ℹ️"
)

# calculate worth contributions for the rent scenario, including

# contributions from budget investment on the markets

rent_forcasts_df = rent_forecasts(
    time_period=TIME_PERIOD,
    rent_initial_amount=RENT_INITIAL_AMOUNT,
    inflation_rate=INFLATION_RATE,
    market_return=MARKET_RETURN,
    budget=BUDGET,
    net_annual_income=NET_ANNUAL_INCOME,
    capital_gains_tax_rate=CAPIAL_GAINS_TAX_RATE
)

# final net worth of the renter scenario

rent_forcasts_df["renter_net_worth"] = (
    rent_forcasts_df["portfolio_value_after_tax"] + 
    rent_forcasts_df["cumulative_savings"]
)

# calculate worth contributions for the buy scenario, including

# contributions from house property

buy_forecasts_house_df = buy_forecasts(
    time_period=TIME_PERIOD,
    net_annual_income=NET_ANNUAL_INCOME,
    house_price=HOUSE_PRICE,
    house_appreciation_rate=HOUSE_APPRECIATION_RATE,
    house_maintenance_cost_rate=HOUSE_MAINTENANCE_COST_RATE,
    buying_transaction_cost_rate=TRANSACTION_COST_RATE,
    loan_amount=LOAN_AMOUNT,
    mortgage_interest_rate=MORTGAGE_INTEREST_RATE,
    transaction_cost_rate=TRANSACTION_COST_RATE
)

# contributions from exceeding budget investment on the markets

buy_forecasts_markets_df = rent_forecasts(
    time_period=TIME_PERIOD,
    rent_initial_amount=0,
    inflation_rate=INFLATION_RATE,
    market_return=MARKET_RETURN,
    budget=EXCEEDING_BUDGET,
    net_annual_income=NET_ANNUAL_INCOME,
    capital_gains_tax_rate=CAPIAL_GAINS_TAX_RATE
)

buy_forecasts_df = pd.merge(
    buy_forecasts_house_df,
    buy_forecasts_markets_df,
    left_index=True,
    right_index=True,
    suffixes=("_house", "_markets")
)

# final net worth of the buyer scenario

buy_forecasts_df["buyer_net_worth"] = (
    buy_forecasts_df["house_value_after_tax"] +
    buy_forecasts_df["buying_transaction_cost"] +
    buy_forecasts_df["mortgage_principal_pending_amount"] +
    buy_forecasts_df["cumulative_buyer_savings"] +
    buy_forecasts_df["portfolio_value_after_tax"]
)

# diplaying the results

analysis = pd.merge(
    rent_forcasts_df,
    buy_forecasts_df,
    left_index=True,
    right_index=True,
    suffixes=("_rent", "_buy")
)

st.header(f"Net worth of Rent vs Buy over the next {TIME_PERIOD} years")

st.line_chart(
    data=analysis[["renter_net_worth", "buyer_net_worth"]],
    # green and red colors in hex format
    color=["#00ff00", "#ff0000"]
)

st.header(f"Buy net worth contributions")
st.bar_chart(
    data=buy_forecasts_df[
        [
            "house_value_after_tax",
            "buying_transaction_cost",
            "mortgage_principal_pending_amount",
            "cumulative_buyer_savings",
            "portfolio_value_after_tax"
        ]
    ]
)

st.header(f"Raw calculations")

st.dataframe(analysis)
