from io import TextIOWrapper
import json


def update_init(updates):
    f = open("init.json")
    data = json.load(f)

    # perform updates to data
    data = updates

    f.write(data)


def create_init():
    f = open("test.json", "w")

    print("Now Beginning Creation of init.json")
    f.write("{")

    add_plc(f)
    add_sql(f)

    f.write("}")


def add_plc(f: TextIOWrapper):
    print("Now setting up PLC Connection")
    f.write('"plc": {')

    host = input("Please input the Host IP: ")
    port = input("Please input the port: ")
    rack = input("Please input rack: ")
    slot = input("Please input slot: ")

    f.write(f'"host": "{host}",')
    f.write(f'"port": {port},')
    f.write(f'"rack": {rack},')
    f.write(f'"slot": {slot},')

    add_measures(f)

    f.write('},')
    return


def add_measures(f: TextIOWrapper):
    print("Now writing plc values:")

    f.write('"values": {')
    measures = ""
    while True:

        id = input("Please input the id for new measure (quit to end): ")
        if(id == 'quit'):
            break
        measures += '"' + id + '": {\n'

        type = input("Is the measure a 'int' or 'float': ")
        db_number = input("Please input db_number: ")
        offset = input("Please input offset: ")
        length = input("Please input length: ")

        measures += f'"type": "{type}",\n'
        measures += f'"db_number": {db_number},\n'
        measures += f'"offset": {offset},\n'
        measures += f'"length": {length}\n'

        measures += ('},')

    f.write(measures[:-1])

    f.write('}')
    return


def add_sql(f: TextIOWrapper):
    print("Now setting up SQL Connection")
    f.write('"sql": {')

    device_id = input("Please input the Device Id: ")
    server = input("Please input the server: ")
    database = input("Please input the database: ")
    username = input("Please input username: ")
    password = input("Please input password: ")

    f.write(f'"device_id": "{device_id}",')
    f.write(f'"server": "{server}",')
    f.write(f'"database": "{database}",')
    f.write(f'"username": "{username}",')
    f.write(f'"password": "{password}"')

    f.write('}')

    return




if __name__ == '__main__':
    create_init()
