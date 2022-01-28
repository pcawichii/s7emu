# This is a connection between the southbound file
# and a successful response from the plc
import snap7
from snap7.exceptions import Snap7Exception
import json
import struct

def values_at_plc(loc):
    # Load JSON Data
    f = open("status/init.json")
    data = json.load(f)

    out = {}

    # Create Reader
    reader = snap7.client.Client()
    try:
        reader.connect(data['plc']['host'], data['plc']['rack'],
                    data['plc']['slot'], data['plc']['port'])

    except:
        print("Died at reader")
        return None

    for i in loc:
        read = reader.db_read(loc[i]["db_number"], loc[i]["offset"], loc[i]["length"])
        try:
            if(loc[i].get("type") == "int"):
                out[i] = int.from_bytes(read, byteorder='big')
            elif(loc[i].get("type") == "float"):
                out[i] = struct.unpack('>f', read)[0]

        except:
            print("Died at " + i)
            out[i] = None

    return out



def connection_to_plc():
    # Load JSON Data
    f = open("status/init.json")
    data = json.load(f)

    try:
        client = snap7.client.Client()
        client.connect(data['plc']['host'], data['plc']['rack'], data['plc']['slot'], data['plc']['port'])

        success = client.get_connected()
    except Snap7Exception:
        return False
    return success

if __name__ == '__main__':
    print(connection_to_plc())
