from argon2.exceptions import VerifyMismatchError

from .toolbox import ensure_bytes

_all_ = ['CryptoManager']
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
        CryptoManager.master_key = ensure_bytes(master_key)

    @staticmethod
    def generate_fingerprint(public_bytes: str|bytes) -> str:
        """Génère un fingerprint SHA-256 pour une clé publique"""
        public_bytes = ensure_bytes(public_bytes)       # on s'assure que c'est du bytes
        fingerprint = hashes.Hash(hashes.SHA256())
        fingerprint.update(public_bytes)
        fingerprint_result = fingerprint.finalize()
        return base58.b58encode(fingerprint_result).decode()

    @staticmethod
    def get_fingerprint(public_key) -> str:
        """Retourne un digest SHA256 tronqué (16 premiers caractères) d'une clé publique."""
        raw_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(raw_bytes)
        full_digest = digest.finalize()
        base58_digest = base58.b58encode(full_digest).decode()
        return base58_digest[:16]

    @staticmethod
    def verify_fingerprint(public_bytes: str|bytes, stored_fingerprint: str) -> bool:
        """Vérifie que l'empreinte générée correspond à celle stockée."""
        fp1 = CryptoManager.generate_fingerprint(public_bytes)

        return fp1 == stored_fingerprint

    @staticmethod
    async def generate_keys()->(bytes, bytes, bytes):
        """Génère une paire de clés X448, stocke en DB et retourne les éléments."""
        private_key = x448.X448PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        finger_print = CryptoManager.generate_fingerprint(public_bytes)

        return public_bytes, private_bytes, finger_print

    @staticmethod
    def encrypt_private_key(private_key_byte: str|bytes, client_secret: str|bytes) -> bytes:
        """Chiffre une clé privée à l'aide d'AES-GCM et retourne un JSON sérialisé."""

        aes_key = CryptoManager.derive_aes_key(CryptoManager.master_key, client_secret)
        iv = os.urandom(12)  # Vecteur d'initialisation aléatoire
        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        encrypted = encryptor.update(private_key_byte) + encryptor.finalize()
        payload = {
            "iv": base64.b64encode(iv).decode(),
            "tag": base64.b64encode(encryptor.tag).decode(),
            "encrypted_key": base64.b64encode(encrypted).decode()
        }

        return json.dumps(payload).encode()

    @staticmethod
    def decrypt_private_key(encrypted_key_data: str|bytes, client_secret: str) -> bytes:
        """Déchiffre une clé privée AES-GCM à partir d'un JSON sérialisé."""
        encrypted_key_data = json.loads(encrypted_key_data)

        iv = base64.b64decode(encrypted_key_data['iv'])

        tag = base64.b64decode(encrypted_key_data['tag'].encode())
        encrypted_key = base64.b64decode(encrypted_key_data['encrypted_key'].encode())

        aes_key = CryptoManager.derive_aes_key(CryptoManager.master_key, client_secret.encode())

        cipher_decrypt = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()
        return cipher_decrypt.update(encrypted_key) + cipher_decrypt.finalize()

    @staticmethod
    def exchange_shared_key(private_key_bytes: bytes, public_key_bytes: bytes):
        """Échange de clés X448 pour générer une clé partagée"""
        private_key_bytes = ensure_bytes(private_key_bytes)
        public_key_bytes = ensure_bytes(public_key_bytes)

        private_key = x448.X448PrivateKey.from_private_bytes(private_key_bytes)
        public_key = x448.X448PublicKey.from_public_bytes(public_key_bytes)
        shared_key = private_key.exchange(public_key)

        return shared_key

    @staticmethod
    def encrypt_document(document: str|bytes, shared_key, client_secret) -> dict:
        # Générer les clés X448 pour l'expéditeur et le récepteur
        iv = os.urandom(12)  # IV pour AES-GCM
        aes_key = CryptoManager.derive_aes_key(shared_key,
                                               client_secret)  # Dériver la clé AES à partir de la clé partagée
        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()

        ciphertext = encryptor.update(document) + encryptor.finalize()
        tag = encryptor.tag

        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'nonce': base64.b64encode(iv).decode(),
            'tag': base64.b64encode(tag).decode(),
        }

    @staticmethod
    def decrypt_document(encrypted_data, shared_key: bytes, secret_key: bytes) -> bytes:
        """Déchiffre les données avec AES-GCM en utilisant la clé partagée dérivée"""
        aes_key = CryptoManager.derive_aes_key(shared_key, secret_key)  # Dériver la clé AES à partir de la clé partagée

        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        iv = base64.b64decode(encrypted_data['nonce'])
        tag = base64.b64decode(encrypted_data['tag'])

        cipher_decrypt = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        document = cipher_decrypt.update(
            ciphertext) + cipher_decrypt.finalize()

        return document

    @staticmethod
    def decrypt_message_json(message_crypted, sender_public_key: bytes,
                             receiver_private_key: bytes, sender_client_secret: bytes) -> dict:
        """Déchiffre un message JSON en utilisant AES-GCM et l'échange de clés X448"""
        shared_key = CryptoManager.exchange_shared_key(receiver_private_key, sender_public_key)
        # Déchiffrer le message
        decrypted_message = CryptoManager.decrypt_document(message_crypted, shared_key, sender_client_secret)

        return json.loads(decrypted_message.decode())

    @staticmethod
    def encrypt_message_json(document: dict, receiver_public_key, sender_private_key, sender_client_secret)->dict:
        # Générer les clés X448 pour l'expéditeur et le récepteur
        shared_key = CryptoManager.exchange_shared_key(sender_private_key, receiver_public_key)
        document = json.dumps(document).encode()

        # Chiffrer le message
        return CryptoManager.encrypt_document(document, shared_key, sender_client_secret)

    @staticmethod
    def encrypt(password):
        """
        Argon2 est une fonction de hachage de mot de passe lauréate du concours Password Hashing Competition.
        """
        return CryptoManager.ph.hash(password)

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
    def basic_auth_encode(s_id, s_sekret):
        """Generation d'un autorization basic de type ID:SECRET"""
        access_token = b64encode(f"{s_id}:{s_sekret}".encode("utf-8")).decode("ascii")
        return f"Basic {access_token}"

    @staticmethod
    def basic_auth_decode(access_token):
        """Generation d'un autorization basic de type ID:SECRET"""
        access_token = b64decode(access_token.encode("ascii")).decode("utf-8")
        return access_token.split(":")

    @staticmethod
    def derive_aes_key(auth_key: str|bytes, salt_key: str|bytes)->bytes:
        """Dérive une clé AES de 256 bits à partir de la clé partagée X448 en utilisant HKDF"""
        # Utiliser HKDF pour dériver une clé AES 256 bits
        auth_key = ensure_bytes(auth_key)
        salt_key = ensure_bytes(salt_key)

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes = 256 bits
            salt=salt_key,
            info=b"SharedKeyDerivation",
            backend=default_backend()
        )
        return hkdf.derive(auth_key)

    @staticmethod
    def fernet_engine(auth_key: str|bytes, salt_key: str|bytes)->Fernet:
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
    def encrypt_jsfile(dc: dict, path_config: str, auth_key: str|bytes, salt_key: str|bytes):
        """
            Déchiffre les données d'un fichier et les retourne.
    
            Args:
            fs (str): Le chemin du fichier contenant les données chiffrées.
    
            Returns:
            str: Les données déchiffrées.
        """

        fernet = CryptoManager.fernet_engine(auth_key, salt_key)
        document = json.dumps(dc)
        sensitive_data = fernet.encrypt(document.encode())

        with open(path_config, 'wb') as file:
            file.write(sensitive_data)

    @staticmethod
    def decrypt_jsfile(path_config:str, auth_key: str|bytes, salt_key: str|bytes):
        """
            Déchiffre les données d'un fichier et les retourne.

            Args:
            fs (str): Le chemin du fichier contenant les données chiffrées.

            Returns:
            str: Les données déchiffrées.
        """
        fernet = CryptoManager.fernet_engine(auth_key, salt_key)

        with open(path_config, 'rb') as file:
            encrypted_data = file.read()

        sensitive_data = fernet.decrypt(encrypted_data).decode()

        return json.loads(sensitive_data)