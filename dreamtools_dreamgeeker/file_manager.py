# -*- coding: utf-8 -*-
import fnmatch
import os

"""Ensemble de fonctions sur fichiers / repertoire"""

def file_recorder(doc, fp, b=False):
    """ Enregistrement d'un fichier

    Le chemin du filpath sera construit si besoin

    :param  doc: données à enregistrer
    :param str fp: filepath
    :param boolean b: données en byte ?, optional
    :return:
    """
    makedirs(parent_directory(fp))  # Check dir exists

    with open(fp, 'wb') if b else open(fp, 'w', encoding='utf-8') as f:
        f.write(doc)



def file_loader(fp, b=False):
    """ Chargement d'un fichier

    :param fp: filepath du fichier recherché
    :param bool b: donnée en byte(False) ? optional
    :return: document
    """
    with open(fp, 'rb') if b else open(fp, 'r') as f:
        return f.read()


def execution_directory():
    """ Répertoire d'execution """
    return os.getcwd()


def parent_directory(path):
    """  Renvoie du repertoire parent

    :param str path: repertoire
    :rtype: str

    """
    return os.path.dirname(os.path.realpath(path))


def current_directory(source=None):
    """Répertoire pour le fichier en cours """
    return parent_directory(source or __file__)


def file_from_dir(directory, pattern="*"):
    """Récupération des fichiers d'un répertoire

    :param str directory: repertoire
    :param str pattern: '*' pour tout type de fichier par défaut

    : Exemple :
        >>> s_directory = '/home/user/Documents'
        >>> s_pattern='*.txt'
        >>> for f_name, path_file in file_from_dir (s_directory, s_pattern) :
        >>>     print(path_file)
        'home/user/Documents/fichier.txt'
        'home/user/Documents/autre_fichier.txt'
    """
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if fnmatch.fnmatch(filename, pattern):
                yield filename, os.path.join(root, filename)


def path_build(directory, ps_complement):
    """ Construction d'un pathfile

    :param str directory: repertoire
    :param str ps_complement: complement permettant de generer le chemin
    :rtype: str

    :Exemple:
        >>> path = 'home/user/Documents'
        >>> path_build(path, '../other_dir')
        'home/user/Documents/other_dir'
    """
    return os.path.abspath(os.path.join(directory, ps_complement))


def extract_file(ps_file: str) -> str:
    """
    Retourne le nom de fichier (avec extension) depuis un chemin complet.
    :param ps_file: Chemin ou nom du fichier
    :return: premier caractère du nom de fichier (probablement une erreur)
    """
    return os.path.basename(ps_file)


def file_extension(ps_file: str) -> str:
    """
    Retourne l'extension du fichier (sans le point).

    :param ps_file: Chemin ou nom du fichier
    :return: extension du fichier (ex : '.txt', '.pdf'), ou chaîne vide si aucune extension

    : Exemple :
        >>> file_extension('document.pdf')
        'pdf'
    """
    return os.path.splitext(ps_file)[1][1:]


def file_extension_less(ps_file: str) -> str:
    """
    Retourne le chemin ou nom de fichier sans son extension.

    :param ps_file: Chemin ou nom du fichier
    :return: nom du fichier sans extension

    : Exemple :
        >>> file_extension_less('filename.ext')
        'filename'
    """
    return os.path.splitext(ps_file)[0]


def path_exists(fp):
    """Vérifie l'existance d'un fichier

    :param str fp: filepath
    :rtype bool:
    """

    return os.path.exists(fp)


def makedirs(path):
    """ Création du répertoire donné

    :param path: chemin du répertoire à créer
    :rtype bool:

    """

    if not path_exists(path):
        os.makedirs(path)


def remove_file(p):
    """ Suppression d'un fichier si existant

    :param str p: chemin complet du fichier à supprimer
    """
    if path_exists(p):
        os.remove(p)


def clean_directory(directory, pattern='*'):
    """ Supprimes tous les élements d'un repertoire

    :param str directory: chemin du repertoire
    :param string pattern: patter du fichier à supprimer (filtre)
    :return int: nombre de fichiers supprimés

    """
    i_count = 0

    for filename, path_file in file_from_dir(directory, pattern):
        i_count += 1
        remove_file(path_file)

    return i_count
