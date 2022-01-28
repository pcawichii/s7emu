import pytest
from ..lib.third_party_status import azure_status, powerbi_status


def test_azure():
    status = {}

    servers = ["West Europe", "North Europe"]
    services = ["Azure IoT Hub", "Azure Stream Analytics"]

    status = azure_status(servers, services)

    for i in status:
        for j in status[i]:
            assert status[i][j] == "Good"

def test_power_bi():
    status = {}
    status = powerbi_status()

    for i in status:
        assert status[i] == 'good-status' or status[i] == 'information-status'
