import pandas as pd
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State

import io
import base64
import sys
import time
import threading

import landing
import data_page
import solution
import models as md

DATA = pd.DataFrame()
LAYOUT_DATA = pd.DataFrame()
counter = 0
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
    ], className="navbar-container"),
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


@app.callback(Output("button-message", "children"),
              Input("solve-button", "n_clicks"),
              State("cycle-time", "value"))
def prompt_solution(n_clicks, val):
    global DATA
    global LAYOUT_DATA

    if n_clicks == 1:
        t1 = threading.Thread(target=solution.solve_models, args=(val, DATA, LAYOUT_DATA))
        t1.start()
        return html.Div(id="interval-container",
                        children=[html.Div(id="interval-container2",
                                           children=[dcc.Interval(id='interval-component',
                                                                  interval=1000,
                                                                  disabled=False)]),
                                  html.Div(id="calculation-message")])


@app.callback(Output('calculation-message', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_calculation_message(n):
    if solution.solution_report:
        return solution.solution_report
    elif n:
        if n % 3 == 1:
            return html.P("Calculating..")
        elif n % 3 == 2:
            return html.P("Calculating...")
        else:
            return html.P("Calculating.")


@app.callback(Output('interval-component', 'interval'),
              [Input('interval-component', 'disabled')])
def stop_interval(n):
    print("####### didnt stop interval")
    while True:
        time.sleep(5)
        if solution.solution_report:
            time.sleep(3)
            print("####### stop interval")
            return 9999999999


@app.callback(Output("navbar", "value"),
              Input('clear-button', 'n_clicks'))
def delete_solution(n):
    if n > 0:
        solution.clear_report()
        return "modelling"


if __name__ == '__main__':
    app.run_server(debug=True)
