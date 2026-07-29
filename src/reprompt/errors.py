"""Exception hierarchy — CLI maps these to distinct exit codes."""


class RepromptError(Exception):
    """Root of the reprompt exception tree."""

    exit_code: int = 1


class ConfigError(RepromptError):
    exit_code = 2


class ModelLoadError(RepromptError):
    exit_code = 3


class GenerationError(RepromptError):
    exit_code = 4


class PostprocessError(RepromptError):
    exit_code = 5


class TargetProfileError(RepromptError):
    exit_code = 6
