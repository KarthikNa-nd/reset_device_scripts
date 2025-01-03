from tabulate import tabulate
import curses
import socket
import sys
import json
import time
import csv
import os

final_output = ""
device_data = {}
rpi_data = {}
device_list = []

def receive_broadcast():
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to all interfaces and the port used for broadcasting
    client_socket.bind(('', 12345))  # Use the same port as the server
        # Receive data
    data, address = client_socket.recvfrom(1024)
    d = data.decode()

    if "{" in d:
        dj = json.loads(d)
        device_id = dj.get("deviceId")
        username = dj.get("Username")
        rpi_name = dj.get("raspberryPiId")
        if device_id:
            if device_list:
                if (device_id in device_list) or (rpi_name in device_list):
                    device_data[device_id] = [
                        device_id,address[0],dj.get("raspberryPiId"),dj.get("relayId")
                    ]
            else:
                device_data[device_id] = [
                    device_id,address[0],dj.get("raspberryPiId"),dj.get("relayId")
                ]
        if username:
            rpi_data[username] = [username, dj.get("IP Address")]

    # Close the socket
    client_socket.close()

def print_table(stdscr):
    while True:
        stdscr.clear()  # Clear the screen

        receive_broadcast()
        # Define your table here

        device_data_column = ["device_id", "ip_address", "username", "RelayID"]
        device_data_list = device_data.values()

        rpi_data_column = ["username", "ip_address"]
        rpi_data_list = rpi_data.values()

        device_data_table = tabulate(device_data_list, headers=device_data_column, tablefmt="pipe")
        rpi_data_table = tabulate(rpi_data_list, headers=rpi_data_column, tablefmt="pipe")
        final_report = device_data_table + "\n\n\n" + rpi_data_table
        stdscr.addstr(final_report)  # Print the table
        stdscr.refresh()  # Refresh the screen to show the new data

        time.sleep(0.05)  # Wait for 2 seconds

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            device_list = sys.argv[1].split(',')
            print(device_list)
            # with open(sys.argv[1]) as device_list:
            #     dl = device_list.read()
            # device_list = dl.strip().split("\n")
        curses.wrapper(print_table)

    except KeyboardInterrupt:
        print("==========================================")
        print("device_id,ip_address,username,RelayID")
        for data in device_data.values():
            print(f"{data[0]},{data[1]},{data[2]},{data[3]}")

        output_folder = "Output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        csv_file = os.path.join(output_folder, 'device.csv')

        with open(csv_file, mode='w', newline='') as file:
            device_writer = csv.writer(file)
            device_writer.writerow(["device_id", "ip_address", "username", "RelayID"])
            for data in device_data.values():
                device_writer.writerow(data)

        rpi_csv_file = os.path.join(output_folder, 'rPi.csv')

        with open(rpi_csv_file, mode='w', newline='') as file:
            rpi_writer = csv.writer(file)
            rpi_writer.writerow(["username", "ip_address"])
            for data in rpi_data.values():
                rpi_writer.writerow(data)