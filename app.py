import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

import io
import base64
import sys

import landing
import data_page
import solution
import models as md

DATA = pd.DataFrame()
LAYOUT_DATA = pd.DataFrame()
assetpath = sys.path[0] + "\\assets"

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div([
    html.Div(children=[
        html.H1("OPTRO", className="banner-heading"),
    ], className="banner row"),
    html.Div([
        dcc.Tabs(id="navbar",
                 value="navbar",
                 children=[
                     dcc.Tab(label="Landing", value="landing", className="nav-tab", selected_className="tab-sel"),
                     dcc.Tab(label="Data", value="data", className="nav-tab", selected_className="tab-sel"),
                     dcc.Tab(label="Modelling", value="modelling", className="nav-tab", selected_className="tab-sel"),
                 ])
    ],className="navbar-container"),
    html.Div(id="body"),

])


@app.callback(Output("body", "children"),
              Input("navbar", "value"))
def render_page_body(tab):
    if tab == "landing":
        return landing.render_landing()
    if tab == "data":
        return data_page.render_data()
    if tab == "modelling":
        return solution.render_solution()


@app.callback(Output("upload-task-data-message", "children"),
              Input("task-data-upload", "contents"))
def upload_task_data(contents):
    global DATA
    if contents is not None:
        content_type, content_str = contents.split(",")
        decoded = base64.b64decode(content_str)
        temp = pd.read_excel(io.BytesIO(decoded))
        DATA = md.create_dataframe(data=temp)
        print(DATA)
        return html.Div([
            html.P("Task data uploaded successfully. Please upload layout data."),
        ], style={"color": "green"})


@app.callback(Output("upload-layout-data-message", "children"),
              Input("layout-data-upload", "contents"))
def upload_task_data(contents):
    global LAYOUT_DATA
    if contents is not None:
        content_type, content_str = contents.split(",")
        decoded = base64.b64decode(content_str)
        temp = pd.read_excel(io.BytesIO(decoded))
        LAYOUT_DATA = md.create_layout_df(data=temp)
        return html.Div([
            html.P("Layout data uploaded successfully. You can go to Modelling!"),
        ], style={"color": "green"})


# @app.callback(Output("upload-default-data-message", "children"),
#               Input("default-data-upload", "n_clicks"))
# def use_default_data(n_clicks):
#     global DATA, LAYOUT_DATA
#     if n_clicks > 0:
#         DATA = md.create_dataframe("C:/Users/baran/OneDrive/Masaüstü/temsa/temsa_tasks.xlsx")
#         LAYOUT_DATA = md.create_layout_df("C:/Users/baran/OneDrive/Masaüstü/temsa/layout.xlsx")
#         return html.Div([
#             html.P("Default data loaded successfully. You can go to Dashboards or Modelling pages!"),
#         ], style={"color":"green"})


@app.callback(Output("button-message", "children"),
              Input("solve-button", "n_clicks"),
              State("cycle-time", "value"))
def prompt_solution(n_clicks, val):
    global DATA
    global LAYOUT_DATA
    if n_clicks > 0:
        return solution.solve_models(val, DATA, LAYOUT_DATA)


if __name__ == '__main__':
    app.run_server(debug=True)
