import os
from configparser import ConfigParser

import OpenSSL
import jks
from OpenSSL import crypto
from loguru import logger

# CONSTANTS
ASN1 = OpenSSL.crypto.FILETYPE_ASN1
configuration = ConfigParser()
configuration.read("configuration.ini")
current_directory = os.path.dirname(os.path.abspath(__file__))
keystore_password = configuration.get("KEYSTORE", "password")
keystore_path = os.path.join(current_directory, configuration.get("KEYSTORE", "path"))


def generate_key_pair() -> OpenSSL.crypto.PKey:
    """
    Generates a new RSA key pair with a key length of 2048 bits.

    Returns:
        OpenSSL.crypto.PKey: The generated key pair.
    """
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    return key


def generate_certificate(key: OpenSSL.crypto.PKey, common_name: str) -> OpenSSL.crypto.X509:
    """
    Generates a certificate with the given key and common name.

    Args:
        key(OpenSSL.crypto.PKey): The key to be used for signing the certificate.
        common_name(str): The common name to be set in the certificate subject.

    Returns:
        OpenSSL.crypto.X509: The generated certificate.
    """
    cert = crypto.X509()
    cert.get_subject().CN = common_name
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # Un año de validez
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    return cert


def save_key_and_certificate_with_alias(key: OpenSSL.crypto.PKey, cert: OpenSSL.crypto.X509, alias: str) -> None:
    """
    Saves the given key and certificate with the specified alias to a keystore.

    Args:
        key (OpenSSL.crypto.PKey): The private key to be saved.
        cert (OpenSSL.crypto.X509): The certificate to be saved.
        alias (str): The alias to be associated with the key and certificate.

    Raises:
        Exception: If there is an error saving the key and certificate.
    """
    try:
        if not os.path.exists(keystore_path):
            keystore = jks.KeyStore.new("jks", [])
        else:
            keystore = jks.KeyStore.load(keystore_path, keystore_password)
        dumped_cert = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
        dumped_key = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_ASN1, key)
        private_key = jks.PrivateKeyEntry.new(alias, [dumped_cert], dumped_key, 'rsa_raw')
        keystore.entries[alias] = private_key

        logger.info(f"Saving key and certificate with alias '{keystore_path}' to keystore...")
        keystore.save(keystore_path, keystore_password)
        logger.info(f"Key and certificate with alias '{alias}' saved to keystore successfully.")
    except Exception as e:
        logger.error(f"Error saving key and certificate: {e}")