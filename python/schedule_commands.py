#!/usr/bin/env python3
'''
This script demonstrates how to schedule a command.

The chosen satellite will have its chosen command scheduled on the next available pass.
'''
from common.script_argparser import get_parser
from majortom_scripting import ModelingAPI

# ADJUST THESE PARAMETERS AS NECESSARY TO MATCH YOUR MISSION
SATELLITE_NAME = "AQUA"
COMMAND_TO_SCHEDULE = "ping"

def main():
    parser = get_parser()
    args = parser.parse_args()

    api = ModelingAPI(host=args.host, token=args.token, scheme=args.scheme)

    AQUA = api.satellite(name=SATELLITE_NAME)                # Get the satellite
    aPass = AQUA.next_pass(scheduled=False)                  # Get the next available, unscheduled pass
   
    current_commands = aPass.get_scheduled_commands()        # Get the currently-scheduled commands for a pass   
    for command in current_commands:
        print(f"Unscheduling {command.commandType} from Pass #{aPass.id}")
        aPass.unschedule_command(command)                    # Unschedule them all
   
    command_def = AQUA.get_command_definition(COMMAND_TO_SCHEDULE)  # Get a specific command definition
    print(f"Scheduling {command_def.displayName} on Pass #{aPass.id}")
    aPass.schedule_command(command_def)                      # Schedule it on the next pass


if __name__ == "__main__":
    main()