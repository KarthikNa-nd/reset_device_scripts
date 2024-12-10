# broadcast_receiver.py
 - usage: python3 broadcast_receiver {comma separated device_ids or pi ID}
 - output - device.csv and rPi.csv

# reset_device.py
 - usage: python3 reset.py {device.csv or comma separated device_ids}

# delete_shadow.py
 - usage: python3 delete_shadow.py -d {comma separated device_ids} -s|p {s for staging | p for production}
 - Do aws sso login before running
