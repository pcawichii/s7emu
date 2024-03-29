import snap7
from ctypes import c_int32, c_int, byref, c_float, c_longlong
import json
import time
from decimal import Decimal
import struct

def read():
    # Load JSON Data
    f = open("init.json")
    data = json.load(f)

    # Create Reader
    reader = snap7.client.Client()
    reader.connect(data['host'], data['rack'], data['slot'], data['port'])

    # Begin Reading
    for key in data['values']:
        print("Reading: " + key)
        # Data for measure
        i = data['values'][key]

        # Read
        read = reader.db_read(i.get('db_number'), i.get('offset'),
                              i.get('length'))
        # Display
        if(i.get("type") == "int"):
            data['values'][key]['value'] = int.from_bytes(read, byteorder='big')
        elif(i.get("type") == "float"):
            data['values'][key]['value'] = struct.unpack('>f', read)[0]



    # Return all data
    return data['values']

def set(up):
    # Load JSON Data
    f = open("init.json")
    data = json.load(f)

    # Create Writer
    writer = snap7.client.Client()
    writer.connect(data['host'], data['rack'], data['slot'], data['port'])

    # Begin Writing
    write = 0b00000000
    for key in up['values']:
        # Check for key
        if data['values'].get(key, False) == False:
            continue

        # Current Update
        print("Writing: " + key)
        i = data['values'][key]

        # Write into PLC
        # temp = int.to_bytes(int(up['values'][key].get('value')), up['values'][key].get('length'), 'big')
        # write = c_int32(int.from_bytes(temp, 'little'))
        # print(write)
        # writer.as_db_write(i.get('db_number'), i.get('offset'),
        #                     i.get('length'), write)
        temp = 0x00
        write = c_int32(0)
        if i.get('type') == 'int':
            temp = int.to_bytes(int(up['values'][key].get('value')),i.get('length'), 'big')
            write = c_int32(int.from_bytes(temp, 'little'))
        elif i.get('type') == 'float':
            temp = struct.pack('>f', float(up['values'][key].get('value')))
            write = c_int32(int.from_bytes(temp, 'little'))
        writer.as_db_write(i.get('db_number'), i.get('offset'), i.get('length'), write)

        # Wait until finished writing
        check_status = c_int(-1)
        for i in range(20):
            writer.check_as_completion(byref(check_status))
            if check_status.value == 0:
                break
            time.sleep(0.5)
        else:
            print("Writing not finished after 10s. Terminating")
            break




if __name__ == '__main__':
    f = open("example_up.json")
    data = json.load(f)

    # print(read())
    set(data)
    print(read())
