# -*- coding: utf-8 -*-
# features.py
import os
import shutil
import sys
from pathlib import Path


"""
Module complémentaire
============================
pathfile : dreamtools-dreamgeeker/features.py
"""

def lets_go():
    current_path = Path.cwd()
    config_dest = current_path / "configuration"
    config_source = Path(__file__).parent / ".config"

    os.makedirs(config_dest)
    shutil.copytree(config_source, config_dest)

    if config_dest.exists():
        print("⚠️  Le dossier `.config` existe déjà dans ce répertoire.")
        print("❗ Aucun fichier n’a été écrasé.")
        return

    try:
        shutil.copytree(config_source, config_dest)
        print("✅ Fichiers de configuration copiés dans le dossier `.config` du projet.")
        print("🛠️ Pensez à adapter les fichiers `log.yml` et `mailing.yml` à votre projet.")
    except Exception as e:
        print(f"❌ Erreur lors de la copie : {e}")
        sys.exit(1)