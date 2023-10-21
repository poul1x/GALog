from dataclasses import dataclass
import re
from typing import Dict

from PyQt5.QtGui import QTextCharFormat, QColor, QFont


class RuleNotFoundError(Exception):
    pass


class RuleAlreadyExistsError(Exception):
    pass


class RuleParseError(Exception):
    pass


@dataclass
class HighlightingRule:
    pattern: re.Pattern
    style: QTextCharFormat


class HighlightingRules:
    _rules: Dict[str, HighlightingRule]

    def __init__(self) -> None:
        self._rules = dict()

    def _loadName(self, rule: dict):
        try:
            name = str(rule["name"])
        except KeyError as e:
            msg = "Expected key 'name: <example-name>'"
            raise RuleParseError(msg) from e

        return name

    def _loadPattern(self, rule: dict):
        try:
            pattern = re.compile(str(rule["pattern"]))
        except KeyError as e:
            msg = "Expected key 'pattern: <regular-expression>'"
            raise RuleParseError(msg) from e
        except re.error as e:
            name = str(rule["name"])
            msg = f"Invalid pattern '{name}': {e}"
            raise RuleParseError(msg) from e

        return pattern

    def _atLeastOneValueSet(self, data: dict):
        return any(value is not None for value in data.values())

    def _loadColors(self, colors: dict):
        if not self._atLeastOneValueSet(colors):
            msg = "Key 'style.color' has no values set"
            raise RuleParseError(msg)

        for key, val in colors.items():
            if not isinstance(val, str):
                msg = f"Key 'style.formatting.{key}': not a string value"
                raise RuleParseError(msg)
            if not val.startswith("#"):
                msg = f"Key 'style.formatting.{key}': must be in #RRGGBB format"
                raise RuleParseError(msg)

        charFormat = QTextCharFormat()
        foreground = colors.get("foreground")
        background = colors.get("background")

        if foreground:
            try:
                charFormat.setForeground(QColor(foreground))
            except TypeError as e:
                msg = f"Key 'style.color.foreground' is invalid: {e}"
                raise RuleParseError(msg)
        if background:
            try:
                charFormat.setBackground(QColor(background))
            except TypeError as e:
                msg = f"Key 'style.color.background' is invalid: {e}"
                raise RuleParseError(msg)

        return charFormat

    def _loadFormatting(self, formatting: dict):
        if not self._atLeastOneValueSet(formatting):
            msg = "Key 'style.formatting' has no values set"
            raise RuleParseError(msg)

        for key, val in formatting.items():
            if not isinstance(val, bool):
                msg = f"Key 'style.formatting.{key}': not a bool value"
                raise RuleParseError(msg)

        charFormat = QTextCharFormat()
        mediumbold = formatting.get("mediumbold", False)
        demibold = formatting.get("demibold", False)
        bold = formatting.get("bold", False)
        italic = formatting.get("italic", False)
        underline = formatting.get("underline", False)
        strikeout = formatting.get("strikeout", False)

        if mediumbold:
            charFormat.setFontWeight(QFont.Medium)
        if demibold:
            charFormat.setFontWeight(QFont.DemiBold)
        elif bold:
            charFormat.setFontWeight(QFont.Bold)
        else:
            charFormat.setFontWeight(QFont.Normal)

        charFormat.setFontItalic(italic)
        charFormat.setFontUnderline(underline)
        charFormat.setFontStrikeOut(strikeout)

        return charFormat

    def _loadStyle(self, rule: dict):
        try:
            style = rule["style"]
            if not isinstance(style, dict):
                raise RuleParseError("Key 'style': not a dict")
        except KeyError as e:
            msg = "Expected key 'style: <style-dict>'"
            raise RuleParseError(msg) from e

        color = style.get("color")
        formatting = style.get("formatting")
        if not color and not formatting:
            msg = "Expected key 'style.color: <dict>' or 'style.formatting: <dict>'"
            raise RuleParseError(msg)

        charFormat = QTextCharFormat()
        if color is not None:
            charFormat.merge(self._loadColors(color))
        if formatting is not None:
            charFormat.merge(self._loadFormatting(formatting))

        return charFormat

    def _loadRule(self, rule: dict):
        name = self._loadName(rule)
        pattern = self._loadPattern(rule)
        style = self._loadStyle(rule)

        if name in self._rules:
            msg = f"Rule '{name}' already exists"
            raise RuleAlreadyExistsError(msg)

        self._rules[name] = HighlightingRule(pattern, style)

    def load(self, rules: list):
        for rule in rules:
            self._loadRule(rule)

    def _getRule(self, name: str):
        rule = self._rules.get(name)
        if not rule:
            raise RuleNotFoundError(f"Rule '{name}' not found")
        return rule

    def getPattern(self, name: str):
        return self._getRule(name).pattern

    def getStyle(self, name: str):
        return self._getRule(name).style

    def iter(self):
        for name, rule in self._rules.items():
            yield (name, rule.pattern)
