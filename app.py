import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import requests
import pandas as pd
import dash_core_components as dcc
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output
import dash_table

from callbacks import *

app = dash.Dash(external_stylesheets = [ dbc.themes.FLATLY],)

body_app = dbc.Container([
    html.H1('Compare Tax Scheme'),
    html.Div('* This app is for approximation only, the author holds no responsibility whatsoever over its contents.'),
    dbc.Row([
      dbc.Col([
        html.H2('Definitions'),
        html.Button('Compute', id='do-compute', n_clicks=0),
        dcc.Textarea(
            id='text-func-0',
            value='"US Federal", lambda income: tax_us_federal(income, FED_SINGLE_INCOME_BRACKETS, 7.65)',
            style={'width': '100%', 'height': 100},
            readOnly=True
        ),
        dcc.Textarea(
            id='text-func-1',
            value='"10k", lambda income: (10_000, 10_000 / income if income >= 100 else 0)',
            style={'width': '100%', 'height': 100},
        ),
        dcc.Textarea(
            id='text-func-2',
            value='"flat 30%", lambda income: tax_flat(income, 30)',
            style={'width': '100%', 'height': 100},
        ),
        dcc.Textarea(
            id='text-func-3',
            value='"flat 40% UBI 10K", lambda income: tax_flat_discount(income, 40, 10_000)',
            style={'width': '100%', 'height': 100},
        ),
        dcc.Textarea(
            id='text-func-4',
            value=f'"flat+UBI+consumption approximation", lambda income: consumption_tax_ubi(income, 7_500, housing_rate=0, food_rate=0.025, disc_rate=0.4, luxury_rate=1.0)',
            style={'width': '100%', 'height': 100},
        ),
      ], width=4),
      dbc.Col([
        html.Div(style={"border-left": "1px solid", "height": "500px"}),
      ], width=1),
      dbc.Col([
        html.H2('Outcomes'),
        html.Div(id='out-income'),
        html.Div(id='out-tax-rate'),
        html.Div(id='out-tax-amount'),
        html.Div(id='out-tax-collected'),
        html.Div(id='out-voter-support'),
      ], width=7)
    ])
])

    # # dbc.Row( html.Marquee("USA, India and Brazil are top 3 countries in terms of confirmed cases"), style = {'color':'green'}),

    # dash_table.DataTable(pd.DataFrame(FED_SINGLE_INCOME_BRACKETS).to_dict('records')),

    # dbc.Row([
    #     html.H1(
    #         children="ML Dashboard",
    #         className="main_title",
    #         style={
    #             "color": "black",
    #             "text-align": "center"
    #         },
    #     ),
    #     ]),
    # html.Div([dcc.Input(id='input'), html.Div(id='output')])

    # ],fluid = True)

app.layout = html.Div(id = 'parent', children = [body_app])

if __name__ == "__main__":
    app.run_server(debug=False)