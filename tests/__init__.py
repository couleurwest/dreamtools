import pytest
from dreamtools import file_manager

from src.dreamtools.controller_manager import ControllerEngine
from src.dreamtools.mailing_manager import MailController
from src.dreamtools.tracking_manager import TrackingManager


class Constantine(ControllerEngine):
    mailer:MailController

# 🔧 Fixture d'initialisation principale
@pytest.fixture(scope="session")
def fixation():
    print("# START")
    application_name = "app_name"
    application_directory = file_manager.execution_directory()

    ControllerEngine.initialize(application_name, application_directory)
    print("Initialisation module de log : ")
    path_log = file_manager.path_build(Constantine.APP_DIR, 'konfigurator/log.yml')
    TrackingManager.initialisation(path_log, logger='development', project_name=application_name)

    # Si tu veux faire un nettoyage après
    print("--------------------------------------------------------------")

