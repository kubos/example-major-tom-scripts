#!/usr/bin/env python3
'''
This script executes a 'downlink_file" command on the chosen spacecraft and gateway.
'''
import logging
import json
from majortom_scripting import ScriptingAPI
from common.script_argparser import get_parser

GATEWAY_NAME="Gateway0"
SATELLITE_NAME= "Satellite0"

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    parser = get_parser()
    args = parser.parse_args()
    api = ScriptingAPI(host=args.host,
                       token=args.token,
                       scheme=args.scheme)

    gateway = api.gateway(name=GATEWAY_NAME)
    system = api.system(name=SATELLITE_NAME)
    command_definition = api.command_definition(system_name=SATELLITE_NAME, command_type="downlink_file")

    # Queue the command
    queue_result = api.mutations.queue_command(system_id=system["id"],
                                            command_definition_id=command_definition["id"],
                                            gateway_id=gateway["id"],
                                            return_fields={'filename': 'foo.png'})
    command = queue_result["command"]
    print(json.dumps(command, indent=2))

    # Execute the queued command. You could also just use queue_and_execute_command to do this in one action, but we wanted
    # to show how to use both mutations.
    result = api.mutations.execute_command(id=command["id"])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()