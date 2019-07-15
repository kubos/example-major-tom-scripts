import logging
import json
import sys
from scripting_api.scripting_api import ScriptingApi

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

api = ScriptingApi(host="app.majortom.cloud",
                   token="YOUR_SCRIPT_TOKEN")

gateway = api.gateway(name="Gateway0")
system = api.system(name="Satellite0")
command_definition = api.command_definition(system_name="Satellite0", command_type="downlink_file")

command = None
# Queue the command
if gateway and system and command_definition:
    queue_result = api.mutations.queue_command(system_id=system["id"],
                                               command_definition_id=command_definition["id"],
                                               gateway_id=gateway["id"],
                                               fields={'filename': 'foo.png'})

    if queue_result["success"]:
        command = queue_result["command"]

        print(json.dumps(command, indent=2))
    else:
        print(f'Error: Unable to queue command: {queue_result["errors"]}')
        sys.exit(1)
else:
    print('Error: Unable to find required gateway, system, or command_definition')
    sys.exit(1)


# Execute the queued command. You could also just use queue_and_execute_command to do this in one action, but we wanted
# to show how to use both mutations.
result = api.mutations.execute_command(id=command["id"])
if result["success"]:
    print(json.dumps(result, indent=2))
else:
    print(f'Error: Unable to execute command: {result["errors"]}')

