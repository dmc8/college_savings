import streamlit as st
import plotly.express as px
import pandas as pd

def calculate_savings(inputs):
    current_age = inputs['current_age']
    college_start_age = inputs['college_start_age']
    annual_cost = inputs['annual_cost']
    college_inflation_rate = inputs['college_inflation_rate'] / 100
    years_of_college = inputs['years_of_college']
    already_saved = inputs['already_saved']
    rate_of_return = inputs['rate_of_return'] / 100
    percent_to_cover = inputs['percent_to_cover'] / 100

    if college_start_age <= current_age:
        st.error("College start age must be greater than current age")
        return None
    if not (0 <= percent_to_cover <= 1):
        st.error("Percentage to cover must be between 0 and 100")
        return None

    years_until_college = college_start_age - current_age
    future_cost_per_year = annual_cost * ((1 + college_inflation_rate) ** years_until_college)
    total_future_cost = future_cost_per_year * years_of_college
    amount_to_cover = total_future_cost * percent_to_cover

    months_until_college = years_until_college * 12
    monthly_rate_of_return = (1 + rate_of_return) ** (1/12) - 1

    if rate_of_return == 0:
        monthly_savings = amount_to_cover / months_until_college
    else:
        monthly_savings = ((amount_to_cover - already_saved * (1 + rate_of_return) ** years_until_college) / 
                         (((1 + monthly_rate_of_return) ** months_until_college - 1) / monthly_rate_of_return))

    cumulative_saved = [already_saved]
    cumulative_contributions = [already_saved]
    cumulative_earnings = [0]
    ages = [current_age]

    total_contributions = already_saved
    total_earnings = 0
    total_saved = total_contributions + total_earnings

    for month in range(1, int(months_until_college) + 1):
        period_earnings = total_saved * monthly_rate_of_return
        total_earnings += period_earnings
        total_saved += period_earnings + monthly_savings
        total_contributions += monthly_savings
        
        cumulative_contributions.append(total_contributions)
        cumulative_saved.append(total_saved)
        cumulative_earnings.append(total_earnings)
        ages.append(current_age + (month / 12))

    df = pd.DataFrame({
        'Age': ages,
        'Contributions': cumulative_contributions,
        'Earnings': cumulative_earnings,
    })

    fig = px.area(df, x='Age', y=['Contributions', 'Earnings'],
                 title=f"Projected College Savings: ${monthly_savings:,.0f} per month needed",
                 labels={'Age': 'Child Age', 'value': 'Amount ($)', 'variable': 'Category'})

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white',
        margin=dict(l=50, r=50, t=100, b=150),
        height=600
    )

    return {
        "monthly_savings": monthly_savings,
        "total_future_cost": total_future_cost,
        "future_cost_per_year": future_cost_per_year,
        "fig": fig
    }

st.title('College Savings Calculator')

with st.form("savings_calculator"):
    col1, col2 = st.columns(2)
    
    with col1:
        current_age = st.number_input('Current Age', value=5.0, step=0.1)
        college_start_age = st.number_input('College Start Age', value=18)
        annual_cost = st.number_input('Annual Cost ($)', value=35000)
        college_inflation_rate = st.number_input('College Inflation Rate (%)', value=4.0)
    
    with col2:
        years_of_college = st.number_input('Years of College', value=4)
        already_saved = st.number_input('Already Saved ($)', value=60000)
        rate_of_return = st.number_input('Expected Return Rate (%)', value=7.0)
        percent_to_cover = st.number_input('Percent to Cover (%)', value=75.0)

    submit = st.form_submit_button("Calculate")

if submit:
    inputs = {
        'current_age': current_age,
        'college_start_age': college_start_age,
        'annual_cost': annual_cost,
        'college_inflation_rate': college_inflation_rate,
        'years_of_college': years_of_college,
        'already_saved': already_saved,
        'rate_of_return': rate_of_return,
        'percent_to_cover': percent_to_cover
    }
    
    results = calculate_savings(inputs)
    if results:
        st.header('Results')
        st.metric('Monthly Savings Needed', f"${results['monthly_savings']:,.0f}")
        st.metric('Total Future Cost', f"${results['total_future_cost']:,.0f}")
        st.metric('Future Cost per Year', f"${results['future_cost_per_year']:,.0f}")
        st.plotly_chart(results['fig'], use_container_width=True)
