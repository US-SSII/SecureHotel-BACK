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

def jks_file_to_context(key_alias: str, key_password: str=None) -> OpenSSL.SSL.Context:
    """
    Loads a Java KeyStore file into an OpenSSL Context object.

    Args:
        key_alias (str): The alias of the key to load.
        key_password (str, optional): The password for decrypting the key entry. Defaults to None.

    Returns:
        OpenSSL.SSL.Context: The OpenSSL Context object loaded with the key and certificates.
    """
    keystore = jks.KeyStore.load(keystore_path, keystore_password)
    pk_entry = keystore.private_keys[key_alias]

    # If the key could not be decrypted using the store password,decrypt with a custom password now
    if not pk_entry.is_decrypted() and key_password:
        pk_entry.decrypt(key_password)

    pkey = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_ASN1, pk_entry.pkey)
    public_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, pk_entry.cert_chain[0][1])
    trusted_certs = [OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert.cert)
                     for alias, cert in keystore.certs]

    ctx = SSL.Context(SSL.TLS_METHOD)
    ctx.set_options(SSL.OP_NO_SSLv2 | SSL.OP_NO_SSLv3 | SSL.OP_NO_TLSv1 | SSL.OP_NO_TLSv1_1)
    ctx.set_min_proto_version(SSL.TLS1_3_VERSION)
    #cipher_suite = "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384"
    #ctx.set_cipher_list(cipher_suite)
    ctx.use_privatekey(pkey)
    ctx.use_certificate(public_cert)
    ctx.check_privatekey()  # Want to know ASAP if there is a problem
    cert_store = ctx.get_cert_store()
    for cert in trusted_certs:
        cert_store.add_cert(cert)

    return ctx




