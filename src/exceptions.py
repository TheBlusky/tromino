class TrominoException(Exception):
    pass


class MonitorAlreadyExists(TrominoException):
    pass


class ParameterAlreadyExists(TrominoException):
    pass


class JobAlreadyStarted(TrominoException):
    pass


class JobNotStarted(TrominoException):
    pass


class UnknownNotificationType(TrominoException):
    pass


class InvalidInterval(TrominoException):
    pass


class InvalidName(TrominoException):
    pass


class InvalidType(TrominoException):
    pass


class TooMuchArgument(TrominoException):
    pass


class NoSuchMonitor(TrominoException):
    pass


class InvalidCustomConf(TrominoException):
    pass
