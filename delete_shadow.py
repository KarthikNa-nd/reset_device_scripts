import boto3
import argparse
import os
import json
import requests

def login_api():
    try:
        status=False
        session_key=''
        access_token=''
        cmd1 = "curl --location --request POST 'https://auth-staging.netradyne.com/authserver/api/v1/oauth/token' --header 'Content-Type:application/x-www-form-urlencoded' --data-urlencode 'client_id=idms' --data-urlencode 'grant_type=password' --data-urlencode 'username=device-test-automation' --data-urlencode 'password=devicetestautomation'"
        login_response = os.popen(cmd1).read()
        login_response = json.loads(login_response)
        print(login_response)
        access_token = login_response["access_token"]
        cmd2 = "curl --location --request POST 'https://auth-staging.netradyne.com/authserver/api/v1/session' --header 'Authorization: bearer "+access_token+"'"
        session_response1 = os.popen(cmd2).read()
        session_response = json.loads(session_response1)
        session_key = session_response['session']['session_id']
        if session_key != ' ':
            status=True
    except Exception as e:
        print(f"Error in login_api: {e}")
    finally:
        return session_key,status,access_token

def keep_alive_ping(device_id,session_key,access_token,ping_command):
    test_status = "Pass"
    if session_key and access_token:
        status = True
    try: 
        if status:  
            url = f"https://idms-staging.netradyne.com/restserver/api/v1/devices/{device_id}/ping"  
            headers = {  
                "session-key": session_key,  
                "Content-Type": "application/json",  
                "Authorization": f"Bearer {access_token}"  
            }  
            data = {  
                "deviceId": device_id,  
                "userId": "8430",  
                "commands": [f"{ping_command}"]  
            }  
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_content = response.json()
            print(f"{device_id} - {ping_command} - {response_content}") 
            if response.status_code == 200 and response_content["data"]["status"] == 0:    
                response_status = True  
            else:  
                raise Exception(f"Ping {ping_command} api call response is not received")  
        else:  
            raise Exception("session key is not generated")  
    except Exception as e:  
        print(f"Error in ops_data_api: {e}") 
        test_status = "Fail"  
    finally:  
        return test_status, response_status

def delete_shadow(thing_name, region_name='us-west-2'):
    """
    Deletes the Classic Shadow of the given IoT thing (device).
    
    :param thing_name: The name of the IoT thing whose shadow should be deleted
    :param region_name: AWS region in which the IoT device resides
    :return: Response metadata indicating the result of the deletion
    """
    print(thing_name)
    test_status = "Pass"
    try:
        # Initialize the AWS IoT Data client within the function
        client = boto3.client('iot-data', region_name=region_name)

        # Delete the Classic Shadow for the specified thing
        response = client.delete_thing_shadow(
            thingName=thing_name
        )
        # print(f"Response: {response}")

        # Check if the deletion was successful based on the HTTP status code
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"Successfully deleted shadow for thing: {thing_name}")
        else:
            print(f"Failed to delete shadow for thing: {thing_name}")
            test_status = "Fail"

        # Return the response metadata
        return test_status

    except Exception as e:
        print(f"An error occurred while deleting the shadow for thing: {thing_name}")
        print(f"Error: {e}")
        return "Fail"
    
def check_shadow(thing_name, region_name='us-west-2'):
    """
    Checks if the Classic Shadow of the given IoT thing (device) exists.
    
    :param thing_name: The name of the IoT thing whose shadow should be checked
    :param region_name: AWS region in which the IoT device resides
    :return: True if the shadow exists, False otherwise
    """
    print(thing_name)
    try:
        # Initialize the AWS IoT Data client within the function
        client = boto3.client('iot-data', region_name=region_name)

        # Get the Classic Shadow for the specified thing
        response = client.get_thing_shadow(
            thingName=thing_name
        )
        print(f"Shadow exists for thing: {thing_name}")
        return True

    except client.exceptions.ResourceNotFoundException:
        print(f"No shadow found for thing: {thing_name}")
        return False

    except Exception as e:
        print(f"An error occurred while checking the shadow for thing: {thing_name}")
        print(f"Error: {e}")
        return False
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete IoT thing shadows.')
    parser.add_argument('-d', '--things', type=str, required=True, help='Comma-separated list of thing names')
    parser.add_argument('-s', '--staging', action='store_true', help='Flag to indicate if the things are in the staging environment')
    parser.add_argument('-p', '--production', action='store_true', help='Flag to indicate if the things are in the production environment')


    args = parser.parse_args()
    thing_names = args.things.split(',')
    session_key,status,access_token = login_api()

    for thing_name in thing_names:
        print("====================================================================")
        print(f"Device ID: {thing_name}")
        print("--------------------------------------------------------------------")

        if args.staging:
            delete_shadow(f"staging-{thing_name}")
        elif args.production:
            delete_shadow(f"production-{thing_name}")
        else:
            print("Please specify the environment of the things to delete")
        keep_alive_ping(thing_name,session_key,access_token,"keep-alive")
        if args.staging:
            check_shadow(f"staging-{thing_name}")
        elif args.production:
            check_shadow(f"production-{thing_name}")
        else:
            print("Please specify the environment of the things to delete")
        keep_alive_ping(thing_name,session_key,access_token,"reboot-phone")

        print("\n")
    