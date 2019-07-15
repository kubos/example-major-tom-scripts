import requests
import logging
import json
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
    def __init__(self, host, token, scheme="https", port="80", basic_auth_username=None, basic_auth_password=None):
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

        return self.query(graphql,
                          variables={'missionId': self.mission_id(), 'name': name},
                          path='data.system')

    def subsystem(self, system_name, name, fields=[]):
        default_fields = ['id', 'name']

        graphql = """
            query SubsystemQuery($missionId: ID!, $systemName: String!, $name: String!) {
                subsystem(missionId: $missionId, systemName: $systemName, name: $name) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.query(graphql,
                          variables={'missionId': self.mission_id(), 'systemName': system_name, 'name': name},
                          path='data.subsystem')

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
                          variables={'missionId': self.mission_id(), 'systemName': system_name, 'subsystemName': subsystem_name, 'name': name},
                          path='data.metric')

    def command_definition(self, system_name, command_type, fields=[]):
        default_fields = ['id', 'displayName', 'commandType', 'fields']

        graphql = """
            query CommandDefinitionQuery($missionId: ID!, $systemName: String!, $commandType: String!) {
                commandDefinition(missionId: $missionId, systemName: $systemName, commandType: $commandType) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.query(graphql,
                          variables={'missionId': self.mission_id(), 'systemName': system_name, 'commandType': command_type},
                          path='data.commandDefinition')

    def command(self, id, fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

        graphql = """
            query CommandQuery($id: ID!) {
                command(id: $id) {
                    %s
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.query(graphql,
                          variables={'id': id},
                          path='data.command')

    def commands(self, system_id, states=[], first=10, after_cursor=None, fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

        graphql = """
            query CommandsQuery($systemId: ID!, $states: [CommandState!], $first: Int!, $afterCursor: String) {
                system(id: $systemId) {
                    commands(filters: { state: $states }, orderBy: { sort: ID, direction: DESC }, first: $first, after: $afterCursor) {
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
                          variables={'systemId': system_id, 'states': states, 'first': first, 'afterCursor': after_cursor},
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

        return self.query(graphql,
                          variables={'missionId': self.mission_id(), 'name': name},
                          path='data.gateway')

    def query(self, query, variables=None, operation_name=None, path=None):
        logger.debug(query)
        request = requests.post(f"{self.scheme}://{self.host}:{self.port}/script_api/v1/graphql",
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
