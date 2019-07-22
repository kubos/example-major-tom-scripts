import logging
import time
import json
import argparse
from scripting_api.scripting_api import ScriptingApi


class ScriptError(Exception):
    pass


"""
This script is designed to run through a demo pass scenario with the demo python gateway:

https://github.com/kubos/example-python-gateway

Make sure that gateway is connected to the mission before running this script.
Connecting the gateway will create all the necessary objects for the script.

For instructions on how to run it, run with the "-h" command line argument:

$ python3 demo_pass.py -h
"""


# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set up command line arguments
parser = argparse.ArgumentParser()
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
required.add_argument(
    '-m',
    '--majortomhost',
    help='Major Tom host name. Can also be an IP address for local development/on prem deployments.',
    required=True)
required.add_argument(
    '-s',
    '--scripttoken',
    help='Script Token used to authenticate the connection. Look this up in Major Tom under the script page for the script you are trying to connect.',
    required=True)
optional.add_argument(
    '-b',
    '--basicauth',
    help='Basic Authentication credentials. Not required unless BasicAuth is active on the Major Tom instance. Must be in the format "username:password".',
    required=False)

args = parser.parse_args()
if args.basicauth:
    basic_auth_username = args.basicauth.split(':')[0]
    basic_auth_password = args.basicauth.split(':')[1]
else:
    basic_auth_username = None
    basic_auth_password = None

# Connect to the API
api = ScriptingApi(host=args.majortomhost,
                   basic_auth_username=basic_auth_username,
                   basic_auth_password=basic_auth_password,
                   token=args.scripttoken)

# Retrieve Gateway and System (with current staged files)
gateway = api.gateway(name="Demo")
system = api.system(name="Space Oddity", return_fields=[
                    "stagedFiles {edges {node {id,name,downloadPath}}}"])

# Make sure a staged file is there to uplink. We're just pulling the latest one uploaded.
if len(system["stagedFiles"]["edges"]) == 0:
    raise(ScriptError("No Files to uplink."))
logger.info(f'Staged Filed to Uplink: {system["stagedFiles"]["edges"][0]["node"]["name"]}')

# Set all the commands we want to run except the final downlink_file command, as it depends on getting the refreshed file list
commands = [
    {"connect": {}},
    {"telemetry": {"fields": {"mode": "NOMINAL", "duration": 60}}},
    {"uplink_file": {"fields": {
        "gateway_download_path": system["stagedFiles"]["edges"][0]["node"]["downloadPath"]}}},
    {"update_file_list": {}}
]

# Queue all commands for the pass and store their respective command IDs
for command in commands:
    for name in command:
        command_definition = api.command_definition(
            system_name=system["name"],
            command_type=name)
        logger.info(f'Queueing Command: "{name}"')
        command[name]["queue_result"] = api.mutations.queue_command(
            system_id=system["id"],
            command_definition_id=command_definition["id"],
            gateway_id=gateway["id"],
            fields=command[name].get("fields", {}))
        command[name]["id"] = command[name]["queue_result"]["command"]["id"]
        time.sleep(1)

# If all commands successfully queue, execute them in order, waiting for each to complete
# If any command fails, it cancelled all remaining queued commands
cancel = False
for command in commands:
    for name in command:
        if cancel:
            logger.info(f'Cancelling command: "{name}"')
            api.mutations.cancel_command(id=command[name]["id"])
        else:
            logger.info(f'Executing command: "{name}"')
            api.mutations.execute_command(id=command[name]["id"])
        command[name]["state"] = None
        while command[name]["state"] not in ["completed", "failed", "cancelled"]:
            command[name]["state"] = api.command(id=command[name]["id"])["state"]
            if command[name]["state"] == "failed":
                logger.error(f'Command "{name}" failed. Cancelling all remaining commands')
                cancel = True
            time.sleep(1)

# Get the latest filename and execute the downlink file command now that the file list is updated
# Skips if commands were cancelled in the last step.
if not cancel:
    logger.info("Executing Downlink File command")

    # Make sure the downlink_file command exists
    command_definition = api.command_definition(
        system_name=system["name"],
        command_type="downlink_file")

    # Get the remoteFileList
    system = api.system(name=system["name"], return_fields=["remoteFileList {files,timestamp}"])

    # Returned as a string, so we make it into a python list of dicts and pull out the name of the latest.
    # You should analyze the timestamp to pull out the latest, but we have control of the gateway, which has it nicely ordered for us already.
    remote_file_list = json.loads(system["remoteFileList"]["files"])
    if remote_file_list == []:
        raise(ScriptError("No remote files to downlink"))
    filename_to_downlink = remote_file_list[-1]["name"]

    # Execute the command
    result = api.mutations.queue_and_execute_command(
        system_id=system["id"],
        command_definition_id=command_definition["id"],
        gateway_id=gateway["id"],
        fields={
            "filename": filename_to_downlink})["command"]

    # Ensure it executes cleanly
    state = None
    while state not in ["completed", "failed", "cancelled"]:
        state = api.command(id=result["id"])["state"]
        if state == "failed":
            logger.error(f'Command "{name}" failed.')
        time.sleep(1)

logger.info("All operations completed.")
