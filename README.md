# 🛠️ dreamtools

**Outils Python pour projets professionnels**  
Validation, manipulation de chaînes, traitement d’images, journalisation, gestion d’erreurs, envoi d’e-mails, etc.

Ce module propose une collection de fonctions utilitaires conçues pour accélérer le développement d'applications robustes, fiables et facilement maintenables, en particulier dans des environnements exigeants (sécurité, supervision, automatisation).

---

## 📦 Installation

```bash
pip install .
dreamtools-dreamgeeker-init
```

⚠️ À l'installation, des fichiers de configuration nécessaires au fonctionnement (log + mailing) seront copiés automatiquement dans le répertoire courant du projet (dans un sous-dossier .config/).
Ces fichiers doivent impérativement être revus et adaptés avant toute utilisation des fonctionnalités de mail ou de journalisation avancée.

## ⚙️ Configuration requise

dreamtools repose sur deux fichiers principaux à adapter selon ton projet :

### 📝 Journalisation (.config/log.yml)

Fichier de configuration du logger Python. Nécessaire pour que TrackingManager fonctionne.

```python
from dreamtools import file_manager
from dreamtools.controller_manager import ControllerEngine
from dreamtools.tracking_manager import TrackingManager

application_name = "mon_app"
application_directory = file_manager.execution_directory()

ControllerEngine.initialize(application_name, application_directory)

log_config_path = file_manager.path_build(ControllerEngine.APP_DIR, 'configuration/log.yml')
TrackingManager.initialisation(log_config_path, logger='development', project_name=application_name)
```

### 📬 Modèles d'e-mail (.config/mailing.yml)

Fichier YAML regroupant les templates d’e-mails transactionnels et le footer.


```python
from dreamtools import file_manager
from dreamtools.controller_manager import ControllerEngine
from dreamtools.mailing_manager import MailController

class APPControllerEngine(ControllerEngine):
    mailer:MailController
    
mail_template_path = file_manager.path_build(APPControllerEngine.APP_DIR, 'config/mailing.yml')

APPControllerEngine.mailer = MailController(
    smtp_url='smtp.exemple.net',
    smtp_port=587,
    smtp_mail='bot@monapp.net',
    smtp_password='motdepasse',
    path_templates=mail_template_path,
    SMTP_USER_NAME='Assistant numérique'
)
```

Les modèles peuvent être dupliqués, personnalisés ou déplacés : il suffira de renseigner le bon chemin dans path_templates.

## 📁 Structure

```bash
dreamtools-dreamgeeker/
├── .config/                # Fichiers de configuration par défaut (copiés dans le projet)
│   ├── mailing.yml         # Templates d'e-mail personnalisables
│   └── log.yml             # Configuration du logger
├── __init__.py
├── config_manager
├── controller_manager  
├── crypting_manager  
├── date_manager  
├── exception_manager # Exceptions métiers avec suivi
├── file_manager  
├── image_manager   # Traitement d’images (Pillow)
├── mailing_manager 
├── toolbox  # Fonctions utilitaires diverses
├── tracking_manager  
├── validators_manager  # Validation (emails, URL, etc.)
```

## 🪪 Licence

### MIT License / Licence MIT

Copyright (c) 2025 Couleur West IT

La licence MIT vous autorise à utiliser, copier, modifier, fusionner, publier, distribuer, sous-licencier et/ou vendre des copies du logiciel, sous réserve d’inclure la notice de droit d’auteur et la permission dans toutes les copies ou parties substantielles.

The MIT License permits use, copy, modification, merge, publication, distribution, sublicensing, and/or selling copies of the software, provided the copyright notice and permission are included in all copies or substantial portions.

Le logiciel est fourni "TEL QUEL", sans garantie d’aucune sorte.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

## ✨ Auteur

Développé par **Couleur West IT**.

Outils pensés pour les environnements complexes : sécurité, validation, traitement léger et fiable.



