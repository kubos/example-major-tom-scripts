import requests
import logging
import json
import datetime
from scripting_api.mutations import Mutations


logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for other exceptions"""
    pass


class ApiError(Error):
    """Raised when the GraphQL request is unparsable or other server-side errors are encountered."""

    def __init___(self, request, errors):
        super(ApiError, self).__init__(f"From server: {errors}")
        self.request = request
        self.errors = errors


class ScriptingApi:
    def __init__(self, host, token, scheme="https", port=None, basic_auth_username=None, basic_auth_password=None):
        self.host = host
        self.token = token
        self.scheme = scheme
        self.port = port
        self.basic_auth_username = basic_auth_username
        self.basic_auth_password = basic_auth_password
        self.mutations = Mutations(self)
        self.script_info = None
        self.__fetch_script_info()

    def script_id(self):
        return self.script_info['id']

    def mission_id(self):
        return self.script_info['mission']['id']

    def system(self, name, fields=[]):
        default_fields = ['id', 'name']

        graphql = """
            query SystemQuery($missionId: ID!, $name: String!) {
                system(missionId: $missionId, name: $name) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        result = self.query(graphql,
                            variables={'missionId': self.mission_id(), 'name': name},
                            path='data.system')
        if result == None:
            raise ApiError(f'No system of name "{name}" found.')
        return result

    def subsystem(self, system_name, name, fields=[]):
        default_fields = ['id', 'name']

        graphql = """
            query SubsystemQuery($missionId: ID!, $systemName: String!, $name: String!) {
                subsystem(missionId: $missionId, systemName: $systemName, name: $name) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        result = self.query(graphql,
                            variables={'missionId': self.mission_id(
                            ), 'systemName': system_name, 'name': name},
                            path='data.subsystem')
        if result == None:
            raise ApiError(f'No subsystem of name "{name}" found on system "{system_name}"')
        return result

    def metric(self, system_name, subsystem_name, name, fields=[]):
        default_fields = ['id', 'name']

        graphql = """
            query MetricQuery($missionId: ID!, $systemName: String!, $subsystemName: String!, $name: String!) {
                metric(missionId: $missionId, systemName: $systemName, subsystemName: $subsystemName, name: $name) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.query(graphql,
                          variables={'missionId': self.mission_id(), 'systemName': system_name,
                                     'subsystemName': subsystem_name, 'name': name},
                          path='data.metric')
        if result == None:
            raise ApiError(
                f'No metric "{name}" found on subsystem "{subsystem_name}" and system "{system_name}"')
        return result

    def command_definition(self, system_name, command_type, fields=[]):
        default_fields = ['id', 'displayName', 'commandType', 'fields']

        graphql = """
            query CommandDefinitionQuery($missionId: ID!, $systemName: String!, $commandType: String!) {
                commandDefinition(missionId: $missionId, systemName: $systemName, commandType: $commandType) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        result = self.query(graphql,
                            variables={'missionId': self.mission_id(), 'systemName': system_name,
                                       'commandType': command_type},
                            path='data.commandDefinition')
        if result == None:
            raise ApiError(f'No command defitinon "{command_type}" found on "{system_name}"')
        return result

    def command(self, id, fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

        graphql = """
            query CommandQuery($id: ID!) {
                command(id: $id) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        result = self.query(graphql,
                            variables={'id': id},
                            path='data.command')

        if result == None:
            raise ApiError(f'No command with id "{id}" found.')
        return result

    def commands(self, system_id, states=[], first=10, after_cursor=None, fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

        graphql = """
            query CommandsQuery($systemId: ID!, $states: [CommandState!], $first: Int!, $afterCursor: String) {
                system(id: $systemId) {
                    commands(filters: { state: $states },
                             orderBy: { sort: ID, direction: DESC },
                             first: $first,
                             after: $afterCursor) {
                        nodes {
                            %s
                        }
                        pageInfo {
                            hasNextPage, hasPreviousPage, startCursor, endCursor
                        }
                        totalCount
                    }
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.query(graphql,
                          variables={'systemId': system_id, 'states': states,
                                     'first': first, 'afterCursor': after_cursor},
                          path='data.system.commands')

    def gateway(self, name, fields=[]):
        default_fields = ['id', 'name', 'connected']

        graphql = """
            query GatewayQuery($missionId: ID!, $name: String!) {
                gateway(missionId: $missionId, name: $name) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        result = self.query(graphql,
                            variables={'missionId': self.mission_id(), 'name': name},
                            path='data.gateway')
        if result == None:
            raise ApiError(f'No gateway of name "{name}" found.')
        return result

    def events(self, system_id, levels=None, start_time=None, first=10, after_cursor=None, fields=[]):
        if levels is None:
            levels = ['debug', 'deprecated', 'nominal', 'warning', 'error', 'critical']

        if start_time is None:
            start_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

        start_time_in_epoch_millis = (
            start_time - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0

        default_fields = ['id', 'type', 'message', 'level', 'timestamp']

        graphql = """
            query EventsQuery($missionId: ID!, $systemId: [ID!], $levels: [EventLevel!], $startTime: Time!, $first: Int!, $afterCursor: String) {
                mission(id: $missionId) {
                    events(filters: { systemId: $systemId, level: $levels, startTime: $startTime },
                           orderBy: { sort: TIMESTAMP, direction: ASC },
                           first: $first,
                           after: $afterCursor) {
                        nodes {
                            %s
                        }
                        pageInfo {
                            hasNextPage, hasPreviousPage, startCursor, endCursor
                        }
                        totalCount
                    }
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.query(graphql,
                          variables={'missionId': self.mission_id(),
                                     'systemId': [system_id],
                                     'levels': levels,
                                     'first': first,
                                     'startTime': start_time_in_epoch_millis,
                                     'afterCursor': after_cursor},
                          path='data.mission.events')

    def query(self, query, variables=None, operation_name=None, path=None):
        logger.debug(query)
        if self.port == None:
            url = f"{self.scheme}://{self.host}/script_api/v1/graphql"
        else:
            url = f"{self.scheme}://{self.host}:{self.port}/script_api/v1/graphql"
        request = requests.post(url,
                                auth=(self.basic_auth_username, self.basic_auth_password),
                                headers={
                                    'X-Script-Token': self.token,
                                },
                                json={
                                    'query': query,
                                    'variables': variables,
                                    'operationName': operation_name
                                })
        request.raise_for_status()

        json_result = request.json()
        logger.debug(json.dumps(json_result, indent=2))

        if 'errors' in json_result:
            raise ApiError(request, json_result["errors"])

        if path:
            for s in path.split('.'):
                if json_result:
                    json_result = json_result.get(s)

        return json_result

    def __fetch_script_info(self):
        self.script_info = self.query("""
            query {
                agent {
                    type
                    script {
                        name, id
                        mission { name, id }
                    }
                }
            }
        """, path='data.agent.script')

        logger.info(f"Script Info: {self.script_info}")
