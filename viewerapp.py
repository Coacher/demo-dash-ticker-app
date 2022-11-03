import requests
import pandas as pd
import plotly.express as px

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


# Application
API = 'http://localhost:8000'
app = Dash(
    name='Trade Viewer',
    suppress_callback_exceptions=True,
    update_title=None
)


# Helpers
def api_req(path, key=None):
    json = requests.get(API + path).json()
    if key is not None:
        return json[key]
    return json


# Layout
header = html.H1('Trade ticker viewer with live updates')

selector = html.Div([
    html.H2('Please select a ticker to monitor:'),
    dcc.Dropdown(id='ticker_selector')
])

graph = html.Div(id='graph_placeholder')

app.layout = html.Div([
    header,
    selector,
    graph,
    dcc.Store(id='ticker_tick'),
    dcc.Store(id='ticker_index'),
    dcc.Interval(id='timer'),
])


# Callbacks
@app.callback(
    Output('ticker_selector', 'options'),
    Input('ticker_selector', 'value'),
)
def update_dropdown(_):
    return api_req('/tickers/names', 'tickers_names')


@app.callback(
    Output('ticker_index', 'data'),
    Output('graph_placeholder', 'children'),
    Input('ticker_selector', 'value'),
)
def display_graph(value):
    if value is None:
        return None, None

    index = api_req(f'/tickers/names/{value}', 'index')

    history = api_req(f'/tickers/{index}/history', 'history')
    history = pd.DataFrame(history, columns=['Tick', 'Price'])

    return index, dcc.Graph(id='ticker_graph', animate=True,
                            figure=px.line(history, x='Tick', y='Price'))


@app.callback(
    Output('ticker_tick', 'data'),
    Output('ticker_graph', 'extendData'),
    inputs=dict(
        cur=Input('ticker_tick', 'data'),
        idx=Input('ticker_index', 'data'),
        _=Input('timer', 'n_intervals'),
    ),
    prevent_initial_call=True,
)
def update_graph(cur, idx, _):
    if idx is None:
        raise PreventUpdate

    tick, price = api_req(f'/tickers/{idx}/point', 'point')

    if tick == cur:
        raise PreventUpdate

    return tick, [dict(x=[[tick]], y=[[price]])]


if __name__ == '__main__':
    app.run_server()
