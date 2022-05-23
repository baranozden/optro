from dash import dcc, html

def render_landing():
    return html.Div([
        html.H2("Welcome to Optro!"),
        html.P("Optro is an open-source web-based tool for analyzing data collected from production processes. After "
               "uploading necessary data, you can use Optro's different features freely."),

        html.H2("Guidelines"),

        html.H3("A. Uploading Data"),

        html.H4("1. Task Data"),
        html.P("Task data represents your production processes directly. To run models correctly, you should provide "
               "your data via an MS Excel spreadsheet. File format and important notes are given below."),
        html.H5("File Format:"),
        html.Ul([
            html.Li("task_id (integer): The unique identifier for each task. Each task should be numbered "
                    "in order starting from 1 (Example: 1)"),
            html.Li("task_name (string): Name of each task (Example: Quality Control)"),
            html.Li("sums (integer): The total duration of completing the corresponding task in the process of "
                    "producing a unit product. It must be entered in the same unit for each task. Specifying the unit "
                    "is not important (Example: 225)"),
            html.Li("precedence (integer list): It contains the tasks that must have been completed before the related "
                    "task can be done. The predecessor task must be specified according to the 'task_id' column. "
                    "In case of more than one premise, the numbers should be seperated by “,” (comma) "
                    "and “ “ (single space) between them. 0 can be written if there is no predecessor. "
                    "(Example: 1, 4, 5)"),
            html.Li("place (string): Specifies the layout element that the task should be performed on. These "
                    "layout elements must be same with the elements given in the Layout Data. (Example: Warehouse)"),
        ]),
        html.H5("Important Notes:"),
        html.Ol([
            html.Li("“task_id”, “task_name”, “sums”, “precedence”, “place” columns must be present in the data, "
                    "without containing any typos and be filled in for each task for the models to work properly."),
            html.Li("Determining the tasks as accurately as possible and making time calculations with the right "
                    "time study methods increases the applicability of the model results in the real world."),
            html.Li("It is critical that the information shared in the precedence column match the task_id column."),
            html.Li("The information shared in the place column must exactly match the Layout Data."),
        ]),


        html.H4("2. Layout Data"),
        html.P("Layout data identify your production layout directly. To run models correctly, you should provide "
               "your data via an MS Excel spreadsheet. File format and important notes are given below."),
        html.H5("File Format:"),
        html.Ul([
            html.Li("layout_items (string): Names of the elements in the layout where tasks are performed. "
                    "(Example: Warehouse)"),
            html.Li("x (integer): Represents the width of the element. (Example: 30)"),
            html.Li("y (integer): Represents the height of the element. (Example: 30)"),
            html.Li("pos_x (integer): Position of the element in the horizontal axis (Example: 30)"),
            html.Li("pos_y (integer): Position of the element in the vertical axis (Example: 40)"),
        ]),

        html.H5("Important Notes:"),
        html.Ol([
            html.Li("It is mandatory to add an element named 'alan' to the data of the layout elements. "
                    "The 'alan' element represents the entire area where the layout will be built. "
                    "The x and y lengths of the 'alan' element must be large enough. The pos_x and pos_y coordinates "
                    "of the 'alan' element are required and the best option is to use 0 for both coordinates."),
            html.Li("The campus planning model aims to find the best location only for elements with empty "
                    "pos_x and pos_y. These elements represent the elements whose locations are not certain and "
                    "finding the best position is desired. The pos_x and pos_y columns of the elements whose positions "
                    "are definite should be filled in the data set considering the center "
                    "of the 'alan' element."),
            html.Li("If there are line-type elements in the layout, these elements must be specified as the box class. "
                    "The Box class supports up to two different types of line cells for two distinct types of "
                    "operations. If only one type of line is used in the production process, "
                    "only “box-in” names should be used, and if two types of lines are used, the names “box-in” "
                    "and “box-out” should be used separately for these types."),
            html.Li("Elements shared in the Layout Data will not participate in the modeling processes unless "
                    "they are specified in the 'place' column of the relevant tasks in the Task Data."),
        ]),

        html.H3("B. Modelling"),
        html.P("Optro's main goal is providing the best solutions that ensures reaching the desired production capacity"
               " for any manufacturing system. After uploading the data you can give your desired cycle time as input. "
               "Optro is going to optimize your production environment automatically and show you reports. Information "
               "about models used in optimization are given below."),
        html.H4("1. Line Balancing Models"),
        html.P("Line Balancing Models are the core modules of Optro's optimization process. There are two different "
               "objectives as default and they are named as Model 1 and Model 2."),
        html.H5("Model 1"),
        html.P("Model 1 aims to distribute given tasks to a minimum number of workstations considering target "
               "production capacity and precedence relations. Basically it provides a solution with minimum cost of "
               "investment (equipments, layout items, etc.)."),
        html.H5("Model 2"),
        html.P("Model 2 aims to distribute given tasks to workstations by distributing processing time in each stations"
               " as evenly as possible considering target production capacity and precedence relations. "
               "Basically it provides a solution with minimum idle time and maximum labor efficiency."),
        html.H4("2. Layout Planning Model"),
        html.P("Layout Planning Model uses the solutions provided by Model 1 and Model 2 to make recommendations about"
               "facility layout plan with respect to each solution. It aims reaching the minimum total distance between the "
               "elements of each workstations."),
    ], className="guidelines")
