# -*- coding: utf-8 -*-

"""
Module de fonctions basiques
=============================

Liste de fonctions utiles

pathfile : dreamtools-dreamgeeker/tools

Constantes globales
--------------------
.. note::

    * RGX_ACCENTS = 'àâäãéèêëîïìôöòõùüûÿñç'
    * RGX_EMAIL = Expression reguliere email
    * RGX_PUNCT = Caractere speciaux autorisé pour mot de passe
    * RGX_PWD = Expression régulière pour un mot de passe de 8 à 12 avec un car.Special/une Majuscule/Une minuscule
    * RGX_PHONE = Expression réguliere remative à un numéro de téléphon
    * RGX_URL = expression reguliere pour URL
    * *PROJECT_DIR*  : Repertoire du projet
    * *APP_NAME* : Nom de l'application
    * *APP_DIR* : PROJECT_DIR/APP_NAME
    * *TMP_DIR* : PROJECT_DIR/tmp

.. warning::
    Il faut configurer l'application afin d'avoir accès au variable PROJECT_DIR, APP_NAME, TMP_DIR

"""
import ast
import base64
import random
import re
import sys
from random import choice, randint
from string import punctuation, ascii_letters, digits
from urllib.parse import urlparse

import dns.resolver
import httpx
from bs4 import BeautifulSoup

RGX_ACCENTS = 'àâäãéèêëîïìôöòõùüûÿñç'
RGX_PUNCT = '#!?$%&_@*+-'

RGX_EMAIL = r'^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$'
RGX_PWD = fr'.*(?=.{{8,12}})(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[{RGX_PUNCT}]).*'
RGX_PHONE = r'^0[1-9]\d{8}$'
RGX_URL = r'https?:\/\/(www\.)?[-a-z0-9@:%._\+~#=]{1,256}\.[a-z0-9()]{1,6}\b([-a-z0-9()@:%_\+.~#?&//=]*)'


import pyperclipfix

def clipboard_copy():
    pyperclipfix.copy('The text to be copied to the clipboard.')
def clipboard_paste():
    pyperclipfix.paste()
'The text to be copied to the clipboard.'

def print_err(*args, **kwargs):
    """Ecriture sur le flux erreur de la console

    :param args: arguments 1
    :param kwargs: arguemnts2
    """
    print(*args, file=sys.stderr, **kwargs)


def get_string(v):
    """ Convertion d'une valeur en chaine

    :param v: valeur à convertir
    :rtype: str, None en cas d'erreur

    """
    return str(v) if v else ''


def clean_space(ch):
    """ Nettoyage des espaces "superflus"

    * Espaces à gouche et à droite supprimés
    * Répétition d'espace réduit

    :Exemple:
        >>> chaine = 'Se  réveiller au matin        de sa destiné    ! !           '
        >>> clean_space (chaine)
        'Se réveiller au matin  de sa destiné ! !'

    """
    s = get_string(ch)
    return re.sub(r'\s{2,}', ' ', s.strip())


def clean_allspace(ch, very_all=True):
    """Nettoyage de tous les espace et carateres vides

    :param str ch: Chaine à nettoyer
    :param bool very_all: caractère vide aussi, True (False = Espaces uniquement)

    :Exemple:
        >>> chaine = 'Se  réveiller au matin        de sa destiné !'
        >>> clean_allspace (chaine)
        'Seréveilleraumatindesadestiné!'

    """
    c = r'\s' if very_all else '[ ]'
    s = get_string(ch)

    return re.sub(c, '', s.strip())


def clean_coma(ch, w_punk=False):
    """ Supprime les accents/caractères spéciaux du texte source en respectant la casse

    :param ch: Chaine de caractere à "nettoyer"
    :param w_punk: indique si la punctuation est à nettoyer ou pas (suppression)

    :Exemple:
        >>> s = 'Se  réveiller au matin    de sa destiné !!'
        >>> clean_coma (s)
        'Se seveiller au matin (ou pas) de sa destine !!''
        >>> clean_coma (s, True)
        'Se reveiller au matin ou pas de sa destine'

    """

    if w_punk:
        # Nettoyage caractere spéciaux (espace...)
        o_rules = str.maketrans(RGX_ACCENTS, 'aaaaeeeeiiioooouuuync', punctuation)
    else:
        o_rules = str.maketrans(RGX_ACCENTS, 'aaaaeeeeiiioooouuuync')

    return clean_space(ch).translate(o_rules).swapcase().translate(o_rules).swapcase()


def clean_master(ch):
    """ Supprime les accents, caractères spéciaux et espace du texte source

    :param str ch: Chaine de caractere à "nettoyer"
    :return str: chaine sans accents:car. spéciaux ni espace en minuscule

    :Exemple:
        >>> s = 'Se  réveiller au matin  (ou pas) de sa destiné !'
        >>> clean_master (s)
        'sereveilleraumatinoupasdesadestine

    """
    return clean_allspace(clean_coma(ch, True)).lower()


def int_to_hexa(v):
    """ Conversion d'une valeur en hexadécimal

    :param int v: nombre à convertir
    :returns: valeur en hexadécimal
    :rtype: str

    """
    return hex(int(v))


def add_hexa(h, v):
    """Additionne une valeur hexadécimal

    :param str h: valeur hexadécimal
    :param int v: valeur entière à ajouter
    :return: valeur additionné en hexedécimal

    :Example:
        >>> hx = '0x129'
        >>> add_hexa(hx, 2)
        0x12b

    """

    v += int(h, 16)
    return hex(v)


def compare_hex(hx_a, hx_b):
    """Compare deux valeurs  hexadécimales

    :param str hx_a:
    :param str hx_b:

    :return int:
        * 0 : hx_a == hx_b
        * 1 : hx_a > hx_b
        * -1 : hx_a < hx_b
    """
    v = int(hx_a, 16) - int(hx_b, 16)

    if v == 0:
        return 0
    else:
        return -1 if v < 0 else 1


def plain_hex(hx, s=3):
    """ Complète un chiffre hexadecimal en préfixant une valeur de zéro

    :param str hx: valeur hexadécimal
    :param int s: longeur chaine attendu
    :rtype: str:

    :Examples:
        >>> hxi = '0x129'
        >>> plain_hex(hxi, 5)
        0x00129

    """
    return hx[:2] + plain_zero(hx[2:], s)


def plain_zero(v, s):
    """Complete une valeur chaine de zéro

    :param v: valeur à completer
    :param s: taille chaine attendu préfixé de zerom

    :Exemple:
        >>> d = 5
        >>> plain_zero(d,3)
        '005'

    """

    s = '{:0>' + str(s) + '}'
    return s.format(v)


def check_password(s):
    """ Vérifie que la syntaxe d'une chaine répond au critère d'un mot de passe

    : Conditions :
        * Une majuscule
        * Une minuscule
        * Un chiffre
        * Un caractère spécial (@#!?$&-_ autorisé)

    :param str s: chaine à vérifier
    :return bool: True si la chaine est valide
    """
    r = re.compile(RGX_PWD)
    return r.match(s)


def pwd_maker(i_size=12):
    """ Génération d'un password respectant les regles de password

    : Conditions :
        * deux majuscules
        * deux minuscules
        * deux chiffres
        * deux caractères spé&ciaux (@#!?$&-_ autorisés)

    :param int i_size: Nombre de caractères de la chaine
    :return: Mot de passe
    """

    l_t = list(ascii_letters + digits + RGX_PUNCT)
    password = ''
    s_chaine = ''

    while not check_password(password):
        s = choice(l_t)
        s_chaine += s
        password = s_chaine[-i_size:]
    return s_chaine



def code_maker(n=None):
    if n is None:
        n = random.randint(6, 24)
    alphabet = ascii_letters + digits
    return ''.join(choice(alphabet) for _ in range(n))


def random_number(end, s=1):
    """ Génération d'un nombre aléatoire entre [1-end]  end caractère

    :param int end: valeur maximale (paut indiquer la taille si s=1)
    :param s: valeur de départ, default to 1
    :return: Un chiffre aléatoire

    : Exemple :
        >>> random_number (5)
        1 : Renvoie un chiffre entre 1 et 5
        >>> random_number (5,3)
        1 : Renvoie un chiffre entre 3 et 5
        >>> 4

    """
    return randint(s, end)


def append_to_list(v, ll: list):
    """ Ajout d'un item dans une liste avec gestion des doublons

    :param str v: valeur à ajouter
    :param list ll: liste

    """
    if v not in ll:
        ll.append(v)


def dictlist(k, v, d: dict):
    """ Ajout d'une valeur dans une liste d'un dictionnaire

    :param str k: clé dictionnaire
    :param v: valeur à ajouter
    :param dict[str, list[]] d: dictionnaire

    : Exemple :
        >>> dictionnaire= {}
        >>> dictlist('printemps', 'mar', dictionnaire)
        dictionnaire{'printemps', ['mars']}
        >>> dictlist('printemps', 'avril', dictionnaire)
        dictionnaire{'printemps', ['mars', ''avril']}
        >>> dictlist('printemps', 'mars', dictionnaire)
        dictionnaire{'printemps', ['mars', ''avril']}

    """
    if k is None or v is None: return

    if k not in d:
        d[k] = [v]
    elif v not in d[k]:
        d[k].append(v)


def str_to_dic(chaine: str) -> dict:
    """Convertion d'une chaine en dictionnaire

    :param str chaine:
    :rtype: dc

    :Exemple:
        >>> s_dic = "{'key':value}"
        >>> str_to_dic(s_dic)
        {'key': 'value'}

    """
    return ast.literal_eval(chaine)


def pop_dic(l_ids: list, dc: dict):
    """ Suppression d'une liste d'éléments d'un dictionnaire

    :param list l_ids : liste de clé à supprimer
    :param dict dc: dictionaire à nettoyer

    """
    if dc:
        for s in l_ids:
            if s in dc: del dc[s]


def find_key(value, dc: dict):
    """Recherche une clé d'un dictionnaire à partir de sa valeur"""

    for k, v in dc.items():
        if v == value:
            return k
    return None


def html_to_text(html: str) -> str:
    """
    Extrait le texte brut d'un contenu HTML et nettoie les espaces.

    :param html: Chaîne HTML à traiter
    :return: texte brut nettoyé

    Exemple :
        >>> html_to_text('<p>Hello <b>world</b> !</p>')
        'Hello world !'
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(strip=True)
    return clean_space(text)


def is_empty(item):
    return (item is None) or (len(item) == 0)


def find_email(s):
    reg_email = re.compile(RGX_EMAIL)
    return list(map(lambda tp: tp[0], reg_email.findall(s)))


def has_mx_record(domain: str) -> bool:
    try:
        records = dns.resolver.resolve(domain, "MX")
        return len(records) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        return False


def is_valid_email(v: str) -> bool:
    try:
        v = clean_allspace(v).lower()
        if re.fullmatch(RGX_EMAIL, v):
            domain = v.split('@')[-1]
            return has_mx_record(domain)
    except Exception as ex:
        print(ex)
    return False


def is_valid_password(v: str) -> bool:
    v = clean_space(v)
    return bool(re.fullmatch(RGX_PWD, v))


def is_valid_url(link: str) -> bool:
    # Force ajout du schéma si manquant
    if not link.startswith(('http://', 'https://')):
        link = f'https://{link}'

    url = clean_allspace(link).lower()
    if not re.fullmatch(RGX_URL, url):
        return False

    domain = urlparse(url).netloc
    if not domain:
        return False

    if is_valid_domain(domain):
        return verify_link(url)

    return False


def is_valid_domain(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, "A")  # IPv4
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except dns.resolver.NoAnswer:  # Essaye avec AAAA si pas de réponse IPv4
        try:
            dns.resolver.resolve(domain, "AAAA")  # IPv6
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
            return False
    except (dns.resolver.NoNameservers, dns.exception.Timeout):
        return False


def verify_link(url: str, max_redirects: int = 3) -> str | bool:
    """
    Vérifie une URL HTTP/HTTPS et renvoie l'URL finale valide, ou False si invalide.

    :param url: URL à tester (ex : 'example.com')
    :param max_redirects: Nombre maximum de redirections autorisées
    :return: URL fonctionnelle (str) ou False
    """

    s = clean_allspace(url)

    try:
        with httpx.Client(follow_redirects=False, timeout=10.0) as client:
            for _ in range(max_redirects):
                response = client.head(s)
                if response.status_code in (301, 302) and "location" in response.headers:
                    s = response.headers["location"]
                    continue

                # Fallback GET si HEAD renvoie 405 ou comportement suspect
                if response.status_code in (405, 403, 400):
                    response = client.get(s)

                return s if response.is_success else False

            return False  # Trop de redirections
    except httpx.RequestError:
        return False


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


def init_and_set_dict(dc, key, value):
    if dc is None:
        dc = {}

    dc[key] = value


def dictionary(dictionnaire):
    document = None

    if type(dictionnaire) is dict:
        document = {k: dictionary(v) for k, v in dictionnaire.items() if v}
    elif type(dictionnaire) is list:
        document = [dictionary(v) for v in dictionnaire]
    elif dictionnaire is not None:
        try:
            document = dict(dictionnaire)
        except TypeError:
            document = dictionnaire

    return document


def ensure_bytes(element: str | bytes | bytearray) -> bytes:
    if isinstance(element, bytes):
        return element
    if isinstance(element, bytearray):
        return bytes(element)
    if isinstance(element, str):
        return element.encode("utf-8")  # ou "ascii" si tout est ASCII
    raise TypeError(f"Unsupported type: {type(element)}")


def ensure_string(element: str | bytes | bytearray) -> str:
    if isinstance(element, str):
        return element
    try:
        return element.decode("utf-8")
    except UnicodeDecodeError:
        return base64.b64encode(element).decode()
