import numpy_financial as npf

def mortgage_monthly_payment(
    annual_interest_rate: float,
    principal: float,
    total_time_period_in_years: int
):
    """Calculate the monthly mortgage payment for a given principal, interest rate and time period.

    Based on reference https://onladder.co.uk/blog/how-to-calculate-mortgage-repayments/
    """
    return -npf.pmt(
        rate=annual_interest_rate / 12,
        nper=total_time_period_in_years * 12,
        pv=principal
    )

def mortgage_principal_contribution(
    annual_interest_rate: float,
    monthly_payment: float,
    month_number: int,
    total_time_period_in_years: int
):
    """For a given mortgage payment and time period, calculate the payment proportion that goes towards the principal.
    """
    pv = npf.pv(
        rate=annual_interest_rate / 12,
        nper=total_time_period_in_years*12,
        when="end",
        pmt=-monthly_payment
    )

    return -npf.ppmt(
        rate=annual_interest_rate / 12,
        per=month_number,
        nper=total_time_period_in_years*12,
        pv=pv,
        when="end"
    )
