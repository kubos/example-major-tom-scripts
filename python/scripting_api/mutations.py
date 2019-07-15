import logging
import json

logger = logging.getLogger(__name__)


class Mutations:
    def __init__(self, api):
        self.api = api

    def queue_and_execute_command(self, system_id, command_definition_id, gateway_id, fields, return_fields=[]):
        default_fields = ['id', 'commandType', 'fields']

        graphql = """
            mutation QueueAndExecuteCommand($systemId: ID!, $commandDefinitionId: ID!, $gatewayId: ID!, $fields: Json) {
                queueAndExecuteCommand(input: { systemId: $systemId, commandDefinitionId: $commandDefinitionId, gatewayId: $gatewayId, fields: $fields }) {
                    success notice errors
                    command {
                        %s
                    }
                }
            }
        """ % ', '.join(set().union(default_fields, return_fields))

        return self.api.query(graphql,
                              variables={
                                  'systemId': system_id,
                                  'commandDefinitionId': command_definition_id,
                                  'gatewayId': gateway_id,
                                  'fields': json.dumps(fields)
                              },
                              path='data.queueAndExecuteCommand')

    def queue_command(self, system_id, command_definition_id, gateway_id, fields, return_fields=[]):
        default_fields = ['id', 'commandType', 'fields']

        graphql = """
            mutation QueueCommand($systemId: ID!, $commandDefinitionId: ID!, $gatewayId: ID!, $fields: Json) {
                queueCommand(input: { systemId: $systemId, commandDefinitionId: $commandDefinitionId, gatewayId: $gatewayId, fields: $fields }) {
                    success notice errors
                    command {
                        %s
                    }
                }
            }
        """ % ', '.join(set().union(default_fields, return_fields))

        return self.api.query(graphql,
                              variables={
                                  'systemId': system_id,
                                  'commandDefinitionId': command_definition_id,
                                  'gatewayId': gateway_id,
                                  'fields': json.dumps(fields)
                              },
                              path='data.queueCommand')

    def execute_command(self, id, fields=[]):
        default_fields = ['id', 'commandType', 'fields']

        graphql = """
            mutation ExecuteCommand($id: ID!) {
                executeCommand(input: { id: $id }) {
                    success notice errors
                    command {
                        %s
                    }
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.api.query(graphql,
                              variables={'id': id},
                              path='data.executeCommand')

    def cancel_command(self, id, fields=[]):
        default_fields = ['id', 'commandType', 'fields']

        graphql = """
            mutation CancelCommand($id: ID!) {
                cancelCommand(input: { id: $id }) {
                    success notice errors
                    command {
                        %s
                    }
                }
            }
        """ % ', '.join(set().union(default_fields, fields))

        return self.api.query(graphql,
                              variables={'id': id},
                              path='data.cancelCommand')


# api.mutations.queue_and_execute_command
