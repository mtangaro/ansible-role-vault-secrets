#!/usr/bin/env python
import argparse
import random
from string import ascii_letters, digits, ascii_lowercase
import hvac

#______________________________________
def cli_options():

    parser = argparse.ArgumentParser(description='Hashicorp Vault secrets manager')

    parser.add_argument('action', choices=['write','read'], nargs='?', help='Read or Write secret')
    parser.add_argument('-v', '--vault-endpoint', dest='vault_endpoint', help='Hashicorp Vault endpoint')
    parser.add_argument('-t', '--token', dest='token', help='Wrapping or standard token')
    parser.add_argument('-m', '--mountpoint', dest='mountpoint', help='secret path')
    parser.add_argument('-p', '--secret-path', dest='secret_path', help='secret path')
    parser.add_argument('-k', '--key', dest='vault_key', help='Hashicorp Vault key')
    parser.add_argument('-w', '--wrap_token', dest='wrap_token', help='Use wrapping token')

    return parser.parse_args()

#______________________________________
def run_command(cmd):
    """
    Run subprocess call redirecting stdout, stderr and the command exit code.
    """
    proc = subprocess.Popen( args=cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    communicateRes = proc.communicate()
    stdout, stderr = communicateRes
    status = proc.wait()
    return stdout, stderr, status

#______________________________________
def read_secret_from_vault(endpoint, token, wrap_token,  mountpoint, secret_path):

    # Instantiate the hvac.Client class
    vault_client = hvac.Client(endpoint, verify=False)

    # Login directly with the (wrapped) token
    if eval(wrap_token) is True:
      vault_client.auth_cubbyhole(token)
    else:
      vault_client.token = token

    assert vault_client.is_authenticated()

    # Post secret
    secrets = vault_client.secrets.kv.v2.read_secret_version(path=secret_path, mount_point=mountpoint)

    # Logout and revoke current token
    # revoke token in case of wrapping
    if eval(wrap_token) is True:
      vault_client.logout(revoke_token=True)

    return secrets

#______________________________________
def vault_secrets_manager():

    options = cli_options()

    secrets = read_secret_from_vault(options.vault_endpoint, options.token, options.wrap_token, options.mountpoint, options.secret_path)

    # WARNING: it is mandatory that this is the only print, otherwise the ansible role is not capable to take the dictionary.
    print(secrets['data']['data'])

#______________________________________
if __name__ == '__main__':
    vault_secrets_manager()
