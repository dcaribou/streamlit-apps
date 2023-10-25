import pandas as pd
import numpy_financial as npf
import datetime

def rent_forecasts(
    time_period: int,
    rent_initial_amount: int,
    net_annual_income: int,
    inflation_rate: float,
    budget: int,
    market_return: float,
    capital_gains_tax_rate: float
):

    forecasts = pd.DataFrame()

    year_start = datetime.datetime.now().year

    year_end = year_start + time_period

    forecasts.index = pd.date_range(
        start=f'{year_start}-01-01',
        end=f'{year_end-1}-12-31',
        freq='Y'
    )

    forecasts["inflation_rate"] = inflation_rate
    forecasts["market_return"] = market_return
    forecasts["budget"] = budget

    forecasts["cumulative_inflation_rate"] = (1 + forecasts["inflation_rate"]).cumprod()
    forecasts["cumulative_market_return"] = (1 + forecasts["market_return"]).cumprod()

    forecasts["net_annual_income"] = net_annual_income * forecasts["cumulative_inflation_rate"]

    forecasts["rent_amount"] = rent_initial_amount * forecasts["cumulative_inflation_rate"]
    forecasts["savings"] = forecasts["net_annual_income"] - forecasts["rent_amount"]
    forecasts["cumulative_savings"] = forecasts["savings"].cumsum()
    forecasts["portfolio_value"] = (
        forecasts["budget"] * forecasts["cumulative_market_return"]
    )
    forecasts["portfolio_value_after_tax"] = (
        forecasts["portfolio_value"] - 
        (forecasts["portfolio_value"] - forecasts["budget"]) * capital_gains_tax_rate
    )

    return forecasts

def buy_forecasts(
    time_period: int,
    net_annual_income: int,
    house_price: int,
    house_appreciation_rate: float,
    house_maintenance_cost_rate: float,
    buying_transaction_cost_rate: float,
    loan_amount: float,
    mortgage_interest_rate: float,
    selling_transaction_cost_rate: float
):

    forecasts = pd.DataFrame()

    year_start = datetime.datetime.now().year

    year_end = year_start + time_period

    forecasts.index = pd.date_range(
        start=f'{year_start}-01-01',
        end=f'{year_end-1}-12-31',
        freq='M'
    )

    MORTGAGE_PAYMENT = -npf.pmt(
        pv=loan_amount,
        nper=time_period*12,
        rate=mortgage_interest_rate/12 # TODO: not sure if i can just divide the annual rate by 12 to get the monthly rate
    )

    forecasts["mortgage_payment"] = MORTGAGE_PAYMENT
    forecasts["mortgage_period"] = range(1, (time_period*12) +1 )
    forecasts["mortgage_principal"] = -npf.ppmt(
        rate=mortgage_interest_rate/12,
        per=forecasts["mortgage_period"],
        nper=time_period*12,
        pv=loan_amount
    )
    forecasts["mortgage_interest"] = -npf.ipmt(
        rate=mortgage_interest_rate/12,
        per=forecasts["mortgage_period"],
        nper=time_period*12,
        pv=loan_amount
    )

    assert (
        forecasts["mortgage_payment"].round(2) == 
        (forecasts["mortgage_principal"] + forecasts["mortgage_interest"]).round(2)
    ).all()

    # aggregate at the year level
    forecasts["year"] = forecasts.index.year
    forecasts = forecasts.groupby("year").sum()

    del forecasts["mortgage_period"]
    forecasts.index = pd.date_range(
        start=f'{year_start}-01-01',
        end=f'{year_end-1}-12-31',
        freq='Y'
    )
    
    forecasts["house_appreciation_rate"] = house_appreciation_rate
    forecasts["net_annual_income"] = net_annual_income
    forecasts["exceeding_budget"] = loan_amount

    forecasts["cumulative_house_appreciation"] = (1 + forecasts["house_appreciation_rate"]).cumprod()
    forecasts["house_value"] = house_price * forecasts["cumulative_house_appreciation"]
    forecasts["buying_transaction_cost"] = -(house_price * buying_transaction_cost_rate)

    forecasts["house_value_after_tax"] = forecasts["house_value"] * (1 - selling_transaction_cost_rate)
    forecasts["cumulative_mortgage_principal"] = forecasts["mortgage_principal"].cumsum()
    forecasts["buyer_savings"] = (
        forecasts["net_annual_income"] - 
        forecasts["mortgage_payment"] - 
        forecasts["house_value"] * house_maintenance_cost_rate
    )
    forecasts["cumulative_buyer_savings"] = forecasts["buyer_savings"].cumsum()
    forecasts["mortgage_principal_pending_amount"] = -(loan_amount - forecasts["cumulative_mortgage_principal"])
    

    return forecasts
