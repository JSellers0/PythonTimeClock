import sqlite3
import pandas as pd

class ClockDatabase:
    def __init__(self, database_location):
        self.conn = sqlite3.connect(database_location)
        self.c = self.conn.cursor()
        self.check_tables()

    def check_tables(self):
        # Create tables if they it doesn't exist
        # project
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS project (projectID INTEGER PRIMARY KEY, project_name VARCHAR NOT NULL, requires_client BOOLEAN DEFAULT 0);"
        )
        # client
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS client (clientID INTEGER PRIMARY KEY, client_name VARCHAR NOT NULL);"
        )
        # timelog
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS timelog (
            timelogid INTEGER PRIMARY KEY, 
            start TIMESTAMP NOT NULL, 
            stop TIMESTAMP, 
            projectID INTEGER NOT NULL, 
            clientid INTEGER NOT NULL,
                CONSTRAINT fk_project FOREIGN KEY(projectID) REFERENCES project(projectID), 
                CONSTRAINT fk_client FOREIGN KEY(clientID) REFERENCES client(clientID));"""
        )

        self.conn.commit()
        return 0

    def update_table_item(self, item, table):
        sql = (
            """UPDATE """
            + table
            + """ SET """
            + item["field"]
            + """ = '"""
            + str(item["value"])
            + """' WHERE """
            + table
            + """ID 
            = '"""
            + str(item["itemid"])
            + """';"""
        )
        self.c.execute(sql)
        self.conn.commit()
        return 0

    def update_timelog_row(self, row_values):
        if row_values["stop"] == "":
            sql = (
                """
            UPDATE timelog
            SET start = '"""
                + str(row_values["start"])
                + """',
                clientid = (SELECT clientID FROM client WHERE client_name = '"""
                + row_values["client_listbox"][0]
                + """'),
                projectid = (SELECT projectID FROM project WHERE project_name = '"""
                + row_values["project_listbox"][0]
                + """')
            WHERE timelogid = '"""
                + str(row_values["timelogid"])
                + """';
            """
            )
        else:
            sql = (
                """
            UPDATE timelog
            SET start = '"""
                + str(row_values["start"])
                + """',
                stop = '"""
                + str(row_values["stop"])
                + """',
                clientid = (SELECT clientID FROM client WHERE client_name = '"""
                + row_values["client_listbox"][0]
                + """'),
                projectid = (SELECT projectID FROM project WHERE project_name = '"""
                + row_values["project_listbox"][0]
                + """')
            WHERE timelogid = '"""
                + str(row_values["timelogid"])
                + """';
            """
            )

        self.c.execute(sql)
        self.conn.commit()
        return 0

    def getTableItemID(self, item, table):
        self.c.execute(
            "SELECT "
            + table
            + "id FROM "
            + table
            + " WHERE "
            + table
            + "_name = '"
            + item
            + "';"
        )
        result = self.c.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def create_table_item(self, item, table):
        if not table == "timelog":
            sql = (
                """INSERT INTO """
                + table
                + """("""
                + table
                + """_name)
                    VALUES('"""
                + item
                + """');"""
            )
        elif table == "timelog":
            if "stop" in item.keys():
                sql = (
                    """INSERT INTO timelog (start, stop, projectid, clientid)
                    VALUES 
                    ('"""
                    + item["start"]
                    + """',
                    '"""
                    + item["stop"]
                    + """',
                    '"""
                    + str(item["projectid"])
                    + """',
                    '"""
                    + str(item["clientid"])
                    + """');"""
                )
            else:
                sql = (
                    """INSERT INTO timelog (start, projectid, clientid)
                    VALUES 
                    ('"""
                    + item["start"]
                    + """',
                    '"""
                    + str(item["projectid"])
                    + """',
                    '"""
                    + str(item["clientid"])
                    + """');"""
                )
        self.c.execute(sql)
        self.conn.commit()
        return 1

    def getTableItemByID(self, item_id, table):
        if table != "timelog":
            self.c.execute(
                """SELECT """
                + table
                + """_name FROM """
                + table
                + """
                           WHERE """
                + table
                + """ID = '"""
                + str(item_id)
                + """';"""
            )
            result = self.c.fetchone()
            if result:
                return result[0]
            else:
                return 0

    def getTableItems(self, table, start_date="", end_date=""):
        if table == "timelog":
            sql = (
                """SELECT 
                     timelogid, start, stop, c.client_name, p.project_name 
                   FROM timelog tl
                     INNER JOIN client c ON c.clientID = tl.clientID
                     INNER JOIN project p ON p.projectID = tl.projectID
                   WHERE (tl.start < '"""
                + end_date
                + """' AND tl.stop >= '"""
                + start_date
                + """')
                                OR (tl.start > '"""
                + start_date
                + """' AND tl.stop IS NULL);
                   """
            )
        else:
            sql = """SELECT * FROM """ + table + """
                ORDER BY """ + table + """ID;"""

        return pd.read_sql(sql, self.conn)

    def check_table_item_exists(self, table, item):
        sql = """SELECT * FROM """ + table + """
                WHERE """ + table + """_name = '""" + item + """'"""

        self.c.execute(sql)
        res = self.c.fetchall()
        if len(res) == 0:
            return 0
        else:
            return 1

    def close(self):
        self.conn.close()
        return 0