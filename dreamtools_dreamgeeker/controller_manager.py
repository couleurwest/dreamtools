_all_ = ['ControllerEngine']
from . import file_manager


class ControllerEngine:
    APP_NAME = ''
    PROJECT_DIR = ''
    APP_DIR = ''
    TMP_DIR = ''

    @staticmethod
    def initialize(project_name:str, application_path:str):
        ControllerEngine.APP_NAME = project_name
        ControllerEngine.APP_DIR = application_path
        ControllerEngine.PROJECT_DIR = file_manager.parent_directory(application_path)
        ControllerEngine.TMP_DIR = file_manager.path_build(ControllerEngine.PROJECT_DIR, '.tmp')
        file_manager.makedirs(ControllerEngine.TMP_DIR)

