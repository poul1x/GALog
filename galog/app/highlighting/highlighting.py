from dataclasses import dataclass
from typing import Dict, List, Optional
from re import Pattern

from PyQt5.QtGui import QTextCharFormat, QColor, QFont
import yaml

from .model import ColorEntry, HRulesConfig, HRuleConfigEntry, LogMessageColors, StyleEntry
from .errors import RuleAlreadyExistsError, RuleNotFoundError, RuleParseError


class HighlightingMode:
    Match = "match"
    Groups = "groups"


@dataclass
class HighlightingRule:
    pattern: Pattern
    charFormat: QTextCharFormat
    priority: int
    groups: Optional[List[int]]


class HighlightingRules:
    _rules: Dict[str, HighlightingRule]

    def __init__(self) -> None:
        self._rules = dict()

    def _loadColors(self, colors: LogMessageColors):
        charFormat = QTextCharFormat()

        if colors.foreground:
            fgColor = colors.foreground
            foreground = QColor(fgColor.value)
            foreground.setAlphaF(fgColor.alpha)
            charFormat.setForeground(foreground)

        if colors.background:
            bgColor = colors.background
            background = QColor(bgColor.value)
            background.setAlphaF(bgColor.alpha)
            charFormat.setBackground(background)

        return charFormat

    def _loadFormatting(self, formatting: List[str]):
        fontWeights = {
            "thin": QFont.Thin,
            "light": QFont.Light,
            "normal": QFont.Normal,
            "medium": QFont.Medium,
            "semibold": QFont.DemiBold,
            "bold": QFont.Bold,
        }

        charFormat = QTextCharFormat()
        for item in formatting:
            if item == "italic":
                charFormat.setFontItalic(True)
            elif item == "underline":
                charFormat.setFontUnderline(True)
            elif item == "overline":
                charFormat.setFontOverline(True)
            elif item == "strikeout":
                charFormat.setFontStrikeOut(True)
            else:
                charFormat.setFontWeight(fontWeights[item])

        return charFormat

    def _loadStyle(self, style: StyleEntry):
        charFormat = QTextCharFormat()
        if style.colors:
            charFormat.merge(self._loadColors(style.colors))
        if style.formatting:
            charFormat.merge(self._loadFormatting(style.formatting))

        return charFormat

    def _loadRule(self, rule: HRuleConfigEntry):
        name = rule.name
        if name in self._rules:
            msg = f"Rule '{name}' already exists"
            raise RuleAlreadyExistsError(msg)

        charFormat = self._loadStyle(rule.style)
        self._rules[name] = HighlightingRule(
            rule.pattern, charFormat, rule.priority, rule.groups
        )

    def addRuleSet(self, filepath: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            config = HRulesConfig.model_validate(data)
            for ruleEntry in config.rules:
                self._loadRule(ruleEntry)

        except Exception as e:
            print("Failed to load rules from %s" % filepath)

    def findRule(self, name: str):
        rule = self._rules.get(name)
        if not rule:
            raise RuleNotFoundError(f"Rule '{name}' not found")
        return rule

    def items(self):
        return self._rules.items()
