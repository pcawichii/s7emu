from .lib.sql import get_latest_message, connect_to_db
from .lib.plc import connection_to_plc, values_at_plc
from .lib.third_party_status import azure_status, powerbi_status
import time
import json
import decimal


def out():
    f = open("status/init.json")
    data = json.load(f)
    print(data)
    measurements = data['plc']['values']

    ret = {}
    ret['connected_to_plc'] = connection_to_plc() == True

    print("PLC")

    ret['plc_active'] = values_at_plc(measurements) != None

    plc_val = values_at_plc(measurements)

    print("SQL")
    ret['sql_active'] = connect_to_db(data["sql"]["server"],
                                      data["sql"]["database"],
                                      data["sql"]["username"],
                                      data["sql"]["password"])

    print("SQL Message")
    sql_res = get_latest_message(data["sql"]["device_id"],
                                 data["sql"]["server"],
                                 data["sql"]["database"],
                                 data["sql"]["username"],
                                 data["sql"]["password"], measurements.keys())

    print("Measurement PLC")
    ret['measurements_plc'] = {}
    for i in measurements:
        if plc_val[i] != None:
            ret['measurements_plc'][i] = True
        else:
            ret['measurements_plc'][i] = False

    print("Measurement SQL")
    ret['measurements_sql'] = {}
    for i in measurements:
        if sql_res[i] != None:
            ret['measurements_sql'][i] = True
        else:
            ret['measurements_sql'][i] = False

    print("Measurements Valid")
    ret['measurements_valid'] = {}
    for i in measurements:
        if plc_val[i] != None and sql_res[i] != None:
            diff = abs(decimal.Decimal(plc_val[i]) - sql_res[i])
            # diff = 0.1
            print(i)
            print(diff)

            ret['measurements_valid'][i] = diff < measurements[i].get('diff', 0.5)
        else:
            ret['measurements_valid'][i] = False

    return ret


def sel():
    ret = {}

    print("Selenium")
    status = {}
    status['powerbi'] = powerbi_status()

    servers = ["West Europe", "North Europe"]
    services = ["Azure IoT Hub", "Azure Stream Analytics"]

    status['azure'] = azure_status(servers, services)

    ret['powerbi'] = {}
    ret['azure'] = {}

    for i in status['powerbi']:
        ret['powerbi'][i] = status['powerbi'][i] == 'good-status' or status[
            'powerbi'][i] == 'information-status'

    for i in status['azure']:
        ret['azure'][i] = {}
        for j in status['azure'][i]:
            ret['azure'][i][j] = status['azure'][i][j] == "Good"

    return ret


if __name__ == '__main__':

    print(out())
    print(sel())
