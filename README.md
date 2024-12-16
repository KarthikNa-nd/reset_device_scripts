# broadcast_receiver.py
1. ##Usage
   ```sh
   python3 broadcast_receiver {comma separated device_ids or pi ID}
   ```
2. ##Output
   device.csv and rPi.csv

# reset_device.py
## Usage

To run the device reset script, you can use the following command-line options:

- `-d` or `--devices`: Provide a comma-separated list of devices.
- `-c` or `--csv`: Provide a CSV file with device information.
- `-s` or `--save`: Save the output to an Excel file.

### Examples

1. **Using a comma-separated list of devices:**

    ```sh
    python reset.py -d device1,device2,device3
    ```

2. **Using a CSV file with device information:**

    ```sh
    python reset.py -c devices.csv
    ```

3. **Using a CSV file and saving the output to an Excel file:**

    ```sh
    python reset.py -c devices.csv -s
    ```

4. **Using a comma-separated list of devices and saving the output to an Excel file:**

    ```sh
    python reset.py -d device1,device2,device3 -s
    ```

# delete_shadow.py
##Usage
- `-d` or `--devices`: Provide a comma-separated list of devices.
- `-s`: for staging
- `-p`: for production
```sh
  python3 delete_shadow.py -d {comma separated device_ids} -s|p {s for staging | p for production}
```
 **Do aws sso login before running**
