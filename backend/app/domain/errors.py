class DomainError(Exception):
    pass


class EmailAlreadyRegisteredError(DomainError):
    pass


class TermsNotAcceptedError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class NotAuthenticatedError(DomainError):
    pass


class TooManyLoginAttemptsError(DomainError):
    pass


class CheckinNotFoundError(DomainError):
    pass


class CheckinAlreadyExistsError(DomainError):
    pass
