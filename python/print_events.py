import logging
import json
import sys
import time
import datetime
from scripting_api.scripting_api import ScriptingApi

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

api = ScriptingApi(host="app.majortom.cloud",
                   token="YOUR_SCRIPT_TOKEN")


system = api.system(name="Satellite0")

# Look for events starting now.
start_time = datetime.datetime.utcnow()

# Pagination uses a cursor.
next_page_cursor = None

while True:
    # NOTE: Please always wait a couple seconds between repeated queries.
    time.sleep(2)

    results = api.events(system_id=system["id"],
                         start_time=start_time,
                         after_cursor=next_page_cursor,
                         fields=['command { id }'])
    next_page_cursor = results["pageInfo"]["endCursor"] or next_page_cursor

    for event in results["nodes"]:
        print(json.dumps(event, indent=2))
