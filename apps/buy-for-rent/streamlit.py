import streamlit as st
import numpy as np
import pandas as pd

from shared.financial import (
    buy_forecasts
)

st.title("Buy for Rent")

with st.expander("Problem statement", expanded=False):

    st.markdown("""
    Given a set of parameters, we calculate the ROI of a rental property (short term and long term) over a period of time and compare with stock market returns.

    In order to calculate the ROI, we use the out-of-pocker method, which is described [here](https://www.fool.com/investing/stock-market/market-sectors/real-estate-investing/roi/).
    The out-of-pocket method defines the ROI as the net profit from the investment divided by the total amount of money invested.
    > `ROI = (Net Profit / Initial Investment) * 100`

    For the house, the net profit is the sum of the aggregated cashflow from the rental plus the home equity.
    > `Net Profit = Cashflow + Home Equity - Initial Investment (Down Payment)`

    The cashflow is the difference between the income from renting the house and the costs of owning the house, including the mortgage payment.
    > `Cashflow = Income - Costs`

    The home equity is the difference between the house value and the mortgage principal pending amount.
    > `Home Equity = House Value - Mortgage Principal Pending Amount`
    """)

with st.sidebar:
    st.header("Parameters")
    with st.expander("House Parameters", expanded=False):
        house_price = st.number_input("House Price", value=200000, step=10000)
        airbnb_multiplier = st.slider("Airbnb Multiplier", min_value=2, max_value=8, value=3,
            help="The number of times the monthly rent that the house can be rented out in a month in Airbnb (or similar)."
        )
        usage_pct = st.slider("Usage Percentage", min_value=0.1, max_value=0.5, value=0.2,
            help="The percentage of the time that the house is rented out."
        )
        maintenance_pct = st.slider("Maintenance Percentage", min_value=0.001, max_value=0.01, value=0.005, step=0.001)
        service_fee = st.slider("Service Fee", min_value=0.03, max_value=0.2, value=0.10)
        annual_suplies = st.number_input("Annual Suplies", value=1200, help="Annual suplies for the house.")
        rent_expectation_rate = st.slider(
            "Rent Expectation Rate (%)", min_value=2.0, max_value=6.0, value=3.5, step=0.5,
            help="The pct of the house price that is expected ot collect as annual rent."
            ) / 100 # https://www.youtube.com/watch?v=VRDTZmOFDzs&t=2s

    with st.expander("Tax Parameters", expanded=False):
        effective_tax_rate = st.slider("Effective Tax Rate", min_value=0.1, max_value=0.5, value=0.3)

    with st.expander("Mortgage Parameters", expanded=False):
        down_payment_rate = st.slider("Down Payment Rate", min_value=0.0, max_value=1.0, value=0.2)
        annual_interest_rate = st.number_input("Annual Interest Rate", value=2.8, step=0.1) / 100
        total_time_period_in_years = st.number_input("Total Time Period (in years)", value=30)

    with st.expander("Opportunity Parameters", expanded=False):
        market_return = st.slider("Market Return", min_value=-0.1, max_value=0.2, value=0.06)
        private_use_nights = st.number_input("Private Use Nights", value=20)
        inflation_rate = st.number_input("Inflation Rate", value=0.02)

down_payment = house_price * down_payment_rate
principal = house_price - down_payment
buy_forecasts_house_df = buy_forecasts(
    time_period=total_time_period_in_years,
    net_annual_income=0,
    house_price=house_price,
    house_appreciation_rate=inflation_rate,
    house_maintenance_cost_rate=maintenance_pct,
    buying_transaction_cost_rate=0.1,
    loan_amount=principal,
    mortgage_interest_rate=annual_interest_rate
)

results = pd.DataFrame()
results["house_value"] = buy_forecasts_house_df["house_value"]
results["mortgage_principal_pending_amount"] = buy_forecasts_house_df["mortgage_principal_pending_amount"].abs()
results["home_equity"] = results["house_value"] - results["mortgage_principal_pending_amount"]
results["expected_annual_rent"] = results["house_value"] * rent_expectation_rate
results["inflation_rate"] = inflation_rate

# Long term renter
results["Long term renter income"] = results["expected_annual_rent"]
results["Long term renter costs"] = (
    buy_forecasts_house_df["mortgage_payment"] + (buy_forecasts_house_df["house_value"] * maintenance_pct)
)
results["Long term renter cashflow"] = results["Long term renter income"] - results["Long term renter costs"]
results["Long term renter cummulative cashflow"] = results["Long term renter cashflow"].cumsum()
results["Long term renter net worth"] = results["Long term renter cummulative cashflow"] + results["home_equity"]
results["Long term renter net profit"] = results["Long term renter net worth"] - down_payment
results["Long term renter cummulative ROI"] = results["Long term renter net profit"] / down_payment
results["Long term renter incremental ROI"] = results["Long term renter net worth"].pct_change()

# Short term renter
private_use_pct = private_use_nights / 365
effective_use_pct = usage_pct - private_use_pct
results["Short term renter income"] = results["expected_annual_rent"] * airbnb_multiplier * effective_use_pct
results["Short term renter costs"] = (
    buy_forecasts_house_df["mortgage_payment"] +
    buy_forecasts_house_df["house_value"] * maintenance_pct * effective_use_pct + # maintenance costs depend on usage
    results["expected_annual_rent"] * airbnb_multiplier * effective_use_pct * service_fee + # airbnb take
    annual_suplies * effective_use_pct
)
results["Short term renter cashflow"] = results["Short term renter income"] - results["Short term renter costs"]
results["Short term renter cummulative cashflow"] = results["Short term renter cashflow"].cumsum()
results["Short term renter net worth"] = results["Short term renter cummulative cashflow"] + results["home_equity"]
results["Short term renter net profit"] = results["Short term renter net worth"] - down_payment
results["Short term renter cummulative ROI"] = results["Short term renter net profit"] / down_payment
results["Short term renter incremental ROI"] = results["Short term renter net worth"].pct_change()

# Market returns
results["Market returns"] = market_return
results["Market returns cummulative ROI"] = (1 + results["Market returns"]).cumprod()

mortgage_payment = buy_forecasts_house_df["mortgage_payment"].values[0] / 12

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label="Monthly mortgage (€)",
    value=int(mortgage_payment)
)
col2.metric(
    label="Monthly rent (€)",
    value=int(results["expected_annual_rent"].values[0] / 12)
)
col3.metric(
    label="Fortnightly Airbnb ticket (€)",
    value=int(results["expected_annual_rent"].values[0] * airbnb_multiplier / 26)
)
col4.metric(
    label="Down payment (€)",
    value=int(down_payment)
)

st.header("Compared ROI")
st.line_chart(
    data=results[[
        "Long term renter cummulative ROI",
        "Short term renter cummulative ROI",
        "Market returns cummulative ROI"
    ]],
    # green, red and blue colors in hex format
    color=["#00FF00", "#FF0000", "#0000FF"]
)

st.header("Compared incremental ROI")
st.line_chart(
    data=results[[
        "Long term renter incremental ROI",
        "Short term renter incremental ROI",
        "Market returns",
        "inflation_rate"
    ]],
    # green, red, blue and yellow colors in hex format
    color=["#00FF00", "#FF0000", "#0000FF", "#FFFF00"]
)

st.expander("Raw calculations", expanded=False).write(results)
