#!/usr/bin/env python3
'''
This script demonstrates working with command definitions.

The chosen satellite will have its definitions uploaded, modified, and printed.
'''
from common.script_argparser import get_parser
import random
from majortom_scripting import ModelingAPI

# ADJUST THESE PARAMETERS AS NECESSARY TO MATCH YOUR MISSION
MISSION = 6
SATELLITE_NAME = "AQUA"

def main():
    parser = get_parser()
    args = parser.parse_args()

    modeling_api = ModelingAPI(host=args.host, token=args.token, scheme=args.scheme)
    mission = modeling_api.mission(MISSION)
    sat = mission.satellite(name=SATELLITE_NAME)

    # Update all definitions
    with open('python/fixtures/commands.json') as f:
        new_defs = f.read()
    sat.update_command_definitions(new_defs)

    # Modify each definition individually
    defs = sat.command_definitions
    for definition in defs:
        definition.update_description((f"{random.randint(0,100)}: {definition.description}"))

    # View definitions
    defs = sat.command_definitions
    for definition in defs:
      print(definition)


if __name__ == "__main__":
    main()