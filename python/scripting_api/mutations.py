import logging
import json

logger = logging.getLogger(__name__)


class MutationError(Exception):
    """Raised when a Mutation Fails"""
    pass


class Mutations:
    def __init__(self, api):
        self.api = api

    def queue_and_execute_command(self, system_id, command_definition_id, gateway_id, fields, return_fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

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

        result = self.api.query(graphql,
                                variables={
                                    'systemId': system_id,
                                    'commandDefinitionId': command_definition_id,
                                    'gatewayId': gateway_id,
                                    'fields': json.dumps(fields)
                                },
                                path='data.queueAndExecuteCommand')
        logger.info(result["notice"])
        if not result["success"]:
            raise(MutationError(f"{result['notice']}: {result['errors']}"))

        return result

    def queue_command(self, system_id, command_definition_id, gateway_id, fields={}, return_fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

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

        result = self.api.query(graphql,
                                variables={
                                    'systemId': system_id,
                                    'commandDefinitionId': command_definition_id,
                                    'gatewayId': gateway_id,
                                    'fields': json.dumps(fields)
                                },
                                path='data.queueCommand')
        logger.info(result["notice"])
        if not result["success"]:
            raise(MutationError(f"{result['notice']}: {result['errors']}"))

        return result

    def execute_command(self, id, fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

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

        result = self.api.query(graphql,
                                variables={'id': id},
                                path='data.executeCommand')
        logger.info(result["notice"])
        if not result["success"]:
            raise(MutationError(f"{result['notice']}: {result['errors']}"))

        return result

    def cancel_command(self, id, fields=[]):
        default_fields = ['id', 'commandType', 'fields', 'state']

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

        result = self.api.query(graphql,
                                variables={'id': id},
                                path='data.cancelCommand')

        logger.info(result["notice"])
        if not result["success"]:
            raise(MutationError(f"{result['notice']}: {result['errors']}"))

        return result
