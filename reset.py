import subprocess
import paramiko
import time
import re
from datetime import datetime as dt

def message_format(key, value):
    mas_len = 30
    space = " "*(mas_len-len(key)-4)
    return f"{key}{space}:{value}"

class Config:
    def __init__(self, product_line = "BGR"):
        self.product_line = product_line
        self.username = "root"
        self.password = "EKM2800123Netra"
        self.bagheera_override = "/home/ubuntu/config/bagheera_override.ini"
        self.sam_config = "/home/ubuntu/.nddevice/latest/sam_config.ini"
        if product_line in "KRT":
            self.password = "EKM2020123Krait"
            self.bagheera_override = "/data/nd_files/config/bagheera_override.ini"

class SSHSession:
    def __init__(self, host, port=22, username="", password=""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {self.host}:{self.port} as {self.username}")
        self.client.connect(self.host, self.port, self.username, self.password)

    def execute_command(self, command, timeout=20):
        stdin, stdout, stderr = self.client.exec_command(command,timeout=timeout)
        return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")

    def upload_file(self, local_file_path, remote_file_path):
        # ftp = self.client.open_sftp()
        # ftp.put(local_file_path, remote_file_path)
        command = f"sshpass -p {self.password} scp {local_file_path} {self.username}@{self.host}:{remote_file_path}"
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if "Host key verification failed." in stderr.decode():
            print("Host key verification failed.")
        self.execute_command("sync")
        time.sleep(0.5)
        # ftp.close()

    def download_file(self, remote_file_path, local_file_path):
        ftp = self.client.open_sftp()
        ftp.get(remote_file_path, local_file_path)
        ftp.close()

    def __del__(self):
        self.client.close()

class Setup:
    def __init__(self, ssh: SSHSession, config:Config):
        self.ssh: SSHSession = ssh
        self.config: Config  = config

    def setup_sam_config(self):
        self.ssh.upload_file("configs/sam_config.ini" ,self.config.sam_config)
        output, err = self.ssh.execute_command(f"md5sum {self.config.sam_config}")
        remote_output_md5sum = re.search(r"([a-f0-9]{32})", output)
        local_output = subprocess.run(["md5sum", "configs/sam_config.ini"], stdout=subprocess.PIPE ).stdout.decode("utf-8")
        local_output_md5sum = re.search(r"([a-f0-9]{32})", local_output)
        if (remote_output_md5sum.group(1) == local_output_md5sum.group(1)):
            print(message_format("sam_config.ini", "PASS"))
        else:
            print(err)
            print(message_format("sam_config.ini", "FAIL"))

    def setup_conn_mgr_config(self):
        self.ssh.upload_file("configs/conn_mgr_config.txt" ,"/home/ubuntu/config/conn_mgr_config.txt")
        output, err = self.ssh.execute_command("cat /home/ubuntu/config/conn_mgr_config.txt")
        if ("SPRINT" in output) and ("internet.curiosity.sprint.com" in output):
            print(message_format("conn_mgr_config.txt", "PASS"))
        else:
            print(message_format("conn_mgr_config.txt", "FAIL"))

    def setup_bagheera_override(self):
        self.ssh.upload_file("configs/bagheera_override.ini", self.config.bagheera_override)
        output, err = self.ssh.execute_command(f"md5sum {self.config.bagheera_override}")
        remote_output_md5sum = re.search(r"([a-f0-9]{32})", output)
        local_output = subprocess.run(["md5sum", "configs/bagheera_override.ini"], stdout=subprocess.PIPE ).stdout.decode("utf-8")
        local_outpu_md5sum = re.search(r"([a-f0-9]{32})", local_output)
        try:
            if remote_output_md5sum.group(1) == local_outpu_md5sum.group(1):
                print(message_format("bagheera_override.ini", "PASS"))
            else:
                print(message_format("bagheera_override.ini", "FAIL"))
        except Exception as e:
            print(e)
            print(message_format("bagheera_override.ini", "FAIL"))
    
    def check_logs_vod_obs(self):
        if self.config.product_line == "KRT":
            vod_command = "sqlite3 /home/ubuntu/.nddevice/db/uploader.db 'select * from uploader_vod' |wc -l"
        else:
            vod_command = "sqlite3 /home/ubuntu/.nddevice/uploader.db 'select * from uploader_vod' |wc -l"
        output, err = self.ssh.execute_command(vod_command)
        print(message_format("VOD upload remaining", output.strip()))

        critical_archive_log_command = "ls /home/ubuntu/.nddevice/log/archive/critical/ | wc -l"
        output, err = self.ssh.execute_command(critical_archive_log_command)
        print(message_format("Critical Archive Log", output.strip()))

        critical_vod_command = "ls /home/ubuntu/.nddevice/observations/ | wc -l"
        output, err = self.ssh.execute_command(critical_vod_command)
        print(message_format("Obs upload remaining", output.strip()))


    def setup_certificates(self):
        # overall_status = False
        # certificate_checks = {
        #     "private.pem.key": False,
        #     "certificate.pem.crt": False,
        #     "ed25519key.pem": False,
        #     "pub-ed25519.pem": False
        # }
        max_len = 30

        output, err = self.ssh.execute_command("cp /home/ubuntu/.nddevice/certificate/backup/cacert.pem /home/ubuntu/.nddevice/certificate/cacert.pem")
        output, err = self.ssh.execute_command("rm /home/ubuntu/.nddevice/certificate/temp.txt")
        output, err = self.ssh.execute_command("rm /home/ubuntu/.nddevice/certificate/private.pem.key")
        output, err = self.ssh.execute_command("rm /home/ubuntu/.nddevice/certificate/certificate.pem.crt")
        output, err = self.ssh.execute_command("rm /home/ubuntu/.nddevice/certificate/ed25519key.pem")
        output, err = self.ssh.execute_command("rm /home/ubuntu/.nddevice/certificate/pub-ed25519.pem")
        output, err = self.ssh.execute_command("sync")
        time.sleep(0.5)
        output, err = self.ssh.execute_command("systemctl restart awsiot")
        time.sleep(20)
        output,err =  self.ssh.execute_command("ls /home/ubuntu/.nddevice/certificate/private.pem.key")
        if err != "":
            print(message_format("private.pem.key", "FAIL"))
        else:
            print(message_format("private.pem.key", "PASS"))
        output,err =  self.ssh.execute_command("ls /home/ubuntu/.nddevice/certificate/certificate.pem.crt")
        if err != "":
            print(message_format("certificate.pem.crt", "FAIL"))
        else:
            print(message_format("certificate.pem.crt", "PASS"))
        output,err =  self.ssh.execute_command("ls /home/ubuntu/.nddevice/certificate/ed25519key.pem")
        if err != "":
            print(message_format("ed25519key", "FAIL"))
        else:
            print(message_format("ed25519key", "PASS"))
        output,err =  self.ssh.execute_command("ls /home/ubuntu/.nddevice/certificate/pub-ed25519.pem")
        if err != "":
            print(message_format("pub-ed25519.pem", "FAIL"))
        else:
            print(message_format("pub-ed25519.pem", "PASS"))


    def setup_services(self):
        active_service_list =  [
            "wifi_mgr",
            "uploader",
            "time_sync",
            "svc",
            "speed",
            "service_mon",
            "scheduler_manager",
            "power_monitor",
            "nd_dta",
            "nd_bt",
            "installer_app",
            "HealthStatsManager",
            "diagnostic",
            "conn_mgr",
            "circular_buffer",
            "cam_rec",
            "bagheera",
            "unifiedAnalyticsClient",
            "outwardAnalyticsClient",
            "audioPlayback",
            "analytics*",
            "awsiot",
            "obd",
        ]
        if self.config.product_line == "KRT":
            active_service_list.remove("cam_rec")
        deactive_service_list = [
            "nd_sam",
            "ext_cam",
        ]
        max_len = 30
        for service in active_service_list:
            output, err = self.ssh.execute_command(f"systemctl status {service}")
            if "active (running)" in output:
                print(message_format(service, "PASS"))
            else:
                print(message_format(service, "FAIL"))
        for service in deactive_service_list:
            output, err = self.ssh.execute_command(f"systemctl status {service}")
            if "inactive (dead)" in output:
                print(message_format(service, "PASS"))
            else:
                print(message_format(service, "FAIL"))

    def device_date_check(self):
        output, err = self.ssh.execute_command("date")
        print(message_format("Device Date", output.strip()))
        p = subprocess.Popen("date -u", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        print(message_format("UTC Date", stdout.decode().strip()))
        device_date = dt.strptime(output.strip(), "%a %b %d %H:%M:%S %Z %Y")
        utc_date = dt.strptime(stdout.decode().strip(), "%A %d %B %Y %I:%M:%S %p %Z")

        if device_date == utc_date:
            print(message_format("Date Check", "PASS"))
        else:
            if(self.config.product_line == "KRT"):
                utc_date_str = utc_date.strftime("%d %b %Y %H:%M:%S").upper()
                _,err = self.ssh.execute_command(f"date -s '{utc_date_str}';hwclock -w;hwclock")
            else:
                utc_date_str = utc_date.strftime("%m/%d/%Y %H:%M:%S")
                _,err = self.ssh.execute_command(f"sudo hwclock --set --date \"{utc_date_str}\" -f /dev/rtc;sudo hwclock --hctosys -f /dev/rtc;sudo hwclock -r")
            
            if err != "":
                print(message_format("Date Check", "FAIL"))
            else:
                print(message_format("Date Check", "Synced with UTC"))

    def get_device_version(self):
        output,err = self.ssh.execute_command("cat /home/ubuntu/.nddevice/nddevice.ini | grep nddevice | head -n 1 | awk -F'= ' {'print $2'}")
        return output
    
    def get_lumia_id(self):
        if self.config.product_line == "KRT":
            output,err = self.ssh.execute_command("echo 'EKM2020123Krait' | lte_gps_test 'ATi' | grep 'Model' | awk -F': ' {'print $2'}")
        else:
            output,err = self.ssh.execute_command("echo 'EKM2800123Netra' | sudo lte_gps_test 'ATi' | grep 'Model' | awk -F': ' {'print $2'}")
        return output

    def reboot(self):
        try:
            if self.config.product_line == "KRT":
                self.ssh.execute_command("echo 'msp qcs_reboot' | cli_mgr", timeout=10)
            elif self.config.product_line == "BGR":
                self.ssh.execute_command("reboot", timeout=10)
        except:
            pass

if __name__ == "__main__":
    import csv
    import sys

    rPi_set = set()

    with open(sys.argv[1]) as file:
        device_data = csv.DictReader(file)
        for device in device_data:
            if len(sys.argv) == 3:
                if device.get("device_id") != sys.argv[2]:
                    continue
            device_id = str(device.get("device_id"))
            ip_address = str(device.get("ip_address"))
            rPi_set.add(str(device.get("username")))
            product_line = "BGR"
            if device_id.startswith("264"):
                product_line = "KRT"
            if device_id.startswith("66"):
                product_line = "KRT"
            config = Config(product_line)
            username = config.username
            password = config.password
            print(f"Device ID: {device_id}, IP Address: {ip_address}, Product Line: {product_line}") 
            print("--------------------------------------------------------------------")
            ssh = SSHSession(ip_address, 22, username, password)
            setup = Setup(ssh, config)
            device_version = setup.get_device_version()
            print(f"Device Version: {device_version}")
            # lumia_id = setup.get_lumia_id()
            # print(f"Lumia ID: {lumia_id}")

            setup.device_date_check()
            setup.check_logs_vod_obs()
            setup.setup_sam_config()
            setup.setup_conn_mgr_config()
            setup.setup_bagheera_override()
            # setup.setup_certificates()
            setup.setup_services()
            setup.reboot()
            print("====================================================================")