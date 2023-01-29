from dash import Input, Output, html, dcc, State
import dash
import plotly.graph_objects as go

import numpy as np
import pandas as pd

percentile = pd.read_csv("income_percentile.txt", delimiter=r"\s+")

FED_SINGLE_INCOME_BRACKETS = [
    (10275, 10),
    (41775, 12),
    (89075, 22),
    (170050, 24),
    (215950, 32),
    (539900, 35),
    (1e20, 37),
]

FED_SINGLE_INCOME_RAISED_BRACKETS = [
    (10275, 10),
    (41775, 12),
    (89075, 22),
    (170050, 24),
    (215950, 32),
    (400000, 37),
    (539900, 40),
    (1e20, 42),
]

def tax_flat(income, rate):
    return income * rate / 100.0, rate / 100

def tax_flat_discount(income, rate, discount):
    if income < 100:
        return - discount, -discount
    tax = income * rate / 100.0 - discount
    return tax, tax / income

def tax_progressive_bracket(income, brackets):
    tax = 0
    for i, (bracket_max, rate) in enumerate(brackets):
        prev_max = brackets[i - 1][0] if i > 0 else 0
        tax += (min(income, bracket_max) - prev_max) * rate / 100.0
        if income <= bracket_max:
            break
    return tax, tax / income
 

def tax_us_federal(income, brackets, medicare_rate):
    if income < 100:
        return 0, 0
    income_tax = tax_progressive_bracket(income, brackets)[0]
    medicare_tax = tax_flat(income, medicare_rate)[0]
    tax = income_tax + medicare_tax
   
    return tax, tax / income

def consumption_tax(income, housing_rate, food_rate, disc_rate, luxury_rate):
    housing = min(max(600 * 12, income * 0.3), 7_500 * 12)
    housing = housing * (1 + housing_rate)
    tax = 0
    food = min(max(20 * 360, income * 0.15), 100 * 360)
    food = food * (1 + food_rate)
    food = min(food, income - tax - housing)
    saving1 = income * 0.05
    saving1 = min(saving1, income - tax - housing - food)
    disc = min(max(25 * 360, income * 0.3), 3000 * 12)
    disc = disc * (1 + disc_rate)
    disc = min(disc, income - tax - housing - food - saving1)
    saving2 = min(income * 0.15, 25_000)
    saving2 = min(saving2, income - tax - housing - food - saving1 - disc)
    luxury = max(income * 0.05, 7500 * 12)
    luxury = luxury * (1 + luxury_rate)
    luxury = min(luxury, income - tax - housing - food - saving1 - disc - saving2)
    saving3 = income - tax - housing - food - disc - saving1 - luxury - saving2

    tax = food * food_rate + housing * housing_rate + disc * disc_rate + luxury * luxury_rate
    return tax, tax / income, dict(income=income, tax=tax, housing=housing, food=food, disc=disc, saving=saving1+saving2+saving3, luxury=luxury)

def consumption_tax_ubi(income, ubi, housing_rate, food_rate, disc_rate, luxury_rate):
    if income < 100:
        return -ubi, -ubi
    tax, _, details = consumption_tax(income + ubi, housing_rate, food_rate, disc_rate, luxury_rate)
    tax = tax - ubi
    return tax, tax / income

@dash.callback(
    [
        Output('out-income', 'children'),
        Output('out-tax-rate', 'children'),
        Output('out-tax-amount', 'children'),
        Output('out-tax-collected', 'children'),
        Output('out-voter-support', 'children'),
    ],
    [
        Input('do-compute', 'n_clicks'),
    ],
    [
        State('text-func-0', 'value'),
        State('text-func-1', 'value'),
        State('text-func-2', 'value'),
        State('text-func-3', 'value'),
        State('text-func-4', 'value'),
    ]
    )
def update(n_clicks, tax_func0, tax_func1, tax_func2, tax_func3, tax_func4):
    l_income = np.arange(10000, 1e6, 2500)

    l_func = [tax_func0, tax_func1, tax_func2, tax_func3, tax_func4]
    l_func = [l for l in l_func if l.lower() != 'none' and len(l) > 10]
    print(l_func)

    fig_tax_abs = go.Figure()
    fig_tax_rate = go.Figure()
    fig_tax_collect = go.Figure()
    fig_income = go.Figure()
    fig_bar = go.Figure()

    num_returns = 170_000_000
    
    # Baseline
    l_baseline_tax = list()
    tfunc = eval(l_func[0])[1]
    print(tfunc)
    for i, row in percentile.iterrows():
        income = int(row['2022'].replace('$', '').replace(',', ''))
        tax, rate = tfunc(income)
        l_baseline_tax.append(tax)

    l_yes = list()
    l_no = list()
    l_national_rate = list()
    l_name = list()
    for j, f in enumerate(l_func):
        name, tfunc = eval(f)
        l_name.append(name)
        l_tax_abs = list()
        l_tax_rate = list()
        for income in l_income:
            tax, rate = tfunc(income)
            l_tax_abs.append(tax)
            l_tax_rate.append(rate)

        l_collected = list()
        l_people = list()
        pincome = list()
        prevp = 0
        vote_yes = 0
        vote_no = 0
        total_income = 0
        for i, row in percentile.iterrows():
            income = int(row['2022'].replace('$', '').replace(',', ''))
            pp = float(row['Income_Percentile'].replace('%', ''))
            per_tile = (pp - prevp) / 100 * num_returns
            prevp = pp
            pincome.append(income)
            tax, rate = tfunc(income)
            l_collected.append(tax * per_tile)
            total_income += income * per_tile
            l_people.append(pp)
            
            if tax <= l_baseline_tax[i]:
                vote_yes += per_tile
            else:
                vote_no += per_tile
        l_yes.append(vote_yes)
        l_no.append(vote_no)
        l_national_rate.append(sum(l_collected) / total_income)
        
        fig_tax_abs.add_trace(go.Scatter(x=l_income, y=l_tax_abs, name=name))
        fig_tax_rate.add_trace(go.Scatter(x=l_income, y=l_tax_rate, name=name))
        fig_tax_collect.add_trace(go.Scatter(x=pincome, y=np.array(l_collected).cumsum(), name=name))
        if j == 0:
            fig_income.add_trace(go.Scatter(x=np.array(l_people), y=pincome, name=name))
    
    fig_income.update_yaxes(type="log")
    fig_income.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=200,
        hovermode="x",
        title='Income Distribution'
    )

    fig_tax_abs.update_xaxes(type="log")
    fig_tax_abs.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        hovermode="x",
        title='Absolute Tax$'
    )

    fig_tax_rate.update_xaxes(type="log")
    fig_tax_rate.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        hovermode="x",
        title='Tax Rate'
    )

    fig_tax_collect.update_xaxes(type="log")
    fig_tax_collect.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        hovermode="x",
        title='Cumulative Tax Collected'
    )
    
    fig_bar.add_trace(go.Bar(x=l_name, y=np.array(l_yes) / num_returns* 100, name='Yes %'))
    fig_bar.add_trace(go.Bar(x=l_name, y=np.array(l_no) / num_returns* 100, name='No %'))
    fig_bar.add_trace(go.Bar(x=l_name, y=np.array(l_national_rate) * 100, name='Average Rate'))

    return [
        dcc.Graph(figure=fig_income),
        dcc.Graph(figure=fig_tax_abs),
        dcc.Graph(figure=fig_tax_rate),
        dcc.Graph(figure=fig_tax_collect),
        dcc.Graph(figure=fig_bar),]