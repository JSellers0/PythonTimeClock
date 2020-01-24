""" ====== PROGRAM ARCHITECTURE ====== """
# TODO: Create "About" or Readme to include link to icons8 <a target="_blank" href="https://icons8.com/icons/set/edit-property">Edit Property icon</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>
# <a target="_blank" href="https://icons8.com/icons/set/calendar">Calendar icon</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>


""" ====== DATABASE ARCHITECTURE ====== """
# TODO: TimeLog State column (ACT, DEL).  Adjustment Delete button sets State to DEL.  Update all queries to only return active rows.
# TODO: Note Table, NoteID Field in Timelog to add notes, especially for projects that share activity code.
# TODO: Build project and client counters and order by most frequent.

""" ====== PROGRAM FEATURES ====== """
# TODO: Reporting - Note on report page that there are missing stamps and calculate available times.
# TODO: Reporting - Quick Link for 'This Week'
# TODO: UI Formatting: Adjustment and Reporting windows
# TODO: Reporting Excel Export

""" ====== BUG FIXES ====== """
# BUG: More robust item input validation: required fields are noted, submitted, proper format

import sys

from datetime import datetime
from datetime import timedelta
from dateutil import tz

class TimeClock():

    def convert_to_utc(self, timestamp):
        return (
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
            .replace(tzinfo=tz.tzlocal())
            .astimezone(tz.tzutc())
            .strftime("%Y-%m-%d %H:%M")
        )

    def convert_to_local(self, timestamp, date_only=False):
        if date_only:
            return (
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                .replace(tzinfo=tz.tzutc())
                .astimezone(tz.tzlocal())
                .strftime("%Y-%m-%d")
            )
        else:
            return (
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                .replace(tzinfo=tz.tzutc())
                .astimezone(tz.tzlocal())
                .strftime("%Y-%m-%d %H:%M")
            )

    def initialize_states(self):
        state = {
            "client_id": 0,
            "client": "",
            "project_id": 0,
            "project": "",
            "timelogid": 0,
            "start_time": "",
            "message1": "Python Time Clock",
            "message2": "Welcome to Work.  Click Start.",
            "adjust_date": self.convert_to_local(
                datetime.utcnow().strftime("%Y-%m-%d %H:%M"), date_only=True
            ),
            "return_to_main": False,
            "adjust_view": "",
        }
        return state

    def start_timing(self, state, db):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        item = {
            "start": timestamp,
            "projectid": str(state["project_id"]),
            "clientid": str(state["client_id"]),
        }
        db.create_table_item(item, "timelog")
        state["start_time"] = self.convert_to_local(timestamp)
        db.c.execute("SELECT timelogid FROM timelog ORDER BY timelogid DESC LIMIT 1;")
        result = db.c.fetchone()
        state["message1"] = "Tracking {} - {}".format(state["client"], state["project"])
        state["message2"] = "since {}".format(state["start_time"])
        state["timelogid"] = result[0]
        return state

    def stop_timing(self, state, db):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        item = {"field": "stop", "value": timestamp, "itemid": state["timelogid"]}
        db.update_table_item(item, "timelog")
        stop_time = self.convert_to_local(timestamp)
        state["message1"] = "Stopped {} - {}".format(state["client"], state["project"])
        state["message2"] = "at {}".format(stop_time)
        state["timelogid"] = 0
        return state

    def run(self, db, ui):
        DB = db
        UI = ui
        state = self.initialize_states()
        main_window = UI.get_main_window((75, 0), state["message1"], state["message2"])
        while True:
            event, values = main_window.read(timeout=10)
            if event in (None, "Exit"):
                if state["timelogid"] > 0:
                    state = self.stop_timing(state, DB)
                main_window.close()
                break

            elif event == "Report":
                report_date_window = UI.get_report_date_window(
                    main_window.current_location(),
                    datetime.today().strftime("%Y-%m-%d"),
                    datetime.today().strftime("%Y-%m-%d"),
                )
                main_window.close()
                while True:
                    if state["return_to_main"]:
                        state["return_to_main"] = False
                        break
                    report_date_event, report_date_values = report_date_window.read(
                        timeout=10
                    )
                    if report_date_event == None:
                        DB.close()
                        sys.exit()
                    elif report_date_event == "Cancel":
                        main_window = UI.get_main_window(
                            report_date_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        report_date_window.close()
                        break
                    
                    elif report_date_event == "Submit":
                        report_df = DB.getTableItems(
                            "timelog",
                            self.convert_to_utc(report_date_values["start"] + " 00:00"),
                            self.convert_to_utc(report_date_values["stop"] + " 23:59"),
                        )
                        # If the current timelog row is in the report, set the stop time
                        # to the current time for calculations
                        if len(report_df) == 0:
                            report_date_window["error_message"].Update(visible=True)
                        else:
                            if (
                                len(report_df[report_df.timelogid == state["timelogid"]])
                                == 1
                            ):
                                report_df.loc[
                                    report_df.timelogid == state["timelogid"], ("stop")
                                ] = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

                            # Check for other null stop values prior to reporting calculations
                            if report_df["stop"].isna().sum() > 0:
                                gap_df = report_df.loc[report_df.stop.isna()]
                                gap_df["date"] = gap_df["start"].apply(
                                    lambda x: self.convert_to_local(x, date_only=True)
                                )
                                state["report_gap_dates"] = gap_df["date"].unique().tolist()
                                gap_df = None
                                report_df.dropna(inplace=True)

                            report_df["diff"] = report_df["stop"].apply(
                                lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M")
                            ) - report_df["start"].apply(
                                lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M")
                            )
                            report_df["date"] = report_df["start"].apply(
                                lambda x: self.convert_to_local(x, date_only=True)
                            )
                            summary_df = (
                                report_df[["date", "client_name", "project_name", "diff"]]
                                .groupby(by=["date", "client_name", "project_name"])
                                .sum()
                            )
                            summary_df.reset_index(inplace=True)
                            # Convert Diff to Hours:Minutes
                            summary_df["diff"] = summary_df["diff"].apply(
                                lambda x: str(x)[
                                    str(x).find("d") + len("days ") : len(str(x)) - 3
                                ]
                            )
                            total_time = (
                                report_df[["date", "diff"]].groupby(by=["date"]).sum()
                            )
                            total_time.reset_index(inplace=True)
                            # Convert Total Time Diff to Hours:Minutes
                            total_time["diff"] = total_time["diff"].apply(
                                lambda x: str(x)[
                                    str(x).find("d") + len("days ") : len(str(x)) - 3
                                ]
                            )

                            i = 0
                            dates = total_time.date.unique().tolist()
                            report_window = UI.get_report_output_window(
                                report_date_window.current_location(),
                                summary_df.loc[summary_df.date == dates[i]],
                                total_time.loc[total_time.date == dates[i]],
                                i,
                            )
                            report_date_window.close()
                            while True:
                                report_event, report_values = report_window.read(timeout=10)
                                if report_event == None:
                                    DB.close()
                                    sys.exit()
                                
                                elif report_event == "back":
                                    report_date_window = UI.get_report_date_window(
                                        report_window.current_location(),
                                        report_date_values["start"],
                                        report_date_values["stop"],
                                    )
                                    report_window.close()
                                    break
                                
                                elif report_event == "increment":
                                    if i + 1 < len(dates):
                                        i += 1
                                        report_window2 = report_window
                                        report_window = UI.get_report_output_window(
                                            report_window2.current_location(),
                                            summary_df.loc[summary_df.date == dates[i]],
                                            total_time.loc[total_time.date == dates[i]],
                                            i,
                                        )
                                        report_window2.close()
                                elif report_event == "decrement":
                                    if i - 1 >= 0:
                                        i -= 1
                                        report_window2 = report_window
                                        report_window = UI.get_report_output_window(
                                            report_window2.current_location(),
                                            summary_df.loc[summary_df.date == dates[i]],
                                            total_time.loc[total_time.date == dates[i]],
                                            i,
                                        )
                                        report_window2.close()
                                
                                elif report_event == "main":
                                    main_window = UI.get_main_window(
                                        report_window.current_location(),
                                        state["message1"],
                                        state["message2"],
                                    )
                                    report_window.close()
                                    state["return_to_main"] = True
                                    break

            elif event == "Adjust":
                adjust_window = UI.get_adjustment_main_window(
                    main_window.current_location()
                )
                main_window.close()
                while True:
                    adjust_event, adjust_values = adjust_window.read(timeout=10)
                    if adjust_event == None:
                        DB.close()
                        sys.exit()
                    
                    elif adjust_event == "Close":
                        state["adjust_view"] = ""
                        main_window = UI.get_main_window(
                            adjust_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        adjust_window.close()
                        break
                    
                    elif adjust_event == "timelog":
                        state["adjust_view"] = adjust_event
                        adjust_select_window = UI.get_adjustment_timestamp_window(
                            adjust_window.current_location(), state["adjust_date"]
                        )
                        adjust_window.close()
                        while True:
                            (
                                adjust_select_event,
                                adjust_select_values,
                            ) = adjust_select_window.read(timeout=10)
                            if adjust_select_event == None:
                                DB.close()
                                sys.exit()
                            
                            elif adjust_select_event == "Back":
                                adjust_window = UI.get_adjustment_main_window(
                                    adjust_select_window.current_location()
                                )
                                adjust_select_window.close()
                                state["adjust_view"] = ""
                                break
                            
                            elif adjust_select_event == "Submit":
                                state["adjust_date"] = adjust_select_values["date_input"]
                                break
                    
                    elif adjust_event in ("client", "project"):
                        state["adjust_view"] = adjust_event

                    if state["adjust_view"]:
                        if state["adjust_view"] == "timelog":
                            adjust_df = DB.getTableItems(
                                table="timelog",
                                start_date=self.convert_to_utc(
                                    adjust_select_values["date_input"] + " 00:00"
                                ),
                                end_date=self.convert_to_utc(
                                    adjust_select_values["date_input"] + " 23:59"
                                ),
                            )
                            adjust_df.fillna("2001-01-01 06:01", inplace=True)
                            adjust_df["start"] = adjust_df["start"].apply(
                                lambda x: self.convert_to_local(x)
                            )
                            adjust_df["stop"] = adjust_df["stop"].apply(
                                lambda x: self.convert_to_local(x)
                            )
                            adjust_result_window = UI.get_adjustment_results_window(
                                adjust_select_window.current_location(),
                                state["adjust_view"],
                                adjust_df,
                            )
                            adjust_select_window.close()
                        else:
                            adjust_df = DB.getTableItems(state["adjust_view"])
                            adjust_result_window = UI.get_adjustment_results_window(
                                adjust_window.current_location(),
                                state["adjust_view"],
                                adjust_df,
                            )
                            adjust_window.close()
                        while True:
                            adjustment_event, adjustment_values = adjust_result_window.read(
                                timeout=10
                            )
                            if adjustment_event == None:
                                DB.close()
                                sys.exit()
                            
                            elif adjustment_event == "Close":
                                adjust_window = UI.get_adjustment_main_window(
                                    adjust_result_window.current_location()
                                )
                                state["adjust_view"] = ""
                                adjust_result_window.close()
                                break
                            
                            elif adjustment_event == "insert":
                                if state["adjust_view"] == "timelog":
                                    row = {"start": state["adjust_date"], "stop": state["adjust_date"]}
                                    insert_window = UI.get_update_window(adjust_result_window.current_location(),
                                                                         "insert",
                                                                         row,
                                                                         DB.getTableItems("client")["client_name"].tolist(),
                                                                         DB.getTableItems("project")["project_name"].tolist(),
                                                                         )
                                    adjust_result_window.close()
                                else:
                                    insert_window = UI.get_new_window(adjust_result_window.current_location(), state["adjust_view"])
                                    adjust_result_window.close()
                                while True:
                                    insert_event, insert_values = insert_window.read(timeout=10)
                                    if insert_event in (None, "Cancel"):
                                        adjust_result_window = UI.get_adjustment_results_window(
                                            insert_window.current_location(),
                                            state["adjust_view"],
                                            adjust_df,
                                        )
                                        insert_window.close()
                                        break
                                    elif insert_event == "Submit":
                                        # DB Insert Row
                                        if state["adjust_view"] == "timelog":
                                            item = {"start": insert_values["start"],
                                                    "stop": insert_values["stop"],
                                                    "projectid": DB.getTableItemID(insert_values["project"][0], "project"),
                                                    "clientid": DB.getTableItemID(insert_values["client"][0], "client")
                                            
                                                }
                                        elif state["adjust_view"] == "client":
                                            item = insert_values["new_client"]
                                        elif state["adjust_view"] == "project":
                                            item = insert_values["new_project"]
                                        DB.create_table_item(item, state["adjust_view"])
                                        if state["adjust_view"] == "timelog":
                                            adjust_df = adjust_df = DB.getTableItems(
                                                state["adjust_view"],
                                                self.convert_to_utc(
                                                    adjust_select_values["date_input"] + " 00:00"
                                                ),
                                                self.convert_to_utc(
                                                    adjust_select_values["date_input"] + " 23:59"
                                                ),
                                            )
                                        else:
                                            adjust_df = DB.getTableItems(state["adjust_view"])
                                        adjust_result_window = UI.get_adjustment_results_window(
                                            insert_window.current_location(),
                                            state["adjust_view"],
                                            adjust_df,
                                        )
                                        insert_window.close()
                                        break

                            elif "Update" in adjustment_event:
                                row = adjust_df.iloc[
                                    int(adjustment_event[len("Update ") :])
                                ]
                                update_window = UI.get_update_window(
                                    adjust_result_window.current_location(),
                                    state["adjust_view"],
                                    row,
                                    DB.getTableItems("client")["client_name"].tolist(),
                                    DB.getTableItems("project")["project_name"].tolist(),
                                )
                                adjust_result_window.close()
                                while True:
                                    update_event, update_values = update_window.read(
                                        timeout=10
                                    )
                                    if update_event == None:
                                        DB.close()
                                        sys.exit()
                                    
                                    elif update_event == "Cancel":
                                        adjust_result_window = UI.get_adjustment_results_window(
                                            update_window.current_location(),
                                            state["adjust_view"],
                                            adjust_df,
                                        )
                                        update_window.close()
                                        break
                                    
                                    elif update_event == "Submit":
                                        if state["adjust_view"] == "timelog":
                                            if (
                                                update_values["start"] <= update_values["stop"]
                                                or update_values["stop"] == ""
                                            ):
                                                # If Start/Stop changed, ask about adjacent timestamps
                                                if update_values["start"] != row["start"]:
                                                    print("Start Adjacent Check")

                                                if update_values["stop"] != row["stop"]:
                                                    print("Stop Adjacent Check")

                                                # Set timelogid in update_values
                                                update_values["timelogid"] = row["timelogid"]
                                                # If the updated timelog row is the current row, 
                                                # then make sure we adjust the
                                                # State values for the main window message
                                                # Will want to do a similar check if we do the 
                                                # Start Adjacent Update
                                                if (
                                                    state["timelogid"]
                                                    == update_values["timelogid"]
                                                ):
                                                    state["start_time"] = update_values["start"]
                                                    state["client"] = update_values[
                                                        "client"
                                                    ][0]
                                                    state["project"] = update_values[
                                                        "project"
                                                    ][0]
                                                    state[
                                                        "message1"
                                                    ] = "Tracking {} - {}".format(
                                                        state["client"], state["project"]
                                                    )
                                                    state["message2"] = "since {}".format(
                                                        state["start_time"]
                                                    )

                                                update_values["start"] = self.convert_to_utc(
                                                    update_values["start"]
                                                )
                                                if not update_values["stop"] == "":
                                                    update_values["stop"] = self.convert_to_utc(
                                                        update_values["stop"]
                                                    )
                                                DB.update_timelog_row(update_values)
                                                adjust_df = DB.getTableItems(
                                                    "timelog",
                                                    self.convert_to_utc(
                                                        state["adjust_date"] + " 00:00"
                                                    ),
                                                    self.convert_to_utc(
                                                        state["adjust_date"] + " 23:59"
                                                    ),
                                                )
                                                adjust_df.fillna(
                                                    "2001-01-01 06:01", inplace=True
                                                )
                                                adjust_df["start"] = adjust_df["start"].apply(
                                                    lambda x: self.convert_to_local(x)
                                                )
                                                adjust_df["stop"] = adjust_df["stop"].apply(
                                                    lambda x: self.convert_to_local(x)
                                                )
                                            else:
                                                update_window["error_message"].Update(
                                                    visible=True
                                                )
                                        else:
                                            if not DB.check_table_item_exists(state["adjust_view"], update_values[0]):
                                                item = {"itemid": row[state["adjust_view"]+"ID"], "field": state["adjust_view"] + "_name", "value": update_values[0]}
                                                print(item)
                                                DB.update_table_item(item, state["adjust_view"])
                                                adjust_df = DB.getTableItems(state["adjust_view"])
                                        adjust_result_window = UI.get_adjustment_results_window(
                                                    update_window.current_location(), state["adjust_view"], adjust_df
                                                )
                                        update_window.close()
                                        break

            elif event == "Stop":
                if state["timelogid"] > 0:
                    state = self.stop_timing(state, DB)
                else:
                    state["message1"] = "Not currently tracking."
                    state["message2"] = "Click Start to begin."
                main_window["message1"].Update(value=state["message1"])
                main_window["message2"].Update(value=state["message2"])

            elif event == "Start":
                start_window = UI.get_start_window(main_window.current_location(), DB, "")
                main_window.close()
                while True:
                    start_event, start_values = start_window.read(timeout=10)
                    if start_event == None:
                        DB.close()
                        sys.exit()
                    elif start_event == "Back":
                        main_window = UI.get_main_window(
                            start_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        start_window.close()
                        break

                    elif start_event == "Start":
                        state["client_id"] = DB.getTableItemID(
                            "".join(start_values["client_listbox"]), "client"
                        )
                        state["project_id"] = DB.getTableItemID(
                            "".join(start_values["project_listbox"]), "project"
                        )
                        state["client"] = "".join(start_values["client_listbox"])
                        state["project"] = "".join(start_values["project_listbox"])
                        if state["timelogid"] > 0:
                            self.stop_timing(state, DB)
                        # Should make sure both client and project are selected before starting
                        state = self.start_timing(state, DB)
                        main_window = UI.get_main_window(
                            start_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        start_window.close()
                        break
                    elif start_event == "New":
                        new_window = UI.get_new_window(start_window.current_location())
                        start_window.close()
                        while True:
                            new_event, new_values = new_window.read(timeout=10)
                            if new_event == None:
                                DB.close()
                                sys.exit()
                            elif new_event == "Cancel":
                                start_window = UI.get_start_window(
                                    new_window.current_location(),
                                    DB.getTableItems("client")["client_name"].tolist(),
                                    DB.getTableItems("project")["project_name"].tolist(),
                                    "",
                                )
                                new_window.close()
                                break
                            elif new_event == "Submit":
                                if new_values["new_client"] != "":
                                    if not DB.check_table_item_exists(
                                        "client", new_values["new_client"]
                                    ):
                                        DB.create_table_item(
                                            new_values["new_client"], "client"
                                        )

                                if new_values["new_project"] != "":
                                    if not DB.check_table_item_exists(
                                        "project", new_values["new_project"]
                                    ):
                                        DB.create_table_item(
                                            new_values["new_project"], "project"
                                        )

                                start_window = UI.get_start_window(
                                    new_window.current_location(),
                                    DB,
                                    "The items were successfully created.",
                                )
                                new_window.close()
                                break

        DB.close()

        return 0


    if __name__ == "__main__":
        run()
