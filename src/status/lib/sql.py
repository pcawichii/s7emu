import pyodbc
import datetime

def connect_to_db(server, database, username, password):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server + ';DATABASE=' + database + ';UID=' +
                          username + ';PWD=' + password)
    cursor = cnxn.cursor()

    cursor.execute(
        f"SELECT 1")

    row = cursor.fetchone()
    return row[0] == 1


def get_latest_message(device_name, server, database, username, password, measures):
    # Some other example server values are

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()


    cursor.execute(
        f"SELECT [name], [timestamp], [value] FROM [dbo].[telemetry] \
        INNER JOIN (SELECT MAX(telemetryid) as id FROM [dbo].[telemetry] WHERE uuid = '{device_name}' GROUP BY [name]) as t \
        ON t.id = telemetryid"
        )


    row = cursor.fetchone()

    out = {}
    for i in measures:
        out[i] = None


    while row:
        print(row[0])
        diff = datetime.datetime.utcnow() - row[1]
        if diff > datetime.timedelta(minutes=5):
            print("Late")
            row = cursor.fetchone()
            continue

        out[row[0]] = row[2]

        row = cursor.fetchone()

    return out
