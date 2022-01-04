import snap7
from ctypes import c_char_p, c_int32
import ctypes
import json
import time

if __name__ == '__main__':

    # Load JSON Data
    f = open("init.json")
    data = json.load(f)

    # Create Reader
    reader = snap7.client.Client()
    reader.connect(data['host'], data['rack'], data['slot'], data['port'])

    # Create Writer
    writer = snap7.client.Client()
    writer.connect(data['host'], data['rack'], data['slot'], data['port'])

    # Begin Writing
    temp = 0
    for key in data['values']:
        print("Writing: " + key)
        i = data['values'][key]

        temp = int.to_bytes(i.get('value'), 4 , 'big' )
        write = c_int32(int.from_bytes(temp, 'little'))
        print(temp)
        writer.as_db_write(i.get('db_number'), i.get('offset'), i.get('length'), write)
        # Wait to finish writing
        time.sleep(3)


    # Begin Reading
    for key in data['values']:
        print("Reading: " + key)
        i = data['values'][key]

        read = reader.db_read(i.get('db_number'), i.get('offset'), i.get('length'))
        print(read)
    print("Done")
