# -*- coding: utf-8 -*-
# dreamtools-dreamgeeker/tracking_manager.py
import asyncio
import inspect
import logging
import logging.config as log_config

from . import file_manager
from . import toolbox
from .config_manager import ConfigController
from .controller_manager import ControllerEngine
from .exception_manager import ExceptionManager, Reponce


class TrackingManager:
    tracker: logging.Logger
    system_tracker: logging.Logger = None
    LOG_TRACKED = ''

    @staticmethod
    def initialisation(path_cfg='.cfg/logcfg', logger='PRODUCTION', **params):
        """Initialisation du gestionnaire de log à partir de la configuration enregistré

        .. warning::
            La configuration doit être configurer dans le fichier <PROJECT_DIR>/cdg/.log.yml

        :Exemple:cls
            >>> TrackingManager.initialisation('/projet/dir', path_cfg='.cfg/log.yml', logger='debug')
        """
        if not ControllerEngine.PROJECT_DIR:
            toolbox.print_err('Initialisation manquante')
            return False

        try:

            log_path = file_manager.path_build(ControllerEngine.PROJECT_DIR, path_cfg)
            file_manager.makedirs(log_path)
            cfg = ConfigController.loading(log_path)

            for f_handler in ['file_info', 'file_system']:
                f_p = cfg['handlers'][f_handler]['filename']
                if params.get('project_name'):
                    path_dir = f'logs/{params.get('project_name')}/'
                    cfg['handlers'][f_handler]['filename'] = f_p.replace('logs/', path_dir)
                    file_manager.makedirs(path_dir)

            log_config.dictConfig(cfg)
            TrackingManager.tracker = logging.getLogger(logger)
            TrackingManager.system_tracker = logging.getLogger("system")

        except Exception as e:
            toolbox.print_err(e, ': ', 'Error in Logging Configuration. Using default configs')
            logging.basicConfig(level=logging.NOTSET)

    @staticmethod
    def msg_tracking(msg, title, log_level=logging.INFO):
        """ Tracking message

        :param str msg: message à ecrire dans logs
        :param str title: Titre ou référence associé au message
        :param int log_level: LOG LEVEL Niveau de l'alert (DEBUG | INFO | WARN | )

        """

        TrackingManager.tracker.log(log_level, msg, exc_info=True, stack_info=False, stacklevel=2,
                                    extra={'title': title, 'stacklevel': 2})

    @staticmethod
    def alert_tracking(msg, title):
        """ Message d'alerte (WARNING)

        :param str msg: message à ecrire dans logs
        :param str title: Titre ou référence associé au message
        """
        TrackingManager.msg_tracking(msg, title, logging.WARNING)

    @staticmethod
    def info_tracking(msg, title):
        """ Message d'info (INFO)

        :param str msg: message à ecrire dans logs
        :param str title: Titre ou référence associé au message
        """

        TrackingManager.msg_tracking(msg, title, logging.INFO)

    @staticmethod
    def error_tracking(msg, title):
        """ Message d'error (ERROR)
        :param str msg: message à ecrire dans logs
        :param str title: Titre ou référence associé au message
        """
        TrackingManager.msg_tracking(msg, title, logging.ERROR)

    @staticmethod
    def critical_tracking(msg, title):
        """ Message dcritique (CRITIQUE)
        :param str msg: message à ecrire dans logs
        :param str title: Titre ou référence associé au message
        """
        TrackingManager.msg_tracking(msg, title, logging.CRITICAL)

    @staticmethod
    def flag(trace):
        """ Permet de pointer la dernier action

        :param str trace: Action à enregistrer
        """
        TrackingManager.LOG_TRACKED = trace

    @staticmethod
    def exception_tracking(ex, title: str, status=500) -> ExceptionManager:
        """
        Récupération et traitement des exceptions

        :param status: 
        :param ex: Exception
        :param str title: Information
        """

        try:
            status = getattr(ex, 'status', status) or status
            if TrackingManager.LOG_TRACKED != '':
                if TrackingManager.system_tracker:
                    TrackingManager.system_tracking('## ' + TrackingManager.LOG_TRACKED + ' ##', title, logging.INFO)
                    TrackingManager.msg_tracking('## ' + TrackingManager.LOG_TRACKED + ' ##', title, logging.INFO)
                TrackingManager.LOG_TRACKED = ''

            if isinstance(ex, ExceptionManager):
                TrackingManager.error_tracking(ex.message, ex.title)
                return ex
            else:
                TrackingManager.error_tracking(str(ex), title)
                return ExceptionManager(str(ex), title)

        except Exception as sex:
            toolbox.print_err('*****************  Erreur système *****************: \n', str(sex))
            toolbox.print_err('** Erreur interceptée : ', str(ex))
            return ExceptionManager(str(ex), status=status)

    @staticmethod
    def fntracker(fn, action, *args, **kwargs):
        """ Execution "securisé" d'une fonction avec gestions des erreurs
        
        :param fn: fonction a executer
        :param action: Titre de l'execution pour tracabilité
        :param args: argument de la fonction
        :param kwargs: parametres supplementaire (status par defaut en cas de reussite)
        :rtype: CReponder

        :Exemple:
            >>> r = TrackingManager.fntracker(fn, 'Test de convertion int', 'j')
            >>> r.response
            {'message': "invalid literal for int() with base 10: 'j'", 'data': None, 'status_code': 500}
            >>> r = TrackingManager.fntracker(fn, 'Test de convertion int', '589321')
            >>> r.response
            {'message': None, 'data': 589321, 'status_code': 200}
        """

        try:
            TrackingManager.flag('{}'.format(action))
            if inspect.iscoroutinefunction(fn):
                r = asyncio.run(fn(*args, **kwargs))
            else:
                r = fn(*args, **kwargs)

            return r if isinstance(r, Reponce) else Reponce("Action réussi", action, 200, r)

        except Exception as ex:
            return TrackingManager.exception_tracking(ex, action)

    @staticmethod
    def system_tracking(msg, title, log_level=logging.WARNING):
        """ Tracking message
        :param str msg: message à ecrire dans logs
        :param str title: Titre ou référence associé au message
        :param int log_level: LOG LEVEL Niveau de l'alert (DEBUG | INFO | WARN | )
        """
        TrackingManager.system_tracker.log(log_level, msg, extra={'title': title})
