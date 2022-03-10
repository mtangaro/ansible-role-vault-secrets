#!/usr/bin/env python
import argparse
import random
from string import ascii_letters, digits, ascii_lowercase
import hvac

#______________________________________
def cli_options():

    parser = argparse.ArgumentParser(description='User passphrase manager')

    parser.add_argument('-v', '--vault-url', dest='vault_url', help='Hashicorp Vault endpoint')
    parser.add_argument('-w', '--wrapping-token', dest='wrapping_token', help='Wrapping token')
    parser.add_argument('-p', '--secret-path', dest='secret_path', help='secret path')
    parser.add_argument('-k', '--key', dest='vault_key', help='Hashicorp Vault key')
    parser.add_argument('-l', '--passphrase-length', dest='passphrase_length', help='Passphrase length')

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
def create_random_secret(passphrase_length):
    alphanum = ascii_letters + digits
    secret = ''.join([random.choice(alphanum) for i in range(passphrase_length)])
    return secret

#______________________________________
def write_secret_to_vault(vault_url, wrapping_token, secret_path, key, value):

    # Instantiate the hvac.Client class
    vault_client = hvac.Client(vault_url, verify=False)

    # Login directly with the wrapped token
    vault_client.auth_cubbyhole(wrapping_token)
    assert vault_client.is_authenticated()

    # Post secret
    secret={key:value}
    vault_client.secrets.kv.v2.create_or_update_secret(path=secret_path, secret=secret, mount_point='secrets', cas=0)

    # Logout and revoke current token
    vault_client.logout(revoke_token=True)

#______________________________________
def vault_secret_manager():

    options = cli_options()

    passphrase = create_random_secret(options.passphrase_length)

    write_secret_to_vault(options.vault_url, options.wrapping_token, options.secret_path, options.key, passphrase)

#______________________________________
if __name__ == '__main__':
    vault_secrets_manager()
