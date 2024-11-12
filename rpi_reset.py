import subprocess
import paramiko
import time
import csv
import sys
import re

def message_format(key, value):
    mas_len = 30
    space = " "*(mas_len-len(key)-4)
    return f"{key}{space}:{value}"

class Rpi:
    def __init__(self,piID,ip):
        self.piID = piID
        self.ip = ip
        self.password = "NetraDyne@123"

class SSHSession:
    def __init__(self, ip, username):
        self.rpi = Rpi(username, ip)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {self.rpi.piID} at {self.rpi.ip}")
        self.client.connect(self.rpi.ip,22,username=username, password=self.rpi.password)

    def execute_command(self, command, timeout=20):
        stdin, stdout, stderr = self.client.exec_command(command,timeout=timeout)
        return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")
    
    def get_relay_id(self):
        command = "lsusb -v 2>/dev/null | grep iSerial | grep 3 | awk '{print $3}'"
        stdout, stderr = self.execute_command(command)
        output = stdout.strip()
        relays = output.split("\n")
        if len(relays) == 0:
            print(f"Relay ID not found for {self.rpi.piID}")
        return relays
    
    def run_relay_curls(self,relays):
        if len(relays) == 0:
            return False
        
        if len(relays) == 1:
            print(f"Relay ID for {self.rpi.piID} is {relays[0]}")
            for i in range(8):
                command = f"curl \"{self.rpi.ip}:8081/Relay?{i}=on\""
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                print(f"Relay {i} of RelayID {relays[0]} ON")
        
        if len(relays) > 1:
            print(f"Multiple Relay IDs found for {self.rpi.piID}")
            for relay in relays:
                print(f"Relay ID: {relay}")
                for i in range(8):
                    command = f"curl \"http://{self.rpi.ip}:8081/Relay?id={relay}&{i}=on\""
                    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = p.communicate()
                    print(f"Relay {i} of RelayID {relay} ON")
        
        

if __name__ == "__main__":
    # rpi_to_reset = sys.argv[2].split(",")
    with open(sys.argv[1]) as file:
        rpi_data = csv.DictReader(file)
        for rpi in rpi_data:
            ssh = SSHSession(rpi["ip_address"], rpi["username"])
            relay_id = ssh.get_relay_id()
            ssh.run_relay_curls(relay_id)
            ssh.client.close()
