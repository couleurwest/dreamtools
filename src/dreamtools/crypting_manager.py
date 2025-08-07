_all_ = ['CryptoManager']
from argon2.exceptions import VerifyMismatchError

import base64
import json
import os
import secrets
import time
from base64 import b64encode, b64decode

import base58
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from . import toolbox


class CryptoManager:
    """
    Gère les opérations cryptographiques (génération de clés, chiffrement/déchiffrement, stockage en base).

    - Utilise X448 pour l'échange de clés.
    - AES-GCM pour le chiffrement symétrique.
    - Clés stockées chiffrées dans la base avec fingerprint.
    """
    master_key = None
    ph = PasswordHasher()

    @staticmethod
    def set_master_key(master_key: str | bytes):
        CryptoManager.master_key = toolbox.ensure_bytes(master_key)

    @staticmethod
    def generate_fingerprint(public_bytes: str | bytes) -> str:
        """Génère un fingerprint SHA-256 pour une clé publique"""
        public_bytes = toolbox.ensure_bytes(public_bytes)  # on s'assure que c'est du bytes
        fingerprint = hashes.Hash(hashes.SHA256())
        fingerprint.update(public_bytes)
        fingerprint_result = fingerprint.finalize()
        return base58.b58encode(fingerprint_result).decode()

    @staticmethod
    def get_fingerprint(public_key) -> str:
        """Retourne un digest SHA256 tronqué (16 premiers caractères) d'une clé publique."""
        raw_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(raw_bytes)
        full_digest = digest.finalize()
        base58_digest = base58.b58encode(full_digest).decode()
        return base58_digest[:16]

    @staticmethod
    def verify_fingerprint(public_bytes: str | bytes, stored_fingerprint: str) -> bool:
        """Vérifie que l'empreinte générée correspond à celle stockée."""
        fp1 = CryptoManager.generate_fingerprint(public_bytes)
        return fp1 == stored_fingerprint

    @staticmethod
    async def generate_keys() -> (bytes, bytes, bytes):
        """Génère une paire de clés X448, stocke en DB et retourne les éléments."""
        private_key = x448.X448PrivateKey.generate()
        private_bytes = private_key.private_bytes(encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw, encryption_algorithm=serialization.NoEncryption())
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
        finger_print = CryptoManager.generate_fingerprint(public_bytes)

        return public_bytes, private_bytes, finger_print

    @staticmethod
    def exchange_shared_key(private_key_bytes: bytes, public_key_bytes: bytes):
        """Échange de clés X448 pour générer une clé partagée"""
        private_key_bytes = toolbox.ensure_bytes(private_key_bytes)
        public_key_bytes = toolbox.ensure_bytes(public_key_bytes)

        private_key = x448.X448PrivateKey.from_private_bytes(private_key_bytes)
        public_key = x448.X448PublicKey.from_public_bytes(public_key_bytes)
        shared_key = private_key.exchange(public_key)

        return shared_key

    @staticmethod
    def encrypt_data(dc: str | bytes, shared_key, client_secret) -> str:
        # Générer les clés X448 pour l'expéditeur et le récepteur
        iv = os.urandom(12)  # IV pour AES-GCM
        aes_key = CryptoManager.derive_aes_key(shared_key,
                                               client_secret)  # Dériver la clé AES à partir de la clé partagée
        encryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=default_backend()).encryptor()
        data_bytes = toolbox.ensure_bytes(dc)
        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()
        tag = encryptor.tag

        encryted_data = {'ciphertext': CryptoManager.encode_secret(ciphertext), 'iv': CryptoManager.encode_secret(iv),
            'tag': CryptoManager.encode_secret(tag)}
        return json.dumps(encryted_data)

    @staticmethod
    def encrypt_message(dc: dict | str, receiver_public_key, sender_private_key, sender_client_secret) -> str:
        # Générer les clés X448 pour l'expéditeur et le récepteur
        if isinstance(dc, dict):
            dc = json.dumps(dc)

        shared_key = CryptoManager.exchange_shared_key(sender_private_key, receiver_public_key)
        # Chiffrer le message
        return CryptoManager.encrypt_data(dc, shared_key, sender_client_secret)

    @staticmethod
    def encrypt_password(password):
        """
        Argon2 est une fonction de hachage de mot de passe lauréate du concours Password Hashing Competition.
        """
        return CryptoManager.ph.hash(password)

    @staticmethod
    def decrypt_encrypted_data(encrypted_data: str, shared_key: str | bytes, secret_key: str | bytes) -> str:
        """Déchiffre les données avec AES-GCM en utilisant la clé partagée dérivée"""
        dc = json.loads(encrypted_data)
        iv = CryptoManager.decode_secret(dc['iv'])
        tag = CryptoManager.decode_secret(dc['tag'])
        ciphertext = CryptoManager.decode_secret(dc['ciphertext'])

        aes_key = CryptoManager.derive_aes_key(shared_key, secret_key)  # Dériver la clé AES à partir de la clé partagée
        cipher_decrypt = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
        decypted_message = cipher_decrypt.update(ciphertext) + cipher_decrypt.finalize()

        return toolbox.ensure_string(decypted_message)

    @staticmethod
    def decrypt_encrypted_message(message_crypted, receiver_private_key: bytes, sender_public_key: bytes,
                                  sender_client_secret: bytes) -> str:
        """Déchiffre un message JSON en utilisant AES-GCM et l'échange de clés X448"""
        shared_key = CryptoManager.exchange_shared_key(receiver_private_key, sender_public_key)
        return CryptoManager.decrypt_encrypted_data(message_crypted, shared_key, sender_client_secret)

    @staticmethod
    def check_password(password, hasher):
        """
        Vérification du mot de passe
        """
        try:
            return CryptoManager.ph.verify(hasher, password)
        except VerifyMismatchError:
            return False

    @staticmethod
    def generate_bytes_secret(x: int = 24) -> bytes:
        """
        Génère une clé secrète aléatoire sous forme d'octets sécurisés.
    
        :param x: La longueur de la clé en octets. Par défaut, la longueur est de 24 octets.
        :type x: Int
        :return: Une séquence d'octets aléatoires sécurisés.
        :rtype: Bytes
    
        : Example :
    
        >>> CryptoManager.generate_bytes_secret(16)
        b'\x8a\xe4\xb3\xf0\xd5\xc7\xe9\x89\xaa\xa3~\xd1\x92\xc5\xb5'
        """
        return secrets.token_bytes(x)

    @staticmethod
    def generate_hex_secret(x=16) -> str:
        """Génère une clé secrète aléatoire sous forme de chaîne hexadécimale.
    
        :param x: La longueur de la chaîne hexadécimale. Par défaut, la longueur est déterminée automatiquement.
        :type x: Int, optional
        :return: Une chaîne hexadécimale aléatoire.
        :rtype: Str
    
        >>> CryptoManager.generate_hex_secret(16)
        'a1b2c3d4e5f6'
        """
        return secrets.token_hex(x)

    @staticmethod
    def code_unique(texte):
        timestamp = str(int(time.time()))
        texte_timestamp = texte + timestamp
        hasher = hashes.Hash(hashes.SHA1())
        hasher.update(texte_timestamp.encode())
        code_hash = hasher.finalize().hex()
        return code_hash[:8]  # Récupère les 8 premiers caractères du code de hachage

    @staticmethod
    def derive_aes_key(auth_key: str | bytes, salt_key: str | bytes) -> bytes:
        """Dérive une clé AES de 256 bits à partir de la clé partagée X448 en utilisant HKDF"""
        # Utiliser HKDF pour dériver une clé AES 256 bits
        auth_key = toolbox.ensure_bytes(auth_key)
        salt_key = toolbox.ensure_bytes(salt_key)

        hkdf = HKDF(algorithm=hashes.SHA256(), length=32,  # 32 bytes = 256 bits
            salt=salt_key, info=b"SharedKeyDerivation", backend=default_backend())
        return hkdf.derive(auth_key)

    @staticmethod
    def fernet_engine(auth_key: str | bytes, salt_key: str | bytes) -> Fernet:
        """
            Déchiffre les données d'un fichier et les retourne.
    
            Args:
            fs (str): Le chemin du fichier contenant les données chiffrées.
    
            Returns:
            str: Les données déchiffrées.
        """
        key_derived = CryptoManager.derive_aes_key(auth_key, salt_key)
        fernet_key = base64.urlsafe_b64encode(key_derived)
        return Fernet(fernet_key)

    @staticmethod
    def basic_auth_encode(s_id, s_sekret):
        """Generation d'un autorization basic de type ID:SECRET"""
        access_token = CryptoManager.encode_secret(f"{s_id}:{s_sekret}")
        return f"Basic {access_token}"

    @staticmethod
    def basic_auth_decode(access_token):
        """Generation d'un autorization basic de type ID:SECRET"""
        access_token = toolbox.ensure_string(CryptoManager.decode_secret(access_token))
        return access_token.split(":")

    @staticmethod
    def encode_secret(secret_data: bytes | str) -> str:
        secret_data = toolbox.ensure_bytes(secret_data)
        encrypted_data = b64encode(secret_data)
        return toolbox.ensure_string(encrypted_data)

    @staticmethod
    def decode_secret(secret_data: bytes | str) -> bytes:
        secret_data = toolbox.ensure_string(secret_data)
        encrypted_data = b64decode(secret_data)
        return encrypted_data

    @staticmethod
    def encrypt_secret(secret_data, auth_key, salt_key) -> str:
        b_cs = toolbox.ensure_bytes(secret_data)
        engine = CryptoManager.fernet_engine(auth_key, salt_key)
        secret_data = engine.encrypt(b_cs)
        return toolbox.ensure_string(secret_data)

    @staticmethod
    def decrypt_secret(encrypted_secret: bytes | str, auth_key: bytes | str, salt_key: bytes | str) -> str:
        engine = CryptoManager.fernet_engine(auth_key, salt_key)
        b_cs = engine.decrypt(encrypted_secret)
        return toolbox.ensure_string(b_cs)

    @staticmethod
    def encrypt_file(js: dict, fs: str, auth_key: str, salt_key: str):
        """
            Déchiffre les données d'un fichier et les retourne.

            Args:
            fs (str): Le chemin du fichier contenant les données chiffrées.

            Returns:
            str: Les données déchiffrées.
        """
        document = json.dumps(js)
        sensitive_data = toolbox.ensure_bytes(CryptoManager.encrypt_secret(document, auth_key, salt_key))

        with open(fs, 'wb') as file:
            file.write(sensitive_data)

    @staticmethod
    def decrypt_file(fs: str, auth_key: str, salt_key: str):
        """
            Déchiffre les données d'un fichier et les retourne.

            Args:
            fs (str): Le chemin du fichier contenant les données chiffrées.

            Returns:
            str: Les données déchiffrées.
        """
        try:
            with open(fs, 'rb') as file:
                encrypted_data = file.read()

            sensitive_data = CryptoManager.decrypt_secret(encrypted_data, auth_key, salt_key)
            return json.loads(sensitive_data)
        except Exception as ex:
            raise Exception('Erreur clé de chiffrage : {}'.format(ex))
