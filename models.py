import pandas as pd
import numpy as np
import random
from pulp import *
from PIL import Image, ImageDraw
import plotly.express as px


def create_dataframe(path=None, data=None):
    if path:
        df = pd.read_excel(rf"{path}")
    else:
        df = data.copy()

    df.drop(['stds', 'mins', 'maxs'], inplace=True, axis=1)
    df.task_id = df.task_id.astype(str)
    df.precedence = df.precedence.astype(str)
    for i in range(len(df)):

        if " " in df.precedence[i]:
            df.precedence[i] = df.precedence[i].split(", ")
        else:
            df.precedence[i] = df.precedence[i].split(",")
    return df


def create_layout_df(path=None, data=None):
    if path:
        lo = pd.read_excel(rf"{path}")
    else:
        lo = data.copy()

    return lo


def optimizer(target, typ, df):
    # SETS & PARAMS
    if typ == "demand":
        ct = 450 * 5 * 60 / target
    else:
        ct = target

    max_no_stas = int(df.sums.sum()/ct)+4
    tasks = [task for task in df.task_id]
    task_dict = {df.task_id[i]: df.task_name[i] for i in range(len(df))}
    task_time = {df.task_id[i]: df.sums[i] for i in range(len(df))}
    precedence = {
        df.task_id[i]: {df.task_id[j]: 1 if str(df.task_id[j]) in df.precedence[i] else 0 for j in range(len(df))} for i
        in range(len(df))}
    stations = ["sta{}".format(i + 1) for i in range(max_no_stas)]

    # PROBLEM ENVIRONMENT
    model = LpProblem("TaskAssignments", LpMinimize)

    # DECISION VARIABLES
    ws_open = LpVariable.dicts("OpenWS", stations, 0, 1, LpBinary)
    task_ws = LpVariable.dicts("TaskWSAssignments", [(j, k) for j in tasks for k in stations], 0, 1, LpBinary)

    # OBJECTIVE FUNCTION
    model += lpSum(ws_open[k] for k in ws_open)
    # model += lpSum(ct - task_ws[(j,k)]*task_time[j] for j in tasks for k in stations)

    # CONSTRAINTS

    # 1 Each task assigned a single ws
    for j in tasks:
        model += lpSum(task_ws[(j, k)] for k in stations) == 1

    # 2 If it has tasks, WS is open
    for k in stations:
        model += lpSum(task_ws[(j, k)] for j in tasks) <= 100000 * ws_open[k]

    # 3 Station times are bounded with cycle time
    for k in stations:
        model += lpSum(task_ws[(j, k)] * task_time[j] for j in tasks) <= ct

    # 4 Predecessors have to be assigned before
    for j in tasks:
        for k in stations:
            for l in tasks:
                model += precedence[j][l] * task_ws[(j, k)] <= lpSum(
                    task_ws[(l, m)] for m in stations[:stations.index(k) + 1] if j != l)

    # SOLVE MODEL
    model.solve()

    tl = []
    sl = []
    ttl = []
    for k in stations:
        for j in tasks:
            if task_ws[(j, k)].varValue > 0:
                tl.append(j)
                sl.append(k)
                ttl.append(task_time[j])

    assignments = pd.DataFrame({'task_id': tl, 'sta': sl, 'task_time': ttl, 'no_worker': np.nan, 'place': np.nan})
    for i in range(len(assignments)):
        assignments.task_id[i] = task_dict[assignments.task_id[i]]
        assignments.no_worker[i] = df[df.task_name == assignments.task_id[i]].no_workers
        assignments.place[i] = df[df.task_name == assignments.task_id[i]].place.values[0]

    return assignments


def optimizedev(target, typ, df):
    # SETS & PARAMS
    if typ == "demand":
        ct = 450 * 5 * 60 / target
    else:
        ct = target

    tasks = [task for task in df.task_id]
    task_dict = {df.task_id[i]: df.task_name[i] for i in range(len(df))}
    task_time = {df.task_id[i]: df.sums[i] for i in range(len(df))}
    precedence = {
        df.task_id[i]: {df.task_id[j]: 1 if str(df.task_id[j]) in df.precedence[i] else 0 for j in range(len(df))} for i
        in range(len(df))}
    stations = ["sta{}".format(i) for i in range(10)]

    # PROBLEM ENVIRONMENT
    model = LpProblem("TaskAssignments", LpMinimize)

    # DECISION VARIABLES
    ws_open = LpVariable.dicts("OpenWS", stations, 0, 1, LpBinary)
    task_ws = LpVariable.dicts("TaskWSAssignments", [(j, k) for j in tasks for k in stations], 0, 1, LpBinary)

    # OBJECTIVE FUNCTION
    # model += lpSum(ws_open[k] for k in ws_open)

    model += lpSum(ct * ws_open[k] - lpSum(task_ws[(j, k)] * task_time[j] for j in tasks) for k in stations)

    # CONSTRAINTS

    # 1 Each task assigned a single ws
    for j in tasks:
        model += lpSum(task_ws[(j, k)] for k in stations) == 1

    # 2 If it has tasks, WS is open
    for k in stations:
        model += lpSum(task_ws[(j, k)] for j in tasks) <= 100 * ws_open[k]

    # 3 Station times are bounded with cycle time
    for k in stations:
        model += lpSum(task_ws[(j, k)] * task_time[j] for j in tasks) <= ct

    # 4 Predecessors have to be assigned before
    for j in tasks:

        for k in stations:

            for l in tasks:
                model += precedence[j][l] * task_ws[(j, k)] <= lpSum(
                    task_ws[(l, m)] for m in stations[:stations.index(k) + 1] if j != l)

    # SOLVE MODEL
    model.solve()

    tl = []
    sl = []
    ttl = []
    for k in stations:
        for j in tasks:
            if task_ws[(j, k)].varValue > 0:
                tl.append(j)
                sl.append(k)
                ttl.append(task_time[j])

    assignments = pd.DataFrame({'task_id': tl, 'sta': sl, 'task_time': ttl, 'no_worker': np.nan, 'place': np.nan})
    for i in range(len(assignments)):
        assignments.task_id[i] = task_dict[assignments.task_id[i]]
        assignments.no_worker[i] = df[df.task_name == assignments.task_id[i]].no_workers
        assignments.place[i] = df[df.task_name == assignments.task_id[i]].place.values[0]

    return assignments


def build_ws_task_dict(assignments):
    stations = assignments.sta.unique()
    ws_task_dict = {}
    for station in stations:
        filtered = assignments[assignments.sta == station].copy()
        ws_task_dict[station] = list(filtered.task_id.unique())
    return ws_task_dict


def build_station_layout_items_dict(ws_task_dict, data):
    sta_item_dict = {}
    for sta in ws_task_dict.keys():
        sta_task_list = ws_task_dict[sta]
        item_set = []
        for task in sta_task_list:
            item_set.append(data.loc[(data.task_name == task)].place.values[0])
        sta_item_dict[sta] = list(set(item_set))
    sta_list = list(sta_item_dict.keys())
    last = sta_list[-1]
    sta_item_dict[last] = sta_item_dict[last] + ["test"]
    return sta_item_dict


class LayoutItem(object):
    def __init__(self, name, ws, x, y, cx=None, cy=None):
        self.name = name
        self.ws = ws
        self.x = x
        self.y = y
        self.cx = cx
        self.cy = cy
        self.up_y = None
        self.down_y = None
        self.right_x = None
        self.left_x = None

    def build_limits(self, rotate=0):
        if rotate:
            up_y, down_y = self.cy + self.x / 2, self.cy - self.x / 2
            right_x, left_x = self.cx + self.y / 2, self.cx - self.y / 2

        else:
            up_y, down_y = self.cy + self.y / 2, self.cy - self.y / 2
            right_x, left_x = self.cx + self.x / 2, self.cx - self.x / 2

        self.up_y = up_y
        self.down_y = down_y
        self.right_x = right_x
        self.left_x = left_x

    def update_centeroids(self, new_cx, new_cy, rotate=0):
        self.cx = new_cx
        self.cy = new_cy
        self.build_limits(rotate)

    def display(self):
        print(f"Name: {self.name}")
        print(f"Workstation: {self.ws}")
        print(f"Length 1: {self.x}")
        print(f"Length 2: {self.y}")
        print(f"Center(x): {self.cx}")
        print(f"Center(y): {self.cy}")
        print(f"Upper-lower limits: {self.up_y, self.down_y}")
        print(f"Right-left limits: {self.right_x, self.left_x}")


def build_area(layout_df):
    filtered = layout_df.loc[(layout_df.layout_items == "alan")]
    area = LayoutItem("area", "area", filtered.x.values[0], filtered.y.values[0], filtered.pos_x.values[0],
                      filtered.pos_y.values[0])
    area.build_limits()
    area.display()
    return area


def build_layout_objects(sta_item_dict, layout_df):
    object_list = []
    for sta in sta_item_dict.keys():
        items = [item for item in sta_item_dict[sta] if "hazırlık" not in item]
        for item in items:
            filtered = layout_df.loc[(layout_df.layout_items == item)]
            x = filtered.x.values[0]
            y = filtered.y.values[0]
            cx = None
            cy = None
            object_list.append(LayoutItem(item, sta, x, y, cx, cy))
    return object_list


def optimize_layout(area_object, item_objects, sta_layout_item_dict):
    env = area_object
    items = [str(item.name) + " - " + str(item.ws) for item in item_objects]
    sta_layout_items = sta_layout_item_dict
    pil_depo = [pil for pil in items if "pil ara depo" in pil]
    for pil in pil_depo[1:]:
        pdx = items.index(pil)
        item_objects.pop(pdx)
        items.remove(pil)
        soi = pil.split(" - ")[1]
        sta_layout_items[soi].remove("pil ara depo")
    items_xlen = {str(item.name) + " - " + str(item.ws): item.x for item in item_objects}
    items_ylen = {str(item.name) + " - " + str(item.ws): item.y for item in item_objects}
    line_cells = [item for item in items if "box" in item]
    M = 99999
    stas = list(sta_layout_items.keys())
    for key in sta_layout_items.keys():
        sta_layout_items[key] = [str(itm) + " - " + str(key) for itm in sta_layout_items[key] if "hazırlık" not in itm]

    # PROBLEM ENVIRONMENT
    model = LpProblem("LayoutPlan", LpMinimize)

    # DECISION VARIABLES
    centeroid_xs = LpVariable.dicts("CenterX", items, env.left_x, env.right_x)
    centeroid_ys = LpVariable.dicts("CenterY", items, env.down_y, env.up_y)
    dummy_xs = LpVariable.dicts("Dummy X", (items, items), 0, 1, LpBinary)
    dummy_ys = LpVariable.dicts("Dummy Y", (items, items), 0, 1, LpBinary)
    dummy_zs = LpVariable.dicts("Dummy Z", (items, items), 0, 1, LpBinary)
    dummy_rotate = LpVariable.dicts("Dummy Rotate pi/2", items, 0, 1, LpBinary)
    connectx = LpVariable.dicts("Line Connection X", items, 0, 1, LpBinary)
    connecty = LpVariable.dicts("Line Connection Y", items, 0, 1, LpBinary)
    x_abs_difference = LpVariable.dicts("Manhattan Dist X", (items, items), 0)
    y_abs_difference = LpVariable.dicts("Manhattan Dist Y", (items, items), 0)

    # OBJECTIVE FUNCTION
    model += lpSum(
        lpSum(x_abs_difference[i][j] + y_abs_difference[i][j] for i in sta_layout_items[k] for j in sta_layout_items[k])
        for k in stas)

    # CONSTRAINTS
    # Dummies for absolute value of distance
    for k in stas:
        for i in sta_layout_items[k]:
            for j in [itm for itm in sta_layout_items[k] if itm != i]:
                model += centeroid_xs[i] - centeroid_xs[j] <= x_abs_difference[i][j]
                model += centeroid_xs[j] - centeroid_xs[i] <= x_abs_difference[i][j]
                model += centeroid_ys[i] - centeroid_ys[j] <= y_abs_difference[i][j]
                model += centeroid_ys[j] - centeroid_ys[i] <= y_abs_difference[i][j]

    # Each item lies within production area
    for item in items:
        model += centeroid_xs[item] + (
                (1 - dummy_rotate[item]) * items_xlen[item] / 2 + dummy_rotate[item] *
                items_ylen[item] / 2) <= env.right_x
        model += centeroid_xs[item] - (
                (1 - dummy_rotate[item]) * items_xlen[item] / 2 + dummy_rotate[item] *
                items_ylen[item] / 2) >= env.left_x
        model += centeroid_ys[item] + (
                (1 - dummy_rotate[item]) * items_ylen[item] / 2 + dummy_rotate[item] *
                items_xlen[item] / 2) <= env.up_y
        model += centeroid_ys[item] - (
                (1 - dummy_rotate[item]) * items_ylen[item] / 2 + dummy_rotate[item] *
                items_xlen[item] / 2) >= env.down_y

        # Items could not intersect with each other
        itmindx = items.index(item)
        relatives = [itm for itm in items[itmindx + 1:]]
        for rel in relatives:
            model += centeroid_xs[item] - centeroid_xs[rel] + dummy_xs[item][rel] * M + dummy_zs[item][rel] * M >= (
                    ((1 - dummy_rotate[item]) * items_xlen[item] + dummy_rotate[item] * items_ylen[item]) +
                    ((1 - dummy_rotate[rel]) * items_xlen[rel] + dummy_rotate[rel] * items_ylen[rel])) / 2

            model += centeroid_xs[rel] - centeroid_xs[item] + (1 - dummy_xs[item][rel]) * M + dummy_zs[item][
                rel] * M >= (((1 - dummy_rotate[item]) * items_xlen[item] + dummy_rotate[item] * items_ylen[item]) +
                             ((1 - dummy_rotate[rel]) * items_xlen[rel] + dummy_rotate[rel] * items_ylen[rel])) / 2

            model += centeroid_ys[item] - centeroid_ys[rel] + dummy_ys[item][rel] * M + (
                    1 - dummy_zs[item][rel]) * M >= (
                             ((1 - dummy_rotate[item]) * items_ylen[item] + dummy_rotate[item] * items_xlen[item]) +
                             ((1 - dummy_rotate[rel]) * items_ylen[rel] + dummy_rotate[rel] * items_xlen[rel])) / 2

            model += centeroid_ys[rel] - centeroid_ys[item] + (1 - dummy_ys[item][rel]) * M + (
                    1 - dummy_zs[item][rel]) * M >= (
                             ((1 - dummy_rotate[item]) * items_ylen[item] + dummy_rotate[item] * items_xlen[item]) +
                             ((1 - dummy_rotate[rel]) * items_ylen[rel] + dummy_rotate[rel] * items_xlen[rel])) / 2

            model += dummy_xs[item][rel] + dummy_ys[item][rel] + dummy_zs[item][rel] <= 2

    for i in range(len(line_cells) - 1):
        item = line_cells[i]
        rel = line_cells[i + 1]

        model += dummy_rotate[item] - dummy_rotate[rel] >= -M * connectx[item]
        model += dummy_rotate[item] - dummy_rotate[rel] <= M * (1 - connectx[item]) - 1
        model += dummy_rotate[item] - dummy_rotate[rel] >= 1 - M * (1 - connecty[item])
        model += dummy_rotate[item] - dummy_rotate[rel] <= M * connecty[item]

        model += centeroid_xs[item] + (
                (1 - dummy_rotate[item]) * items_xlen[item] + dummy_rotate[item] * items_ylen[item]) / 2 == (
                         centeroid_xs[rel] - ((1 - dummy_rotate[rel]) * items_xlen[rel] -
                                              dummy_rotate[rel] * items_ylen[rel] +
                                              2 * connectx[item] * items_ylen[rel]) / 2)
        model += centeroid_ys[item] + (
                (1 - dummy_rotate[item]) * items_ylen[item] + dummy_rotate[item] * items_xlen[item]) / 2 == (
                         centeroid_ys[rel] + ((1 - dummy_rotate[rel]) * items_ylen[rel] -
                                              2 * connecty[item] - dummy_rotate[rel] * items_xlen[rel]) / 2)

    model.solve()

    for item in item_objects:
        opt_var = item.name + " - " + item.ws
        item.update_centeroids(centeroid_xs[opt_var].varValue, centeroid_ys[opt_var].varValue,
                               dummy_rotate[opt_var].varValue)


def render_layout(area_object, sta_layout_items, item_objects, base_df):
    area_img = Image.new('RGB', (area_object.x, area_object.y), (43, 43, 43))
    draw = ImageDraw.Draw(area_img)
    sta_colors = {}
    layout_info = {sta: {"color": np.nan, "items": {}} for sta in base_df.sta.unique()}

    step_size = int(area_object.x/20)
    for x in range(0, area_object.x, step_size):
        line = ((x, 0), (x, area_object.y))
        draw.line(line, fill=(175, 177, 179))

    for y in range(0, area_object.y, step_size):
        line = ((0, y), (area_object.x, y))
        draw.line(line, fill=(175, 177, 179))

    for item in item_objects:
        idx = item_objects.index(item)
        ws = item.ws
        name = item.name
        task_list = base_df.loc[(base_df["sta"] == ws) & (base_df["place"] == name)].task_id.unique()
        layout_info[ws]["items"][name] = {"item_no": idx+1, "item_task": list(task_list)}

    for sta in sta_layout_items.keys():
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        sta_colors[sta] = (r, g, b)
        layout_info[sta]["color"] = (r, g, b)

    for item in item_objects:
        idx = item_objects.index(item)
        ulx = item.left_x + area_object.x / 2
        uly = -item.up_y + area_object.y / 2
        lrx = item.right_x + area_object.x / 2
        lry = -item.down_y + area_object.y / 2
        draw.rectangle((int(ulx), int(uly), int(lrx), int(lry)), fill=sta_colors[item.ws], outline=(0, 0, 0))
        draw.text((item.cx + area_object.x / 2 - 1, -item.cy + area_object.y / 2 - 1), str(idx+1))

    return area_img, layout_info


def summarize_stations(data):
    stas = data.sta.unique()
    sta_no = len(stas)
    worker_no = 2 * sta_no
    sta_dict = {"Station #" + str(i + 1): stas[i] for i in range(len(stas))}
    sta_names = list(sta_dict.keys())
    assigned_tasks = {}
    task_times = {}
    sta_times = {}
    sta_idle = {}
    sta_util = {}
    sta_blocking = {}
    sta_starving = {}
    sta_bs_total = {}
    for soi in sta_dict.keys():
        sta = sta_dict[soi]
        assigned_tasks[soi] = list(data.loc[data.sta == sta].task_id)
        task_times[soi] = list(data.loc[data.sta == sta].task_time)
        sta_times[soi] = data.loc[data.sta == sta].task_time.sum()
    max_time = max(list(sta_times.values()))
    for sta in sta_times.keys():
        sta_util[sta] = round(sta_times[sta] / max_time, 2)
        sta_idle[sta] = -sta_times[sta] + max_time
        avg_util = round(sum(list(sta_util.values())) / len(list(sta_util.values())), 2)

    for i in range(len(sta_names)):
        sn1 = sta_names[i]
        if i != sta_no - 1:
            sn2 = sta_names[i + 1]
            if sta_times[sn1] < sta_times[sn2]:
                sta_blocking[sn1] = sta_times[sn2] - sta_times[sn1]
            else:
                sta_blocking[sn1] = 0
        else:
            sta_blocking[sn1] = 0

    for i in range(len(sta_names)):
        sn1 = sta_names[i]
        if i != 0:
            sn2 = sta_names[i - 1]
            if sta_times[sn1] < sta_times[sn2]:
                sta_starving[sn1] = sta_times[sn2] - sta_times[sn1]
            else:
                sta_starving[sn1] = 0
        else:
            sta_starving[sn1] = 0

    for key in sta_blocking.keys():
        sta_bs_total[key] = sta_blocking[key] + sta_starving[key]

    return sta_no, worker_no, assigned_tasks, task_times, sta_times, max_time, sta_idle, sta_util, avg_util, \
           sta_blocking, sta_starving, sta_bs_total


def plot_sta_times(times, cyc):
    stas = list(times.keys())
    time = list(times.values())
    fig = px.bar(x=stas, y=time)
    fig.update_layout(title="Processing Time of Stations",
                      xaxis_title="Station",
                      yaxis_title="Time (secs)")
    fig.update_yaxes(range=[0, cyc])
    return fig


def plot_idle_times(times, cyc):
    stas = list(times.keys())
    time = list(times.values())
    fig = px.bar(x=stas, y=time)
    fig.update_layout(title="Idle Time of Stations",
                      xaxis_title="Station",
                      yaxis_title="Time (secs)")
    fig.update_yaxes(range=[0, cyc])
    return fig


def plot_sta_util(times):
    stas = list(times.keys())
    time = [i*100 for i in list(times.values())]
    fig = px.bar(x=stas, y=time)
    fig.update_layout(title="Utilization Rates of Stations",
                      xaxis_title="Station",
                      yaxis_title="Rate %")
    fig.update_yaxes(range=[0, 100])
    return fig


def plot_sta_blocking(times, cyc):
    stas = list(times.keys())
    time = list(times.values())
    fig = px.bar(x=stas, y=time)
    fig.update_layout(title="Blocked Time of Stations",
                      xaxis_title="Station",
                      yaxis_title="Time (secs)")
    fig.update_yaxes(range=[0, cyc])
    return fig


def plot_sta_starving(times, cyc):
    stas = list(times.keys())
    time = list(times.values())
    fig = px.bar(x=stas, y=time)
    fig.update_layout(title="Starved Time of Stations",
                      xaxis_title="Station",
                      yaxis_title="Time (secs)")
    fig.update_yaxes(range=[0, cyc])
    return fig


def plot_sta_bstotal(times, cyc):
    stas = list(times.keys())
    time = list(times.values())
    fig = px.bar(x=stas, y=time)
    fig.update_layout(title="Blocked + Starved Time of Stations",
                      xaxis_title="Station",
                      yaxis_title="Time (secs)")
    fig.update_yaxes(range=[0, cyc])
    return fig
