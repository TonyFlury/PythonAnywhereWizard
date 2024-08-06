import logging
import enum

logging.basicConfig(format='%(name)s - %(levelname)s : %(message)s')

class Verbosity(enum.IntEnum):
    ZERO = logging.WARNING,
    ONE = logging.INFO,
    TWO = logging.INFO-1,
    THREE = logging.INFO-2


# Mapping between Verbosity levels and logging levels
logging_levels = {0 : Verbosity.ZERO,
                  1 : Verbosity.ONE,
                  2 : Verbosity.TWO,
                  3 : Verbosity.THREE}


logging.addLevelName(Verbosity.TWO, 'INFO+')
logging.addLevelName(Verbosity.THREE, 'INFO++')


class WizardLogger( logging.getLoggerClass()):
    # Define a custom class to support the new logging levels
    def __init__(self, name:str):
        super().__init__(name)

    def info_v1(self, *args, **kwargs):
        self.info( *args, **kwargs)

    def info_v2(self, *args, **kwargs):
        self.log( level = Verbosity.TWO, *args, **kwargs)

    def info_v3(self, *args, **kwargs):
        self.log( level = Verbosity.THREE, *args, **kwargs)


logging.setLoggerClass(WizardLogger)

logger = logging.getLogger('PythonAnywhereWizard')
logger.setLevel(logging.DEBUG)

