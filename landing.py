from dash import dcc, html

def render_landing():
    return html.Div([
        html.H2("Welcome to Optro!"),
        html.P("Optro is an open-source web-based tool for analyzing data collected from production processes. After "
               "uploading necessary data, you can use Optro's different features freely."),

        html.H2("Guidelines"),

        html.H3("A. Uploading Data"),
        html.H4("1. Task Data"),
        html.P("Lorem ipsum dolor si amet..."),
        html.H4("2. Layout Data"),
        html.P("Lorem ipsum dolor si amet..."),
        html.H3("B. Modelling"),
        html.P("Lorem ipsum dolor si amet..."),
        html.H4("1. Line Balancing Models"),
        html.P("Lorem ipsum dolor si amet..."),
        html.H4("2. Layout Planning Model"),
        html.P("Lorem ipsum dolor si amet..."),

    ])
