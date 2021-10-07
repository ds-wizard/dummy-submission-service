import yaml

from typing import List

from dummy_submitter.consts import DEFAULT_LOG_LEVEL, DEFAULT_LOG_FORMAT


class MissingConfigurationError(Exception):

    def __init__(self, missing: List[str]):
        self.missing = missing


class ServiceConfig:

    def __init__(self, code: str):
        self.code = code


class SecurityConfig:

    def __init__(self, enabled: bool, tokens: List[str]):
        self.enabled = enabled
        self.tokens = frozenset(tokens)


class LoggingConfig:

    def __init__(self, level, message_format: str):
        self.level = level
        self.format = message_format


class SubmitterConfig:

    def __init__(self, service: ServiceConfig, security: SecurityConfig,
                 logging: LoggingConfig):
        self.service = service
        self.security = security
        self.logging = logging


class SubmitterConfigParser:

    DEFAULTS = {
        'service': {
            'code': 'unknown',
        },
        'security': {
            'enabled': False,
            'tokens': [],
        },
        'logging': {
            'level': DEFAULT_LOG_LEVEL,
            'format': DEFAULT_LOG_FORMAT,
        },
    }

    REQUIRED = [
        ['service', 'code']
    ]

    def __init__(self):
        self.cfg = dict()

    def has(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return False
            x = x[p]
        return True

    def _get_default(self, *path):
        x = self.DEFAULTS
        for p in path:
            x = x[p]
        return x

    def get_or_default(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return self._get_default(*path)
            x = x[p]
        return x

    def validate(self):
        missing = []
        for path in self.REQUIRED:
            if not self.has(*path):
                missing.append('.'.join(path))
        if len(missing) > 0:
            raise MissingConfigurationError(missing)

    @property
    def _service(self):
        return ServiceConfig(
            code=self.get_or_default('service', 'code'),
        )

    @property
    def _security(self):
        return SecurityConfig(
            enabled=self.get_or_default('security', 'enabled'),
            tokens=self.get_or_default('security', 'tokens'),
        )

    @property
    def _logging(self):
        return LoggingConfig(
            level=self.get_or_default('logging', 'level'),
            message_format=self.get_or_default('logging', 'format'),
        )

    def parse_file(self, fp) -> SubmitterConfig:
        self.cfg = yaml.full_load(fp)
        self.validate()
        return self.config

    @property
    def config(self) -> SubmitterConfig:
        return SubmitterConfig(
            service=self._service,
            security=self._security,
            logging=self._logging,
        )


cfg_parser = SubmitterConfigParser()
