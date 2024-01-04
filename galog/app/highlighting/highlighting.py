from collections import defaultdict
from dataclasses import dataclass
from re import Pattern
from typing import Dict, List, Optional

import yaml
from PyQt5.QtGui import QColor, QFont, QTextCharFormat

from .errors import RuleAlreadyExistsError, RuleNotFoundError
from .model import (
    HighlightingRuleModel,
    HighlightingRulesetModel,
    RegexGroupsHighlightingModel,
    TextColorModel,
    TextHighlightingModel,
)


@dataclass
class HighlightingRule:
    pattern: Pattern
    match: Optional[QTextCharFormat]
    groups: Optional[Dict[int, QTextCharFormat]]
    priority: int


class HighlightingRules:
    _rules: Dict[str, HighlightingRule]

    def __init__(self) -> None:
        self._rules = dict()

    def _loadColors(self, colors: TextColorModel):
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
                assert item in fontWeights
                charFormat.setFontWeight(fontWeights[item])

        return charFormat

    def _loadTextHighlighting(self, hl: TextHighlightingModel):
        charFormat = QTextCharFormat()
        if hl.colors:
            charFormat.merge(self._loadColors(hl.colors))
        if hl.formatting:
            charFormat.merge(self._loadFormatting(hl.formatting))

        return charFormat

    def _loadTextHighlightingForGroups(
        self, rulesetForGroups: List[RegexGroupsHighlightingModel]
    ):
        charFormatDict = defaultdict(QTextCharFormat)
        for groupsRule in rulesetForGroups:
            charFormat = self._loadTextHighlighting(groupsRule.highlighting)
            for groupNum in groupsRule.numbers:
                charFormatDict[groupNum].merge(charFormat)

        return dict(charFormatDict)

    def _loadRule(self, rule: HighlightingRuleModel):
        name = rule.name
        if name in self._rules:
            msg = f"Rule '{name}' already exists"
            raise RuleAlreadyExistsError(msg)

        assert not (rule.highlighting is None and rule.groups is None)
        match = self._loadTextHighlighting(rule.highlighting) if rule.highlighting else None  # fmt: skip
        groups = self._loadTextHighlightingForGroups(rule.groups) if rule.groups else None  # fmt: skip
        self._rules[name] = HighlightingRule(rule.pattern, match, groups, rule.priority)

    def addRuleset(self, filepath: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            config = HighlightingRulesetModel.model_validate(data)
            for rule in config.rules:
                self._loadRule(rule)

        except Exception as e:
            print("Failed to load rules from %s" % filepath)

    def findRule(self, name: str):
        rule = self._rules.get(name)
        if not rule:
            raise RuleNotFoundError(f"Rule '{name}' not found")
        return rule

    def items(self):
        return self._rules.items()
