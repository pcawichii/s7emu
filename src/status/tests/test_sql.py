import pytest
from ..lib.sql import get_latest_message, connect_to_db
from ..lib.plc import connection_to_plc, values_at_plc
import json
import decimal

def test_db_connection():
    f = open("init.json")
    data = json.load(f)

    assert connect_to_db(data["sql"]["server"],
                            data["sql"]["database"],
                            data["sql"]["username"],
                            data["sql"]["password"])


def test_receive_measurements():
    f = open("init.json")
    data = json.load(f)
    measurements = data["plc"]["values"]

    plc_val = values_at_plc(measurements)

    sql_res = get_latest_message(data["sql"]["device_id"],
                                 data["sql"]["server"],
                                 data["sql"]["database"],
                                 data["sql"]["username"],
                                 data["sql"]["password"], measurements.keys())



    for i in measurements:
        if sql_res[i] != None:
            assert True
        else:
            print(i +" could not be read at SQL")
            assert False


def test_measurements_end_to_end():
    f = open("init.json")
    data = json.load(f)
    measurements = data["plc"]["values"]


    plc_val = values_at_plc(measurements)

    sql_res = get_latest_message(data["sql"]["device_id"],
                                        data["sql"]["server"],
                                        data["sql"]["database"],
                                        data["sql"]["username"],
                                        data["sql"]["password"], measurements.keys())

    for i in measurements:
        if plc_val[i] != None and sql_res[i] != None:
            diff = abs(decimal.Decimal(plc_val[i]) - sql_res[i])
            assert diff < measurements[i].get('diff', 0.5)
        else:
            print(i + " is different at e2e")
            assert False
