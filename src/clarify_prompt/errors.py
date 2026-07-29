"""Exception hierarchy — CLI maps these to distinct exit codes."""


class ClarifyPromptError(Exception):
    """Root of the clarify-prompt exception tree."""

    exit_code: int = 1


class ConfigError(ClarifyPromptError):
    exit_code = 2


class ModelLoadError(ClarifyPromptError):
    exit_code = 3


class GenerationError(ClarifyPromptError):
    exit_code = 4


class PostprocessError(ClarifyPromptError):
    exit_code = 5


class TargetProfileError(ClarifyPromptError):
    exit_code = 6
