import snap7
import json

if __name__ == '__main__':
    # Load JSON Data
    f = open("init.json")
    data = json.load(f)

    # Open Server
    print("listening on port: {}".format(data['port']))
    snap7.server.mainloop(tcpport=data['port'])
