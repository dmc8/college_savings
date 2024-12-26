import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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
    if not (0 <= percent_to_cover <= 100):
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
        'Total Savings': cumulative_contributions + cumulative_earnings  # Calculate total savings here
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Age'], y=df['Contributions'], fill='tozeroy', name='Contributions', stackgroup='one'))
    fig.add_trace(go.Scatter(x=df['Age'], y=df['Earnings'], fill='tonexty', name='Earnings', stackgroup='one'))

    fig.update_layout(
        title=f"Projected College Savings: ${monthly_savings:,.0f} per month needed",
        xaxis_title="Child Age",
        yaxis_title="Amount ($)",
        template='plotly_white',
        margin=dict(l=50, r=50, t=100, b=150),
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            title="",
            x=1
        )
    )

    max_savings = df['Total Savings'].max()
    max_savings_age = df.loc[df['Total Savings'].idxmax(), 'Age']

    if max_savings >= 1000:
        max_savings_text = f"Total Savings: ${max_savings/1000:,.0f}k"
    else:
        max_savings_text = f"Total Savings: ${max_savings:,.0f}"

    fig.add_annotation(
        x=max_savings_age,
        y=max_savings,
        text=max_savings_text,
        showarrow=True,
        arrowhead=7,
        ax=0,
        ay=-40,
        font=dict(color="red"),
    )

    annual_cost_formatted = f"${annual_cost:,.0f}"
    already_saved_formatted = f"${already_saved:,.0f}"
    total_future_cost_formatted = f"${total_future_cost:,.0f}"
    future_cost_per_year_formatted = f"${future_cost_per_year:,.0f}"
    monthly_savings_formatted = f"${monthly_savings:,.0f}"

    return {
        "monthly_savings": monthly_savings_formatted, #returns formatted value
        "total_future_cost": total_future_cost_formatted, #returns formatted value
        "future_cost_per_year": future_cost_per_year_formatted, #returns formatted value
        "fig": fig,
        "annual_cost_formatted": annual_cost_formatted,
        "already_saved_formatted": already_saved_formatted
    }

st.title('College Savings Calculator')

with st.form("savings_calculator"):
    col1, col2 = st.columns(2)

    with col1:
        current_age = st.number_input('Current Age', value=5.0, step=0.1)
        college_start_age = st.number_input('College Start Age', value=18)

        # Use text input with formatting for display, but store the numeric value
        annual_cost_display = st.text_input('Annual Cost ($)', value="$35,000")
        try:
          annual_cost = int(annual_cost_display.replace("$", "").replace(",", ""))
        except ValueError:
          st.error("Please enter a valid number for Annual Cost")
          st.stop()
        college_inflation_rate = st.number_input('College Inflation Rate (%)', value=4.0)

    with col2:
        years_of_college = st.number_input('Years of College', value=4)
        
        already_saved_display = st.text_input('Already Saved ($)', value="$60,000")
        try:
          already_saved = int(already_saved_display.replace("$", "").replace(",", ""))
        except ValueError:
          st.error("Please enter a valid number for Already Saved")
          st.stop()

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
        st.metric('Monthly Savings Needed', results['monthly_savings']) #uses formatted value
        st.metric('Total Future Cost', results['total_future_cost']) #uses formatted value
        st.metric('Future Cost per Year', results['future_cost_per_year']) #uses formatted value
        st.metric('Annual College Cost (Today\'s Dollars)', results['annual_cost_formatted'])
        st.metric('Already Saved', results['already_saved_formatted'])
        st.plotly_chart(results['fig'], use_container_width=True)