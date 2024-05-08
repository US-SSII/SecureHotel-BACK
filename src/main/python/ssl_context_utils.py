import os
from configparser import ConfigParser

import OpenSSL
import jks
from OpenSSL import SSL

# CONSTANTS
ASN1 = OpenSSL.crypto.FILETYPE_ASN1
configuration = ConfigParser()
configuration.read("configuration.ini")
current_directory = os.path.dirname(os.path.abspath(__file__))
keystore_password = configuration.get("KEYSTORE", "password")
keystore_path = os.path.join(current_directory, configuration.get("KEYSTORE", "path"))
certification_path = os.path.join(current_directory, configuration.get("CERTIFICATION", "path"))

import OpenSSL


def load_keystore(keystore_path: str, keystore_password: str) -> jks.KeyStore:
    """
    Loads a Java KeyStore file.

    Args:
        keystore_path (str): The path to the keystore file.
        keystore_password (str): The password for the keystore.

    Returns:
        jks.KeyStore: The loaded keystore.
    """
    try:
        return jks.KeyStore.load(keystore_path, keystore_password)
    except jks.KeystoreException as e:
        raise ValueError(f"Invalid keystore path or password: {e}")


def decrypt_key(pk_entry: jks.PrivateKeyEntry, key_password: str) -> None:
    """
    Decrypts the private key entry.

    Args:
        pk_entry (jks.PrivateKeyEntry): The private key entry to decrypt.
        key_password (str): The password for decrypting the key entry.
    """
    if not pk_entry.is_decrypted() and key_password:
        pk_entry.decrypt(key_password)


def load_certificates(pk_entry: jks.PrivateKeyEntry, keystore: jks.KeyStore) -> tuple:
    """
    Loads the public certificate and trusted certificates.

    Args:
        pk_entry (jks.PrivateKeyEntry): The private key entry.
        keystore (jks.KeyStore): The keystore.

    Returns:
        tuple: A tuple containing the public certificate and trusted certificates.
    """
    public_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, pk_entry.cert_chain[0][1])
    trusted_certs = [OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert.cert)
                     for alias, cert in keystore.certs]
    return public_cert, trusted_certs


def create_ssl_context(pkey: OpenSSL.crypto.PKey, public_cert: OpenSSL.crypto.X509,
                       trusted_certs: list) -> OpenSSL.SSL.Context:
    """
    Creates an SSL context.

    Args:
        pkey (OpenSSL.crypto.PKey): The private key.
        public_cert (OpenSSL.crypto.X509): The public certificate.
        trusted_certs (list): The trusted certificates.

    Returns:
        OpenSSL.SSL.Context: The SSL context.
    """
    ctx = OpenSSL.SSL.Context(OpenSSL.SSL.TLS_METHOD)
    ctx.set_options(
        OpenSSL.SSL.OP_NO_SSLv2 | OpenSSL.SSL.OP_NO_SSLv3 | OpenSSL.SSL.OP_NO_TLSv1 | OpenSSL.SSL.OP_NO_TLSv1_1)
    ctx.set_min_proto_version(OpenSSL.SSL.TLS1_3_VERSION)
    ctx.use_privatekey(pkey)
    ctx.use_certificate(public_cert)
    ctx.check_privatekey()  # Want to know ASAP if there is a problem
    cert_store = ctx.get_cert_store()
    for cert in trusted_certs:
        cert_store.add_cert(cert)
    return ctx


def jks_file_to_context(key_alias: str, key_password: str = None) -> OpenSSL.SSL.Context:
    """
    Loads a Java KeyStore file into an OpenSSL Context object.

    Args:
        key_alias (str): The alias of the key to load.
        key_password (str, optional): The password for decrypting the key entry. Defaults to None.

    Returns:
        OpenSSL.SSL.Context: The OpenSSL Context object loaded with the key and certificates.
    """
    keystore = load_keystore(keystore_path, keystore_password)
    pk_entry = keystore.private_keys[key_alias]
    decrypt_key(pk_entry, key_password)
    pkey = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_ASN1, pk_entry.pkey)
    public_cert, trusted_certs = load_certificates(pk_entry, keystore)

    # Save the certificate to a file
    with open(certification_path, "wb") as f:
        f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, public_cert))

    ctx = create_ssl_context(pkey, public_cert, trusted_certs)
    return ctx




