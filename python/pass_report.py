import logging
import json
import sys
import time
import datetime
from majortom_scripting import ScriptingAPI

# Note: Currently does not paginate, so if the time window is too large, it'll only grab the first page of events/commands. 

# Number of minutes in the past: 
MINUTES_FROM_NOW = 1
# Time MINUTES_FROM_NOW in the past
start_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=MINUTES_FROM_NOW)
# Report Filename
REPORT_FILENAME = "Events and Commands: " + \
    str(start_time) + " - " + str(datetime.datetime.utcnow()) + ".json"


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

api = ScriptingAPI(host="app.majortom.cloud",
                   token="adc7eb1a1ef2013647c7008ffdf5373f5a1229a21b54dd64c42f7ee68545df5b")

commands_query_graphql = """query AllCommands($missionId: ID!,$startTime:Time!) {
  mission(id:$missionId) {
    commands(filters:{startUpdatedTime:$startTime}){
      nodes {
        displayName
        system {
          name
        }
        state
        status
        fields
        id
      }
    }
  }
}
"""

events_query_graphql = """query AllEvents($missionId:ID!,$startTime:Time!) {
  mission(id:$missionId) {
    events(filters:{startTime:$startTime}){
      nodes {
        id
        type
        level
        system {
          name
        }
        gateway {
          name
        }
        script {
          name
        }
        timestamp
        createdAt
        message
        command {
          displayName
          id
        }
      }
    }
  }
}"""

# Calculate epoch in millis
start_time_in_epoch_millis = (
    start_time - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0

command_results = api.query(
    commands_query_graphql,
    variables={'missionId': api.mission_id(),
               'startTime': start_time_in_epoch_millis},
    path='data.mission.commands')

event_results = api.query(
    events_query_graphql,
    variables={'missionId': api.mission_id(),
               'startTime': start_time_in_epoch_millis},
    path='data.mission.events')

with open(REPORT_FILENAME, "w") as f:
    f.write(json.dumps({"events": event_results["nodes"]}, indent=2))
    f.write("\n")
    f.write(json.dumps({"commands": command_results["nodes"]}, indent=2))
