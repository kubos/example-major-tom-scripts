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

# Queue the command
queue_result = api.mutations.queue_command(system_id=system["id"],
                                           command_definition_id=command_definition["id"],
                                           gateway_id=gateway["id"],
                                           fields={'filename': 'foo.png'})
command = queue_result["command"]
print(json.dumps(command, indent=2))

# Execute the queued command. You could also just use queue_and_execute_command to do this in one action, but we wanted
# to show how to use both mutations.
result = api.mutations.execute_command(id=command["id"])
print(json.dumps(result, indent=2))
