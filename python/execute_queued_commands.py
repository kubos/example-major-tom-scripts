#!/usr/bin/env python3
'''
This script finds and executes queued commands on a particular satellite. 

Queued commands are different from scheduled commands -- while both are
pre-populated with field arguments, queued commands require an additional manual
step to send, whereas scheduled commands will execute automatically during a
pass.

You will need an active Gateway to complete this script, as it will wait for the
command to be successfully delivered before finishing.
'''
import logging
import json
import sys
import time
from majortom_scripting import ScriptingAPI
from common.script_argparser import get_parser

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ADJUST THESE PARAMETERS AS NECESSARY TO MATCH YOUR MISSION
SATELLITE_NAME = "AQUA"

def main():
    parser = get_parser()
    args = parser.parse_args()
    api = ScriptingAPI(host=args.host,
                       token=args.token,
                       scheme=args.scheme)

    system = api.system(name=SATELLITE_NAME)

    # Find the newest queued command on this system.
    commands = api.commands(system_id=system["id"], first=1, states=['queued'])

    # Execute the returned command.
    command = None
    if commands and len(commands["nodes"]) > 0:
        for command in commands["nodes"]:
            result = api.mutations.execute_command(id=command["id"])
            if result["success"]:
                command = result["command"]
                print(json.dumps(result, indent=2))
            else:
                print(f'Error: Unable to execute command: {result["errors"]}')
                sys.exit(1)
    else:
        print("Found no queued commands")
        sys.exit(1)

    # Wait for the executed command to finish running.
    last_state = None
    last_status = None
    while command["state"] not in ['cancelled', 'completed', 'failed']:
        # NOTE: Please always wait a couple seconds between repeated queries.
        time.sleep(2)

        print('.', end='', flush=True)

        # Refresh the command data.
        command = api.command(id=command["id"], return_fields=[
                            'status', 'output', 'payload', 'remoteErrors'])

        if command["state"] != last_state:
            last_state = command["state"]
            print(f'\nNew state: {command["state"]}')

        if command.get("status") != last_status:
            last_status = command["status"]
            print(f'\nNew status: {command["status"]}')

    print("Command has finished:")
    print(json.dumps(command, indent=2))

if __name__ == "__main__":
    main()