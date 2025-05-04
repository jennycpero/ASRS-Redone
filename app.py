from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from pymongo import MongoClient
from pandas import json_normalize
import requests
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import evaluate
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Grab data - start August 2001 and end at November 2024
client = MongoClient('mongodb+srv://jennycpero:UQHG2Sfufk73KHGX@cluster0.rudlgwh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['ASRSDB']
collection = db.asrsColl

cursor = collection.find({})
df = pd.json_normalize(list(cursor))

# Create app
app = Dash(__name__, suppress_callback_exceptions=True,  external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Query", href="/query", className="nav-link")),
        dbc.NavItem(dcc.Link("Statistics", href="/statistics", className="nav-link")),
        dbc.NavItem(dcc.Link("Analysis", href="/analysis", className="nav-link")),
    ],
    brand="ASRS Redone",
    brand_href="/",
    color="#1B91DA",
    brand_style={'font-size':'25px'},
    style={'background':'linear-gradient(to right,#1B91DA,#0E4D74)', 'font-weight':'bold','font-size':'20px','padding':'5px 20px'}
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', style={'padding': '20px'})
])

# Define the page content callback
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def update_page(pathname):
    if pathname == "/query":
        return html.Div([
            html.H2("Query"),
            html.H3("Use our AI tool to query the ASRS database"),
            html.Label("Input Text"),
            dcc.Textarea(id='input-text', style={'width': '100%', 'height': 100}),
            html.Label("Expected Output (optional)"),
            dcc.Textarea(id='expected-text', style={'width': '100%', 'height': 60}),
            html.Br(),
            html.Button("Generate & Evaluate", id='generate-button', n_clicks=0),
            html.Br(),
            html.Div(id='output-text', style={'whiteSpace': 'pre-wrap'}),
        ])
    elif pathname == "/statistics":
        # Incident Type Bar Chart
        df_grouped = df.groupby("Assessments.Primary Problem").size().reset_index(name="count")
        fig_problem = px.bar(df_grouped, x='Assessments.Primary Problem', y='count', title="Reports By Primary Problem")

        # Incidents By Location
        states_count=df.groupby("Place.State Reference").size().reset_index(name="count")
        geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
        response = requests.get(geojson_url)
        geojson_states = response.json()

        fig_states = px.choropleth(states_count,
                    locations='Place.State Reference',  # Column with state abbreviations
                    locationmode='USA-states',  # This works with both names and abbreviations
                    color='count',
                    scope='usa',
                    color_continuous_scale='Burg',
                    title='Reports by US States')

        # Time Line Chart
        df["Time / Day.Date"] = df["Time / Day.Date"].dt.normalize()  # Remove time component
        df_grouped = df.groupby("Time / Day.Date").size().reset_index(name="count")
        fig_time = px.line(df_grouped, x='Time / Day.Date', y='count', title="Reports Over Time")
        return html.Div([
            html.H1("Statistics"),
            html.H3("Total Reports: " + str(df.shape[0])),
            dcc.Graph(figure=fig_time),
            dcc.Graph(figure=fig_problem),
            dcc.Graph(figure=fig_states)
        ])
    elif pathname == "/analysis":
        return html.H2("Abbreviations and Acronyms")
    return html.H2("Welcome to the App!")

if __name__ == '__main__':
    app.run(debug=True)


