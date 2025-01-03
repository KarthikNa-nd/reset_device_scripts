from tabulate import tabulate
import socket
import json
import time
import csv
import sys
import curses
import os

final_output = ""
rpi_data = {}
rpi_list = []

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
        username = dj.get("Username")
        if username:
            if rpi_list:
                if username in rpi_list:
                    rpi_data[username] = [username, dj.get("IP Address")]
            else:
                rpi_data[username] = [username, dj.get("IP Address")]

    # Close the socket
    client_socket.close()

def print_table(stdscr):
    while True:
        stdscr.clear()  # Clear the screen

        receive_broadcast()
        # Define your table here

        rpi_data_column = ["username", "ip_address"]
        rpi_data_list = rpi_data.values()

        
        rpi_data_table = tabulate(rpi_data_list, headers=rpi_data_column, tablefmt="pipe")
        final_table = str(rpi_data_table)
        stdscr.addstr(final_table)  # Print the table
        stdscr.refresh()  # Refresh the screen to show the new data

        time.sleep(0.05)  # Wait for 2 seconds

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            rpi_list = sys.argv[1].split(',')
            print(rpi_list)
            # with open(sys.argv[1]) as device_list:
            #     dl = device_list.read()
            # device_list = dl.strip().split("\n")
        curses.wrapper(print_table)
    except KeyboardInterrupt:
        print("==========================================")
        print("Username, IP Address")
        for data in rpi_data.values():
            print(f"{data[0]},{data[1]}")

        output_folder = "Output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        rpi_csv_file = os.path.join(output_folder, 'rPi.csv')

        with open(rpi_csv_file, mode='w', newline='') as file:
            rpi_writer = csv.writer(file)
            rpi_writer.writerow(["username", "ip_address"])
            for data in rpi_data.values():
                rpi_writer.writerow(data)
        