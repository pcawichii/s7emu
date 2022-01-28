import pytest
from ..lib.plc import connection_to_plc, values_at_plc
import time
import json

def test_connected_to_plc():
    assert connection_to_plc() == True


def test_receive_measurements():
    f = open("init.json")
    data = json.load(f)
    measurements = data["plc"]["values"]

    plc_val = values_at_plc(measurements)

    for i in measurements:
        if plc_val[i] != None:
            assert True
        else:
            print(i + " could not be read at PLC")
            assert False


def test_measurements_are_active():
    f = open("init.json")
    data = json.load(f)
    measurements = data['plc']['values']

    assert values_at_plc(measurements) != None
