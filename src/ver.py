import snap7
import json
import logging
import time

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Load JSON Data
    f = open("init.json")
    data = json.load(f)

    # Open Server
    print("listening on port: {}".format(data['port']))
    # snap7.server.mainloop(tcpport=data['port'])

    server = snap7.server.Server()
    size = 300
    DBdata = (snap7.types.wordlen_to_ctypes[snap7.types.WordLen.Byte.value] *
              size)()
    server.register_area(snap7.types.srvAreaDB, 80, DBdata)

    server.start(tcpport=data['port'])
    while True:
        while True:
            event = server.pick_event()
            if event:
                logger.info(server.event_text(event))
            else:
                break
        time.sleep(1)
