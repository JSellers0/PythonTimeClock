import PySimpleGUI as sg


class ClockUI:
    def __init__(self):
        sg.theme("Reddit")
        self.font = "Roboto"
        sg.set_options(element_padding=(0, 0))
        sg.set_options(font=(self.font, 10))
        self.PROGRAM_TITLE = "Python Time Clock"
        self.images = {
            "edit_icon": "/static/images/edit_icon.png",
            "cal_icon": "/static/images/cal_icon.png",
        }

    def get_main_window(self, window_location, window_message1, window_message2):
        layout = [
            [
                sg.Text(
                    window_message1,
                    size=(30, 1),
                    font=(self.font, 16),
                    justification="left",
                    key="message1",
                )
            ],
            [
                sg.Text(
                    window_message2,
                    size=(30, 1),
                    font=(self.font, 14),
                    justification="left",
                    key="message2",
                )
            ],
            [
                sg.Button("Start", button_color=("white", "#007339")),
                sg.Button("Stop", button_color=("white", "firebrick4")),
            ],
            [
                sg.Button("Adjust", button_color=("white", "#000000")),
                sg.Button("Report", button_color=("white", "#000000")),
                sg.Button("Exit", button_color=("white", "#000000")),
            ],
        ]

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            grab_anywhere=True,
            keep_on_top=True,
            finalize=True,
        )

    def get_start_window(self, window_location, db, message1):
        layout = [
            [
                sg.Text(
                    message1, size=(20, 1), font=(self.font, 12), justification="left"
                )
            ],
            [
                sg.Text(
                    "Select a Client and Project to start timing:",
                    size=(30, 1),
                    font=(self.font, 14),
                    justification="left",
                )
            ],
            [
                sg.Text(
                    "Clients", key="client_label", justification="left", size=(20, 1)
                ),
                sg.Text("Projects", key="project_label"),
            ],
            [
                sg.Listbox(
                    values=db.getTableItems("client")
                    .sort_values(by="client_name")["client_name"]
                    .tolist(),
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    size=(20, 10),
                    key="client_listbox",
                ),
                sg.Listbox(
                    values=db.getTableItems("project")
                    .sort_values(by="project_name")["project_name"]
                    .tolist(),
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    size=(20, 10),
                    key="project_listbox",
                ),
            ],
            [
                sg.Button("Back"),
                sg.Button("Start", button_color=("white", "#007339")),
                sg.Button("New"),
            ],
        ]

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            finalize=True,
        )

    def get_new_window(self, window_location, view="all"):
        if view == "all":
            layout = [
                [sg.Text("New Client")],
                [sg.Input(key="new_client")],
                [sg.Text("New Project")],
                [sg.Input(key="new_project")],
                [sg.Button("Submit"), sg.Button("Cancel")],
            ]
        elif view == "client":
            layout = [
                [sg.Text("New Client")],
                [sg.Input(key="new_client")],
                [sg.Button("Submit"), sg.Button("Cancel")],
            ]
        elif view == "project":
            layout = [
                [sg.Text("New Project")],
                [sg.Input(key="new_project")],
                [sg.Button("Submit"), sg.Button("Cancel")],
            ]

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            grab_anywhere=False,
            finalize=True,
        )

    def get_adjustment_main_window(self, window_location):
        layout = [
            [sg.Text("Click the table you want to adjust")],
            [
                sg.Button("Times", key="timelog"),
                sg.Button("Clients", key="client"),
                sg.Button("Projects", key="project"),
            ],
            [sg.Button("Close")],
        ]

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            finalize=True,
        )

    def get_adjustment_timestamp_window(self, window_location, default_date):
        layout = [
            [
                sg.Text(
                    "Please type a date as YYYY-MM-DD or use the date selector",
                    key="date_message",
                )
            ],
            [
                sg.Input(default_text=default_date, key="date_input"),
                sg.CalendarButton(
                    "",
                    target="date_input",
                    key="date_select",
                    format="%Y-%m-%d",
                    image_filename=self.images["cal_icon"],
                    size=(1, 1),
                ),
            ],
            [sg.Button("Back"), sg.Button("Submit")],
        ]

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            finalize=True,
        )

    def get_adjustment_results_window(self, window_location, table, df):
        if table == "timelog":
            layout = [
                [
                    sg.Text(
                        "Timelog Rows Available for Adjustment:", font=(self.font, 16),
                    )
                ],
                [
                    sg.Text("Start", size=(20, 1)),
                    sg.Text("Stop", size=(20, 1)),
                    sg.Text("Client", size=(15, 1)),
                    sg.Text("Project", size=(20, 1)),
                ],
            ]
            for index, row in df.iterrows():
                layout.append(
                    [
                        sg.Text(row["start"], size=(20, 1)),
                        sg.Text(row["stop"], size=(20, 1)),
                        sg.Text(row["client_name"], size=(15, 1)),
                        sg.Text(row["project_name"], size=(20, 1)),
                        sg.Button(
                            key="Update " + str(index),
                            image_filename=self.images["edit_icon"],
                        ),
                    ]
                )
            layout.append(
                [sg.Button("+", key="insert", size=(1, 1)), sg.Text("Insert Row")]
            )
            layout.append([sg.Button("Back", key="Close")])

        elif table in ("client", "project"):
            col = []
            for index, row in df.iterrows():
                col.append(
                    [
                        sg.Text(row[table + "ID"], size=(10, 1)),
                        sg.Text(row[table + "_name"], size=(15, 1)),
                        sg.Button(
                            key="Update " + str(index),
                            image_filename=self.images["edit_icon"],
                        ),
                    ]
                )
            layout = [
                [sg.Text("Records Available:", font=(self.font, 16))],
                [
                    sg.Text(table + "ID", size=(10, 1)),
                    sg.Text(table + " Name", size=(15, 1)),
                ],
                [sg.Column(col, scrollable=True, vertical_scroll_only=True)],
                [sg.Button("+", key="insert", size=(1, 1)), sg.Text("Insert Row")],
                [sg.Button("Back", key="Close")],
            ]

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            finalize=True,
        )

    def get_update_window(self, window_location, table, row, client_list, project_list):
        if table == "insert":
            layout = [
                [
                    sg.Text("Start", size=(20, 1), pad=(2.5, 1)),
                    sg.Text("Stop", size=(20, 1), pad=(2.5, 1)),
                ],
                [
                    sg.Input(row["start"], size=(20, 1), pad=(2.5, 1), key="start"),
                    sg.Input(row["stop"], size=(20, 1), pad=(2.5, 1), key="stop"),
                ],
                [
                    sg.Text("Client", size=(20, 1), pad=(2.5, 1)),
                    sg.Text("Project", size=(22, 1), pad=(2.5, 1)),
                ],
                [
                    sg.Listbox(
                        values=client_list,
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(20, 10),
                        pad=(2.5, 1),
                        key="client",
                    ),
                    sg.Listbox(
                        values=project_list,
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(20, 10),
                        pad=(2.5, 1),
                        key="project",
                    ),
                ],
            ]
        elif table == "timelog":
            if row["stop"] == "2001-01-01 01:01":
                row["stop"] = row["start"]
            layout = [
                [
                    sg.Text("Start", size=(20, 1), pad=(2.5, 1)),
                    sg.Text("Stop", size=(20, 1), pad=(2.5, 1)),
                ],
                [
                    sg.Input(row["start"], size=(20, 1), pad=(2.5, 1), key="start"),
                    sg.Input(row["stop"], size=(20, 1), pad=(2.5, 1), key="stop"),
                ],
                [
                    sg.Text("Client", size=(20, 1), pad=(2.5, 1)),
                    sg.Text("Project", size=(22, 1), pad=(2.5, 1)),
                ],
                [
                    sg.Listbox(
                        values=client_list,
                        default_values=row["client_name"],
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(20, 10),
                        pad=(2.5, 1),
                        key="client",
                    ),
                    sg.Listbox(
                        values=project_list,
                        default_values=row["project_name"],
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(20, 10),
                        pad=(2.5, 1),
                        key="project",
                    ),
                ],
                [
                    sg.Text(
                        "Error: Start Value must be earlier than, or equal to, Stop Value",
                        visible=False,
                        key="error_message",
                    )
                ],
            ]
        else:
            layout = [
                [sg.Text(table + " ID"), sg.Text(row[table + "ID"])],
                [sg.Text(table + "Name"), sg.Input(row[table + "_name"])],
            ]
        layout.append([sg.Button("Submit"), sg.Button("Cancel")])

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            finalize=True,
        )

    def get_report_date_window(self, window_location, start_date, stop_date):
        layout = [
            [sg.Text("Start")],
            [
                sg.Input(start_date, key="start"),
                sg.CalendarButton(
                    "",
                    target="start",
                    key="date_select",
                    format="%Y-%m-%d",
                    image_filename=self.images["cal_icon"],
                    size=(1, 1),
                ),
            ],
            [sg.Text("End")],
            [
                sg.Input(stop_date, key="stop"),
                sg.CalendarButton(
                    "",
                    target="stop",
                    key="date_select",
                    format="%Y-%m-%d",
                    image_filename=self.images["cal_icon"],
                    size=(1, 1),
                ),
            ],
            [
                sg.Text(
                    "Error: Nothing was tracked during the dates selected.",
                    key="error_message",
                    visible=False,
                )
            ],
            [sg.Button("Submit"), sg.Button("Cancel")],
        ]

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            finalize=True,
        )

    def get_report_output_window(self, window_location, summary_df, total_df, i):
        layout = [
            [
                sg.Text(
                    "Report for {}".format(total_df.iloc[0]["date"]),
                    font=(self.font, 16),
                    relief=sg.RELIEF_RIDGE,
                    pad=(2, 0),
                ),
                sg.Text(
                    "Total Hours {}".format(total_df.iloc[0]["diff"]),
                    font=(self.font, 16),
                    relief=sg.RELIEF_RIDGE,
                    pad=(2, 0),
                ),
                sg.Button("<", key="decrement", size=(1, 1)),
                sg.Text(i + 1, key="page"),
                sg.Button(">", key="increment", size=(1, 1)),
            ],
            [
                sg.Text("Client", size=(15, 1),),
                sg.Text("Project", size=(20, 1),),
                sg.Text("Time", size=(15, 1),),
            ],
        ]

        for index, row in summary_df.iterrows():
            layout.append(
                [
                    sg.Text(row["client_name"], size=(15, 1),),
                    sg.Text(row["project_name"], size=(20, 1),),
                    sg.Text(row["diff"], size=(15, 1),),
                ]
            )
        layout.append(
            [
                sg.Button("New Dates", key="back"),
                sg.Button("Return to Main", key="main", size=(13, 1)),
            ]
        )

        return sg.Window(
            self.PROGRAM_TITLE,
            layout=layout,
            location=window_location,
            auto_size_buttons=False,
            finalize=True,
        )
