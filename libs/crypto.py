from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
import subprocess
import datetime
import base64
from typing import Tuple


class Crypto:
    def __init__(self):
        """
        Initialise the class - load the private key from file
        """
        print('Initialising Crypto object')
        # Load server keys
        if 'CSAFE_KEY' in os.environ and 'CSAFE_KPWD' in os.environ:
            key = '\n'.join(os.environ['CSAFE_KEY'].split('\\n')) + '\n'
            pw = os.environ['CSAFE_KPWD']
            self.private_key = serialization.load_pem_private_key(
                        data=(key).encode('utf-8'),
                        password=pw.encode('utf-8'),
                        backend=default_backend()
                    )
            print("Server's secure key obtained from environment")
        else:
            print("Server secure key not in environment variables")


        # server_keydir = 'keys/'
        # with open(os.path.join(server_keydir, 'private_key.pem'), "rb") as key_file:
        #     self.private_key = serialization.load_pem_private_key(
        #         data=key_file.read(),
        #         password=b'secure server passphrase',
        #         backend=default_backend()
        #     )
        self.public_key = self.private_key.public_key()
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return

    def pub_key(self):
        """
        Return the public key
        :return: bytes
        """
        return self.public_key_pem

    def decrypt(self, msg: str, sig: str, pkey: str) -> Tuple[bool, str]:
        """
        Build safe public key from str supplied
        :param msg:
        :param sig:
        :param pkey:
        :return:  encrypted message, message signature
        """
        #
        safe_public_key = serialization.load_pem_public_key(bytes(pkey, 'utf-8'),
                                                            backend=default_backend())
        # Decrypt
        try:
            plaintext = self.private_key.decrypt(
                base64.urlsafe_b64decode(msg),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                ))
            decrypt_success = True
        except ValueError:
            decrypt_success = False

        # Check signature if decryption was successful
        if decrypt_success:
            try:
                safe_public_key.verify(
                    base64.urlsafe_b64decode(sig),
                    plaintext,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256())
                signature_valid = True
            except InvalidSignature as e:
                print('Invalid signature : {}'.format(e))
                signature_valid = False
        else:
            signature_valid = False

        if signature_valid:
            return signature_valid, str(plaintext.decode('utf-8'))
        else:
            return signature_valid, ''

    def encrypt(self, msg: str, safe_pkey: str) -> Tuple[str, str]:
        """
        Encrypt and sign server message to safe
        :param msg:
        :param safe_pkey:
        :return:
        """
        # Sign message
        server_message_bin = bytes(msg.encode('UTF-8'))
        server_message_sig = self.private_key.sign(
            server_message_bin,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256())
        server_message_sig_64 = base64.urlsafe_b64encode(server_message_sig)
        # Convert safe_pkey into form that can be used
        safe_public_key = serialization.load_pem_public_key(bytes(safe_pkey, 'utf-8'),
                                                            backend=default_backend())

        # Encrypt message
        server_message_enc = safe_public_key.encrypt(
            server_message_bin,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        server_message_enc_64 = base64.urlsafe_b64encode(server_message_enc)

        return server_message_enc_64, server_message_sig_64
