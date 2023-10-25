import pandas as pd
import numpy_financial as npf

def renter_forecasts():
    pass

def buyer_forecasts():
    pass

def calculate_yearly_amortization_amounts(
    year_start: int,
    loan_amount: float,
    mortgage_periods: int,
    mortgage_interest_rate: float

) -> pd.DataFrame:
    """Compute the morgage payment plan for the mortgage term, including
    - Yearly payment
    - Yearly principal
    - Yearly interest
    """

    mortgage_payment_plan = pd.DataFrame()

    year_end = year_start + mortgage_periods

    mortgage_payment_plan.index = pd.date_range(
        start=f'{year_start}-01-01',
        end=f'{year_end-1}-12-31',
        freq='M'
    )

    MORTGAGE_PAYMENT = -npf.pmt(
        pv=loan_amount,
        nper=mortgage_periods*12,
        rate=mortgage_interest_rate/12 # TODO: not sure if i can just divide the annual rate by 12 to get the monthly rate
    )

    mortgage_payment_plan["payment"] = MORTGAGE_PAYMENT
    mortgage_payment_plan["period"] = range(1, (mortgage_periods*12) +1 )
    mortgage_payment_plan["principal"] = -npf.ppmt(
        rate=mortgage_interest_rate/12,
        per=mortgage_payment_plan["period"],
        nper=mortgage_periods*12,
        pv=loan_amount
    )
    mortgage_payment_plan["interest"] = -npf.ipmt(
        rate=mortgage_interest_rate/12,
        per=mortgage_payment_plan["period"],
        nper=mortgage_periods*12,
        pv=loan_amount
    )

    assert (
        mortgage_payment_plan["payment"].round(2) == 
        (mortgage_payment_plan["principal"] + mortgage_payment_plan["interest"]).round(2)
    ).all()

    # aggregate at the year level
    mortgage_payment_plan["year"] = mortgage_payment_plan.index.year
    mortgage_payment_plan_yearly = mortgage_payment_plan.groupby("year").sum()

    del mortgage_payment_plan_yearly["period"]
    mortgage_payment_plan_yearly.index = pd.date_range(
        start=f'{year_start}-01-01',
        end=f'{year_end-1}-12-31',
        freq='Y'
    )

    return mortgage_payment_plan_yearly
