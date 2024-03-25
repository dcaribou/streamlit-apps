import streamlit as st
import numpy as np
import pandas as pd

from shared.financial import (
    buy_forecasts
)

st.title("Buy for Rent")

with st.expander("Problem statement", expanded=False):

    st.markdown("""
Given a set of parameters, we calculate the ROI of buying a property for renting (short term and long term) over a period of time and compare with stock market returns.

In order to calculate the ROI, we use the out-of-pocker method, which is described [here](https://www.fool.com/investing/stock-market/market-sectors/real-estate-investing/roi/).
The out-of-pocket method defines the ROI as the net profit from the investment divided by the total amount of money invested.
> `ROI = (Net Profit / Total Investment) * 100`

For the house, the net profit is the sum of the cashflow from renting the house plus the home equity.
> `Net Profit = Cashflow + Home Equity`

The cashflow is the difference between the income from renting the house and the costs of owning the house, including the mortgage payment.
> `Cashflow = Income - Costs`

The home equity is the difference between the house value and the mortgage principal pending amount.
> `Home Equity = House Value - Mortgage Principal Pending Amount`
""")

with st.sidebar:
    st.header("Parameters")
    with st.expander("House Parameters", expanded=False):
        house_price = st.number_input("House Price", value=200000)
        airbnb_multiplier = st.slider("Airbnb Multiplier", min_value=2, max_value=5, value=3,
            help="The number of times the monthly rent that the house can be rented out in a month in Airbnb (or similar)."
        )
        usage_pct = st.slider("Usage Percentage", min_value=0.1, max_value=0.5, value=0.2,
            help="The percentage of the time that the house is rented out."
        )
        maintenance_pct = st.slider("Maintenance Percentage", min_value=0.001, max_value=0.01, value=0.005)
        service_fee = st.slider("Service Fee", min_value=0.03, max_value=0.2, value=0.10)
        annual_suplies = st.number_input("Annual Suplies", value=1200, help="Annual suplies for the house.")
        appreciation_rate = st.slider("Appreciation Rate", min_value=0.01, max_value=0.1, value=0.02)
        rent_expectation_rate = st.slider(
            "Rent Expectation Rate", min_value=0.02, max_value=0.1, value=0.05,
            help="The pct of the house price that is expected ot collect as annual rent."
            ) # https://www.youtube.com/watch?v=VRDTZmOFDzs&t=2s

    with st.expander("Tax Parameters", expanded=False):
        effective_tax_rate = st.slider("Effective Tax Rate", min_value=0.1, max_value=0.5, value=0.3)

    with st.expander("Mortgage Parameters", expanded=False):
        down_payment_rate = st.slider("Down Payment Rate", min_value=0.0, max_value=1.0, value=0.2)
        annual_interest_rate = st.number_input("Annual Interest Rate", value=0.03)
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
    house_appreciation_rate=appreciation_rate,
    house_maintenance_cost_rate=maintenance_pct,
    buying_transaction_cost_rate=0.1,
    loan_amount=principal,
    mortgage_interest_rate=annual_interest_rate
)

st.dataframe(buy_forecasts_house_df)

results = pd.DataFrame()
results["house_value"] = buy_forecasts_house_df["house_value"] 
results["total_home_equity"] = buy_forecasts_house_df["house_value"] + buy_forecasts_house_df["mortgage_principal_pending_amount"]
# the home equity gain is the gain in equity compared with the previous year
results["home_equity_gain"] = results["total_home_equity"].diff()
results["expected_annual_rent"] = results["house_value"] * rent_expectation_rate

# Long term renter
results["Long term renter income"] = results["expected_annual_rent"]
results["Long term renter costs"] = (
    buy_forecasts_house_df["mortgage_payment"] + buy_forecasts_house_df["house_value"] * maintenance_pct
)
results["Long term renter cashflow"] = results["Long term renter income"] - results["Long term renter costs"]
results["Long term renter net profit"] = results["Long term renter cashflow"] + results["home_equity_gain"]
results["Long term renter ROI (before taxes)"] = (results["Long term renter net profit"] / down_payment)

# Short term renter
private_use_pct = private_use_nights / 365
effective_use_pct = usage_pct - private_use_pct
results["Short term renter income"] = buy_forecasts_house_df["mortgage_payment"] * airbnb_multiplier * effective_use_pct
results["Short term renter costs"] = (
    buy_forecasts_house_df["mortgage_payment"] +
    buy_forecasts_house_df["house_value"] * maintenance_pct * effective_use_pct + # maintenance costs depend on usage
    results["expected_annual_rent"] * airbnb_multiplier * effective_use_pct * service_fee + # airbnb take
    annual_suplies * effective_use_pct
)
results["Short term renter cashflow"] = results["Short term renter income"] - results["Short term renter costs"]
results["Short term renter net profit"] = results["Short term renter cashflow"] + results["home_equity_gain"]
results["Short term renter ROI (before taxes)"] = (results["Short term renter net profit"] / down_payment)

st.dataframe(results)
