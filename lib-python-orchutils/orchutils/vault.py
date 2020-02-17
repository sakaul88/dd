import base64
import hvac
import logging
import os
import requests
import six
import time
import yaml
from functools import wraps

import baseutils

logger = logging.getLogger(__name__)
certs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vault_certs')
credentials_file = '/root/.vault/credentials'
client = None


def get_vault_ca():
    """
    Returns the path to the CA file that can be used to validate the Vault server's certificate.
    Returns: The path to the Vault CA
    """
    return os.path.join(certs_dir, 'cacerts.pem')


def login(vault_url, vault_access_token):
    """
    Authenticates with Vault, instantiating the long-lived client object.
    This can either be called directly or you can rely on the ensure_client decorator if the credentials are passed via environment variables or files.
    """
    global client
    logger.info('Creating Vault client object')
    client = baseutils.retry(hvac.Client, url=vault_url, token=vault_access_token, verify=get_vault_ca())


def ensure_client(f):
    """
    Ensures that the Vault client object has been initialised.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        global client
        vault_url = vault_access_token = None
        if client is None:
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as fh:
                    credentials = yaml.safe_load(fh)
                    vault_url = credentials.get('vault_url')
                    vault_access_token = credentials.get('vault_access_token')
            else:
                vault_url = os.environ.get('VAULT_URL')
                vault_access_token = os.environ.get('VAULT_ACCESS_TOKEN')
            if not vault_url or not vault_access_token:
                raise Exception('Not logged into Vault and unable to discover Vault credentials')
            login(vault_url, vault_access_token)
        return f(*args, **kwargs)
    return decorated


@ensure_client
def create_transit_key(enc_key_name):
    """
    Creates a new transit encryption key in Vault.
    Args:
        enc_key_name: The name of the Vault transit encryption key to create
    """
    baseutils.retry(client.secrets.transit.create_key, enc_key_name)


@ensure_client
def decrypt_dict(enc_key_name, data):
    """
    Decrypts the values of a passed dictionary.
    The dictionary is recursively traversed to find all values and the values are passed in batch to Vault for decryption.
    It is therefore much more efficient to use this method to decrypt a dictionary with many values than individually calling decrypt for each one.
    Caution: The passed dictionary is mutated.
    Args:
        enc_key_name: The name of the Vault transit encryption key to use for decryption
        data: A dictionary of values to be decrypted. The dictionary can contain nested keys. The passed dictionary is mutated to contain the decrypted values
    """
    enc_aggregated_data = _aggregate_dict_for_vault(data, 'ciphertext')
    dec_aggregated_data = baseutils.retry(client.secrets.transit.decrypt_data, enc_key_name, None, batch_input=enc_aggregated_data)['data']['batch_results']
    _restore_dict_from_vault(data, 'plaintext', dec_aggregated_data)


@ensure_client
def encrypt_dict(enc_key_name, data):
    """
    Encrypts the values of a passed dictionary.
    The dictionary is recursively traversed to find all values and the values are passed in batch to Vault for encryption.
    It is therefore much more efficient to use this method to encrypt a dictionary with many values than individually calling encrypt for each one.
    Caution: The passed dictionary is mutated.
    Args:
        enc_key_name: The name of the Vault transit encryption key to use for encryption
        data: A dictionary of values to be encrypted. The dictionary can contain nested keys. The passed dictionary is mutated to contain the encrypted values
    """
    dec_aggregated_data = _aggregate_dict_for_vault(data, 'plaintext')
    try:
        enc_aggregated_data = baseutils.retry(client.secrets.transit.encrypt_data, enc_key_name, None, batch_input=dec_aggregated_data)['data']['batch_results']
    except Exception as e:
        if str(e) == 'encryption key not found':  # Create the key if it does not yet exist
            create_transit_key(enc_key_name)
            enc_aggregated_data = baseutils.retry(client.secrets.transit.encrypt_data, enc_key_name, None, batch_input=dec_aggregated_data)['data']['batch_results']
        else:
            raise
    _restore_dict_from_vault(data, 'ciphertext', enc_aggregated_data)


def _aggregate_dict_for_vault(data, vault_key, aggregated_data=None):
    """
    Aggregates a dictionary's values in the form needed for passing as a batch list to Vaults encrypt and decrypt methods.
    Args:
        data: The data to be aggregated.
        vault_key: The dictionary key that Vault expects for the data. This is specific to the encrypt and decrypt functions of vault and is either 'plaintext' or 'ciphertext'
        aggregated_data: Internal parameter used as part of the functions recursive implementation. This is the eventual return value
    Returns: A list of aggregated data of the form: [{vault_key: '<value>'}, ...]
    """
    if aggregated_data is None:
        aggregated_data = []
    keys = list(data.keys())
    keys.sort()  # Need to guarantee that iteration ordering in aggregate and restore function match while mutating the values
    for key in keys:
        value = data[key]
        if isinstance(value, dict):
            _aggregate_dict_for_vault(value, vault_key, aggregated_data)
        elif isinstance(value, six.string_types):
            aggregated_data.append({vault_key: base64.b64encode(value.encode('utf-8')) if vault_key == 'plaintext' else value})  # Plaintext must base64 encoded for Vault
    return aggregated_data


def _restore_dict_from_vault(data, vault_key, aggregated_data):
    """
    Restores aggregated data from Vault into an original data dictionary, overwriting existing encrypted values.
    Args:
        data: The original data dictionary to have decrypted values written into
        vault_key: The dictionary key that Vault returned. This is specific to the encrypt and decrypt functions of vault and is either 'plaintext' or 'ciphertext'
        aggregated_data: The raw data that Vault returned as part of a batch encrypt or decrypt process
    """
    keys = list(data.keys())
    keys.sort()  # Need to guarantee that iteration ordering in aggregate and restore function match while mutating the values
    for key in keys:
        value = data[key]
        if isinstance(value, dict):
            _restore_dict_from_vault(value, vault_key, aggregated_data)
        elif isinstance(value, six.string_types):
            vault_entry = aggregated_data.pop(0)[vault_key]
            data[key] = base64.b64decode(vault_entry).decode('utf-8') if vault_key == 'plaintext' else vault_entry


@ensure_client
def decrypt_value(key_name, value):
    """
    Decrypts a single value using Vault's transit encryption service.
    Args:
        key_name: The name of the Vault transit key to use for decryption
        value: The value to decrypt
    """
    return base64.b64decode(baseutils.retry(client.secrets.transit.decrypt_data, key_name, value)['data']['plaintext']).decode('utf-8')


@ensure_client
def encrypt_value(key_name, value):
    """
    Encrypts a single value using Vault's transit encryption service.
    Args:
        key_name: The name of the Vault transit key to use for encryption
        value: The value to encrypt
    """
    return baseutils.retry(client.secrets.transit.encrypt_data, key_name, base64.b64encode(value.encode('utf-8')))['data']['ciphertext']


@ensure_client
def issue_certificate(hostnames, ca_mount='csp-intermediate-ca', role='csp-role', ttl='43800h', revoke_cert=False):
    """
    Issues a certificate for the specified CA mount point and roles using Vault's pki secrets engine.
    Both the certificate and the key are generated and returned.
    Args:
        hostnames: A comma-seperated list of hostnames, with no spaces, to issue the cert for. The hostnames can contain a wildcard. This constitutes the altnames of the cert
        ca_mount: The location where the secrets engine is mounted at in Vault (Optional, default: csp-intermediate-ca)
        role: The Vault pki role to use when generating the certificate (Optional, default: 'csp-role')
        ttl: Specifies the ttl of the certificate in a form like "2160h" - 2160 hours (Optional, default: "43800h" - 5 years)
        revoke_cert: Certain certs are re-generated regularly. To avoid the number being tracked in Vault from climbing, you can trigger the generated cert to be
                     revoked immediately. You will still receive the cert back, but it won't be tracked in Vault.
    Returns: The issued certificate as a dictionary containing all properties as returned from vault, which includes: private_key, certificate, ca_chain
    """
    retry = True
    retry_attempt = 0
    while retry:
        try:
            response = requests.post('{vault_url}/v1/{ca_mount}/issue/{role}'.format(vault_url=client.url, ca_mount=ca_mount, role=role),
                                     json={
                                         'common_name': hostnames.split(',', 1)[0],
                                         'alt_names': hostnames,
                                         'ttl': ttl
                                     },
                                     headers={'X-Vault-Token': client.token},
                                     verify=get_vault_ca())
            response.raise_for_status()
            vault_response = response.json()['data']
            serial_number = vault_response['serial_number']
            retry = False
        except Exception:
            retry_attempt += 1
            if retry_attempt < 10:
                time.sleep(5)
            else:
                raise
    if revoke_cert:
        retry = True
        retry_attempt = 0
        while retry:
            try:
                response = requests.post('{vault_url}/v1/{ca_mount}/revoke'.format(vault_url=client.url, ca_mount=ca_mount),
                                         json={
                                             'serial_number': serial_number
                                         },
                                         headers={'X-Vault-Token': client.token},
                                         verify=get_vault_ca())
                response.raise_for_status()
                retry = False
            except Exception:
                retry_attempt += 1
                if retry_attempt < 10:
                    time.sleep(5)
                else:
                    break  # We don't need to fail a code flow just because we could not remove the cert from Vault
    return vault_response


@ensure_client
def delete(path):
    """
    Deletes a secret at a given path in Vault.
        path: The path to delete the secrets at
    """
    baseutils.retry(client.delete, path=path)


@ensure_client
def list_keys(path):
    """
    Retrieves a list of keys at a specified path in Vault.
    Args:
        path: The path to list the keys at, eg. secret/my/path
    Returns: A list of keys at the specified path
    """
    result = baseutils.retry(client.list, path=path) or {}
    return result.get('data', {}).get('keys', [])


@ensure_client
def read(path, property=None):
    """
    Retrieves a value from the Vault. This is not specific to a secret engine backend and anything can be queried.
    Vault secrets are returned as dictionaries. Only the actual value (data attribute of vault response) is returned, not the request metadata.
    Args:
        path: The path to the secret to retrieve. This must include the backend eg. secret/my/path
        property: A sub-property of the secret (under the data attribute) to retrieve (Optional)
    Returns: The Vault secret as a dictionary or None if the value does not exist
    """
    result = baseutils.retry(client.read, path=path)
    if result:
        result = result.get('data', {})
        if property:
            result = result.get(property)
    return result


@ensure_client
def write(path, properties):
    """
    Write values to a given path.
    The values are key-value pairs that should be passed as a dictionary.
    Args:
        path: The path to write the secrets to
        properties: The properties to write as key-value pairs passed as a dictionary
    """
    baseutils.retry(client.write, path=path, **properties)
