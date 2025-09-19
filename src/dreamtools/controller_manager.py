_all_ = ['ControllerEngine']
from . import file_manager


class ControllerEngine:
    APP_NAME:str
    PROJECT_DIR:str
    APP_DIR:str
    TMP_DIR:str

    @classmethod
    def initialize(cls, project_name:str, application_path:str):
        cls.APP_NAME = project_name
        cls.APP_DIR = application_path
        cls.PROJECT_DIR = file_manager.parent_directory(application_path)
        cls.TMP_DIR = file_manager.path_build(cls.APP_DIR, '.tmp')
        file_manager.makedirs(cls.TMP_DIR)

