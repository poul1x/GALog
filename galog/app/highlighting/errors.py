class HighlightingEngineError(Exception):
    pass


class RuleNotFoundError(HighlightingEngineError):
    pass


class RuleAlreadyExistsError(HighlightingEngineError):
    pass


class RuleParseError(HighlightingEngineError):
    pass
