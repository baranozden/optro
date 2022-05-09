import base64

from dash import dcc, html

def render_data():
    return html.Div([
        html.H3("Upload Task Data"),
        html.P("For more information check the Guidelines given in the Landing page."),
        dcc.Upload(id="task-data-upload",
                   children=html.Button("Search")),
        html.Div(id="upload-task-data-message"),

        html.H3("Upload Layout Data"),
        html.P("For more information check the Guidelines given in the Landing page."),
        dcc.Upload(id="layout-data-upload",
                   children=html.Button("Search")),
        html.Div(id="upload-layout-data-message"),

    #     html.P("Or simply continue with the default data"),
    #     html.Button("Yes, please",
    #                 id="default-data-upload",
    #                 n_clicks=0),
    #     html.Div(id="upload-default-data-message"),
    ])


