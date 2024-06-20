import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Load environment variables
load_dotenv(dotenv_path='/Users/berkayakisik/Desktop/dashboard_cb/dashboard_cb/token.env')

# Retrieve environment variables
weather_api = os.getenv('weatherapi')
username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
db_climate = os.getenv('DB_CLIMATE')

# Create the database engine
engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db_climate}')

# Query to select data from your table
query = "SELECT * FROM mart_forecast_day"

# Load data into DataFrame
df = pd.read_sql(query, engine)

# Initialize the Dash app with the 'Vapor' theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])

server = app.server

app.config.suppress_callback_exceptions = True

# List of unique cities for the dropdown
cities = df['city'].unique()

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Weather Forecast Dashboard", className='text-center text-primary mb-4'), width=12)
    ]),
    
    dbc.Row([
        dbc.Col(dbc.Label("Select City"), width=2),
        dbc.Col(dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in cities],
            value='Istanbul',
            clearable=False,
            style={'color': '#000'}
        ), width=10)
    ], className='mb-4'),
    
    dbc.Row([
        dbc.Col(dbc.Label("Select Temperature Metrics"), width=2),
        dbc.Col(dcc.Checklist(
            id='temp-checklist',
            options=[
                {'label': 'Min Temperature', 'value': 'min_temp_c'},
                {'label': 'Max Temperature', 'value': 'max_temp_c'},
                {'label': 'Avg Temperature', 'value': 'avg_temp_c'}
            ],
            value=['min_temp_c', 'max_temp_c', 'avg_temp_c'],
            inline=True,
            style={'color': '#fff'}
        ), width=10)
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='temperature-plot'), width=12)
    ], className='mb-4'),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='wind-speed-plot'), width=6),
        dbc.Col(dcc.Graph(id='uv-index-plot'), width=6)
    ], className='mb-4'),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='humidity-plot'), width=6),
        dbc.Col(dcc.Graph(id='precipitation-plot'), width=6)
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(html.Div(id='summary-card'), width=12)
    ], className='mb-4')
], fluid=True)

@app.callback(
    Output('temperature-plot', 'figure'),
    [Input('city-dropdown', 'value'),
     Input('temp-checklist', 'value')]
)
def update_temperature_plot(selected_city, selected_metrics):
    df_city = df[df['city'] == selected_city]
    fig = px.line(df_city, x='date', y=selected_metrics, title=f'Temperature Over Time in {selected_city}')
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('wind-speed-plot', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_wind_speed_plot(selected_city):
    df_city = df[df['city'] == selected_city]
    fig = px.line(df_city, x='date', y='max_wind_kph', title=f'Wind Speed Over Time in {selected_city}')
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('uv-index-plot', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_uv_index_plot(selected_city):
    df_city = df[df['city'] == selected_city]
    fig = px.line(df_city, x='date', y='uv', title=f'UV Index Over Time in {selected_city}')
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('humidity-plot', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_humidity_plot(selected_city):
    df_city = df[df['city'] == selected_city]
    fig = px.line(df_city, x='date', y='avg_humidity', title=f'Humidity Over Time in {selected_city}')
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('precipitation-plot', 'figure'),
    [Input('city-dropdown', 'value')]
)
def update_precipitation_plot(selected_city):
    df_city = df[df['city'] == selected_city]
    fig = px.bar(df_city, x='date', y='total_precip_mm', title=f'Precipitation Over Time in {selected_city}')
    fig.update_layout(title_x=0.5)
    return fig

@app.callback(
    Output('summary-card', 'children'),
    [Input('city-dropdown', 'value')]
)
def update_summary_card(selected_city):
    df_city = df[df['city'] == selected_city]
    avg_temp = df_city['avg_temp_c'].mean()
    max_temp = df_city['max_temp_c'].max()
    min_temp = df_city['min_temp_c'].min()
    total_precip = df_city['total_precip_mm'].sum()
    
    card_content = [
        dbc.CardHeader("Summary", className='text-center'),
        dbc.CardBody([
            html.H5(f"Average Temperature: {avg_temp:.2f} °C", className='card-title'),
            html.P(f"Maximum Temperature: {max_temp:.2f} °C", className='card-text'),
            html.P(f"Minimum Temperature: {min_temp:.2f} °C", className='card-text'),
            html.P(f"Total Precipitation: {total_precip:.2f} mm", className='card-text')
        ])
    ]
    
    return dbc.Card(card_content, className='text-center')

if __name__ == '__main__':
    app.run_server(debug=True)