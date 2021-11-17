import argparse

def get_parser():
    # Set up command line arguments
    parser = argparse.ArgumentParser()

    # Required Args
    parser.add_argument(
        "host",
        help='Major Tom host name. Can also be an IP address for local development/on prem deployments.')
    parser.add_argument(
        "token",
        help='Script Token used to authenticate the connection. Look this up in Major Tom under the script page for the script you are trying to connect.')

    # Optional Args
    parser.add_argument(
        '-b',
        '--basicauth',
        help='Basic Authentication credentials. Used mostly by Kubos engineers internally for testing. Not required unless BasicAuth is active on your Major Tom instance. Must be in the format "username:password".',
        required=False)

    parser.add_argument(
        '-s', 
        '--scheme',
        choices=["http", "https"],
        type=str,
        default="https",
        help="You may choose your transport scheme. The non-secure version can support on prem deployments and local development without https.",
        required=False)

    return parser