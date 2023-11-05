import streamlit as st

from utils.financial import (
    mortgage_monthly_payment,
    mortgage_principal_contribution
)


st.title("Buy for Rent")

st.text("""
Given a set of parameters, we calculate the ROI of buying a property for renting.
""")

st.header("Parameters")

st.dataframe(
    mortgage_monthly_payment(
        principal=100000,
        annual_interest_rate=0.01,
        total_time_period_in_years=30
    )
)
