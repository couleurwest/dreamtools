# -*- coding: utf-8 -*-
# config_manager.py
_all_ = ['ConfigController']
"""
Gestion fichiers de configurations (YAML)

pathfile : dreamtools-dreamgeeker/config_manager.py

Repertoires par défaut
----------------------


Class CFBases
-------------
"""
import yaml
from yaml import SafeLoader

from . import file_manager

class ConfigController:
    """
    cfg engine
    """

    @classmethod
    def loading(cls, p, ref=None, m='r'):
        """
        Récupération des parameters de configuration du fichier <p> section <r>

        :param str p: Fichier de configuration
        :param str ref: référence parameters à récupérer, optionnels
        :param str m: str|bytes par default
        :return: configuration | None

        """
        config = None

        if file_manager.path_exists(p):
            try:
                with open(p, mode=m) if 'b' in m else open(p, mode=m, encoding='utf-8') as cfg:
                    cfg = yaml.load(cfg, Loader=SafeLoader)
                    if type(cfg) == "dict":
                        cfg = dict(cfg)
                    elif type(cfg).__name__ == "list":
                        cfg = list(cfg)

                    config = cfg.get(ref) if ref else cfg
            except Exception as ex:
                print(f'[Chargement du fichier {p}:\n', ex)
        return config

    @classmethod
    def saving(cls, d, f, m="w"):
        """
        Enregistrement d'un fichier yaml
        ========================================

        :param dict(str, list(str)) d: données à enregistrer
        :param str f: nom du fichier
        :param str m: default (write): mode "w|a", optional
        :return:
        """
        file_manager.makedirs(file_manager.parent_directory(f))

        with open(f, m) if 'b' in m else open(f, mode=m, encoding='utf-8') as f_yml:
            yaml.dump(d, stream=f_yml, allow_unicode=True)

        return f
