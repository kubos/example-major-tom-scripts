#!/usr/bin/env python3
'''
This script shows the recent events for a particular satellite.
'''
import logging
import json
import time
import datetime
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

    # Look for events starting yesterday.
    start_time = (datetime.datetime.today() - datetime.timedelta(days = 1))

    # Pagination uses a cursor.
    next_page_cursor = None

    results = api.events(system_id=system["id"],
                        start_time=start_time,
                        after_cursor=next_page_cursor,
                        return_fields=['command { id }'])
    next_page_cursor = results["pageInfo"]["endCursor"] or next_page_cursor

    for event in results["nodes"]:
        print(json.dumps(event, indent=2))

if __name__ == "__main__":
    main()