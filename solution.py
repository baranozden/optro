from dash import dcc, html
import dash_daq as daq
import models as md
import plotly.express as px


solution_report = False


def clear_report():
    global solution_report
    solution_report = False


def solve_models(val, df, lo):
    global solution_report
    sol1 = md.optimizer(val, "ct", df)
    sol2 = md.optimizedev(val, "ct", df)
    sta_numbers, worker_numbers, task_assignments, task_time, sta_time, max_times, sta_idleness, sta_utilize, \
    avg_utilize, sta_block, sta_starv, sta_bst = md.summarize_stations(sol1)
    tot_idle = sum(list(sta_idleness.values()))
    tot_blocked = sum(list(sta_block.values()))
    tot_starved = sum(list(sta_starv.values()))
    tot_bst = sum(list(sta_bst.values()))

    sta_numbers2, worker_numbers2, task_assignments2, task_time2, sta_time2, max_times2, sta_idleness2, sta_utilize2, \
    avg_utilize2, sta_block2, sta_starv2, sta_bst2 = md.summarize_stations(sol2)
    tot_idle2 = sum(list(sta_idleness2.values()))
    tot_blocked2 = sum(list(sta_block2.values()))
    tot_starved2 = sum(list(sta_starv2.values()))
    tot_bst2 = sum(list(sta_bst2.values()))

    task_list = [html.Div([html.H3(sta), html.Ul(children=[html.Li(task) for task in task_assignments[sta]])])
                 for sta in task_assignments.keys()]
    task_list2 = [html.Div([html.H3(sta), html.Ul(children=[html.Li(task) for task in task_assignments2[sta]])])
                  for sta in task_assignments2.keys()]
    st_plot = md.plot_sta_times(sta_time, val)
    si_plot = md.plot_idle_times(sta_idleness, val)
    su_plot = md.plot_sta_util(sta_utilize)
    sb_plot = md.plot_sta_blocking(sta_block, val)
    ss_plot = md.plot_sta_starving(sta_starv, val)
    sbs_plot = md.plot_sta_bstotal(sta_bst, val)
    st_plot2 = md.plot_sta_times(sta_time2, val)
    si_plot2 = md.plot_idle_times(sta_idleness2, val)
    su_plot2 = md.plot_sta_util(sta_utilize2)
    sb_plot2 = md.plot_sta_blocking(sta_block2, val)
    ss_plot2 = md.plot_sta_starving(sta_starv2, val)
    sbs_plot2 = md.plot_sta_bstotal(sta_bst2, val)

    wstasks = md.build_ws_task_dict(sol1)
    area_object_created = md.build_area(lo)
    sta_layout_dict = md.build_station_layout_items_dict(wstasks, df)
    item_objects_created = md.build_layout_objects(sta_layout_dict, lo)
    md.optimize_layout(area_object_created, item_objects_created, sta_layout_dict)
    image, item_names = md.render_layout(area_object_created, sta_layout_dict, item_objects_created, sol1)
    img = px.imshow(image)
    img.update_layout(width=800, height=600, margin=dict(l=10, r=10, b=10, t=10))
    img.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)

    item_ul_dict = {sta: {item: [html.Div([html.Ul([html.Li(task)], className="task-ul")])
                                 for task in item_names[sta]["items"][item]["item_task"]]
                          for item in item_names[sta]["items"].keys()} for sta in item_names.keys()}

    item_names_dict = {sta: [html.Div([html.Details([html.Summary(str(item_names[sta]["items"][item]["item_no"])+
                                                                  ": "+str(item), className="item-summ"),
                                                     html.Div(children=item_ul_dict[sta][item])])])
                             for item in item_names[sta]["items"].keys()]
                       for sta in item_names.keys()}

    item_names_list = [html.Div([html.Details([html.Summary("Station #"+str(list(item_names.keys()).index(sta)+1),
                                                            style={"background-color":
                                                                       "rgb"+str(item_names[sta]["color"])},
                                                            className="sta-summ"),
                                              html.Div(children=item_names_dict[sta])])])
                       for sta in item_names.keys()]

    wstasks2 = md.build_ws_task_dict(sol2)
    sta_layout_dict2 = md.build_station_layout_items_dict(wstasks2, df)
    item_objects_created2 = md.build_layout_objects(sta_layout_dict2, lo)
    md.optimize_layout(area_object_created, item_objects_created2, sta_layout_dict2)
    image2, item_names2 = md.render_layout(area_object_created, sta_layout_dict2, item_objects_created2, sol2)
    img2 = px.imshow(image2)
    img2.update_layout(width=800, height=600, margin=dict(l=10, r=10, b=0, t=0))
    img2.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)

    item_ul_dict2 = {sta: {item: [html.Div([html.Ul([html.Li(task)], className="task-ul")])
                                 for task in item_names2[sta]["items"][item]["item_task"]]
                          for item in item_names2[sta]["items"].keys()} for sta in item_names2.keys()}

    item_names_dict2 = {sta: [html.Div([html.Details([html.Summary(str(item_names2[sta]["items"][item]["item_no"]) +
                                                                  ": " + str(item), className="item-summ"),
                                                     html.Div(children=item_ul_dict2[sta][item])])])
                             for item in item_names2[sta]["items"].keys()]
                       for sta in item_names2.keys()}

    item_names_list2 = [html.Div([html.Details([html.Summary("Station #" + str(list(item_names2.keys()).index(sta)+1),
                                                            style={"background-color":
                                                                       "rgb" + str(item_names2[sta]["color"])},
                                                            className="sta-summ"),
                                               html.Div(children=item_names_dict2[sta])])])
                       for sta in item_names2.keys()]


    solution_report = html.Div([
        html.H2(["Model 1 KPIs"], className="ribbon-banner"),
        html.Div([
            html.Div([
                html.Div([html.H3("Cycle Time")]),
                html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        label=" ",
                        size=150,
                        units="Seconds",
                        value=int(max_times),
                        max=val,
                        min=0,
                        color="#ef432a"
                    )
                ], className="gauge")
            ], className="card"),

            html.Div([
                html.Div([html.H3("Number of Stations")]),
                html.Div([html.H1(sta_numbers)], className="num-ind")
            ], className="card"),

            html.Div([
                html.Div([html.H3("Number of Workers")]),
                html.Div([html.H1(worker_numbers)], className="num-ind")
            ], className="card"),

            html.Div([
                html.Div([html.H3("Average Utilization Rate")]),
                html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        label=" ",
                        size=150,
                        units="Percent",
                        value=avg_utilize*100,
                        max=100,
                        min=0,
                        color="#ef432a"
                    )
                ], className="gauge")
            ], className="card"),

        ], className="card-container"),
        html.H2(["Model 2 KPIs"], className="ribbon-banner"),
        html.Div([
            html.Div([
                html.Div([html.H3("Cycle Time")]),
                html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        label=" ",
                        size=150,
                        units="Seconds",
                        value=max_times2,
                        max=val,
                        min=0,
                        color="#ef432a"
                    )
                ], className="gauge")
            ], className="card"),

            html.Div([
                html.Div([html.H3("Number of Stations")]),
                html.Div([html.H1(sta_numbers2)], className="num-ind")
            ], className="card"),

            html.Div([
                html.Div([html.H3("Number of Workers")]),
                html.Div([html.H1(worker_numbers2)], className="num-ind")
            ], className="card"),

            html.Div([
                html.Div([html.H3("Average Utilization Rate")]),
                html.Div([
                    daq.Gauge(
                        showCurrentValue=True,
                        label=" ",
                        size=150,
                        units="Percent",
                        value=avg_utilize2 * 100,
                        max=100,
                        min=0,
                        color="#ef432a"
                    )
                ], className="gauge")
            ], className="card"),

        ], className="card-container"),

        html.Div([

            html.Div([
                html.H2("Model 1"),
                html.Div(children=task_list),
                dcc.Graph(figure=st_plot),
                dcc.Graph(figure=su_plot),
                dcc.Graph(figure=si_plot),
                html.Div([
                    html.Div([html.H3("Total Idle Time")]),
                    html.Div([html.H1(tot_idle)])
                ], className="dash-card"),
                dcc.Graph(figure=sb_plot),
                html.Div([
                    html.Div([html.H3("Total Blocking Time")]),
                    html.Div([html.H1(tot_blocked)])
                ], className="dash-card"),
                dcc.Graph(figure=ss_plot),
                html.Div([
                    html.Div([html.H3("Total Starving Time")]),
                    html.Div([html.H1(tot_starved)])
                ], className="dash-card"),
                dcc.Graph(figure=sbs_plot),
                html.Div([
                    html.Div([html.H3("Total Blocking+Starving Time")]),
                    html.Div([html.H1(tot_bst)])
                ], className="dash-card"),
            ], className="column"),


            html.Div([
                html.H2("Model 2"),
                html.Div(children=task_list2),
                dcc.Graph(figure=st_plot2),
                dcc.Graph(figure=su_plot2),
                dcc.Graph(figure=si_plot2),
                html.Div([
                    html.Div([html.H3("Total Idle Time")]),
                    html.Div([html.H1(tot_idle2)])
                ], className="dash-card"),
                dcc.Graph(figure=sb_plot2),
                html.Div([
                    html.Div([html.H3("Total Blocking Time")]),
                    html.Div([html.H1(tot_blocked2)])
                ], className="dash-card"),
                dcc.Graph(figure=ss_plot2),
                html.Div([
                    html.Div([html.H3("Total Starving Time")]),
                    html.Div([html.H1(tot_starved2)])
                ], className="dash-card"),
                dcc.Graph(figure=sbs_plot2),
                html.Div([
                    html.H3("Total Blocking+Starving Time"),
                    html.H1(tot_bst2)
                ], className="dash-card"),
            ], className="column"),

        ], className="column-container"),

        html.Div([
            html.Div([html.H2("Layout for Model 1")], className="row"),
            html.Div([dcc.Graph(figure=img)], className="lo-img-col"),
            html.Div(children=item_names_list),
        ], className="lo-container"),

        html.Div([
            html.Div([html.H2("Layout for Model 2")], className="row"),
            html.Div([dcc.Graph(figure=img2)], className="lo-img-col"),
            html.Div(children=item_names_list2),
        ], className="lo-container"),
    ], className="page-body")



def render_solution():
    return html.Div(id="model-control", children=[
        html.H3("Model Target", className="input-header"),
        dcc.Input(id="cycle-time",
                  type="number",
                  placeholder="Target Cycle Time"),
        html.Button("Solve!",
                    id="solve-button",
                    n_clicks=0),
        html.Button("Clear Solution",
                    id="clear-button",
                    n_clicks=0,
                    className="delete-button"),
        html.Div(id="button-message"),
        html.Div(id="solution-page")
    ])

