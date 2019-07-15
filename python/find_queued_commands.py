import logging
import json
import sys
from scripting_api.scripting_api import ScriptingApi

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

api = ScriptingApi(host="app.majortom.cloud",
                   token="YOUR_SCRIPT_TOKEN")


system = api.system(name="Satellite0")

if not system:
    print("Unable to find system Satellite0")
    sys.exit(1)

# Find the newest queued command on this system.
commands = api.commands(system_id=system["id"], first=1, states=['queued'])
if commands and len(commands["nodes"]) > 0:
    for command in commands["nodes"]:
        result = api.mutations.execute_command(id=command["id"])
        if result["success"]:
            print(json.dumps(result, indent=2))
        else:
            print(f'Error: Unable to execute command: {result["errors"]}')
else:
    print("Found no queued command")

