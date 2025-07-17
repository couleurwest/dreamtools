from src.dreamtools.exception_manager import AccountException
from tests import fixation
from . import TrackingManager


def test_tracking_info(fixation):
    TrackingManager.info_tracking('# test 1 : Réussi', 'Test info tracking')


def test_tracking_warning(fixation):
    TrackingManager.info_tracking('# test 2 : Réussi', 'Test info tracking')


def test_tracking_exception(fixation):
    try:
        TrackingManager.flag('# test 3 : Réussi')
        raise Exception('Raised exception')
    except Exception as exception:
        TrackingManager.exception_tracking(exception, 'Test exception tracking')


def test_tracking_custom_exception(fixation):
    try:
        TrackingManager.flag('# test 4 : Réussi')
        raise AccountException()
    except Exception as exception:
        TrackingManager.exception_tracking(exception, 'Test custom exception tracking')
