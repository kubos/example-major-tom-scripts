import logging
import json
import sys
import time
from majortom_scripting import ScriptingAPI

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

api = ScriptingAPI(host="app.majortom.cloud",
                   token="YOUR_SCRIPT_TOKEN")


system = api.system(name="Satellite0")

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
    print("Found no queued command")
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
