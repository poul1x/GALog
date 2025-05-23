from re import Pattern
from typing import List, Optional, Union

from pydantic import (
    AfterValidator,
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    model_validator,
)
from pydantic.types import Annotated, StringConstraints
from typing_extensions import Literal


def validate_non_empty_list(value: list):
    if not value:
        raise ValueError("List must not be empty")
    return value


def validate_at_least_one_key_set(fields: dict):
    if all(not x for x in fields.values()):
        keys = "{%s}" % ", ".join(fields.keys())
        msg = "At least one property must be set: %s" % keys
        raise ValueError(msg)


NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
ColorHexRgb = Annotated[str, StringConstraints(pattern=r"#[0-9a-fA-F]{6}")]
VersionString = Annotated[str, StringConstraints(pattern=r"\d+\.\d+\.\d+")]
GroupNumberList = Annotated[List[PositiveInt], AfterValidator(validate_non_empty_list)]

# fmt: off
ColorName = Literal[
    "aliceblue", "antiquewhite", "aqua", "aquamarine",
    "azure", "beige", "bisque", "black",
    "blanchedalmond", "blue", "blueviolet", "brown",
    "burlywood", "cadetblue", "chartreuse", "chocolate",
    "coral", "cornflowerblue", "cornsilk", "crimson",
    "cyan", "darkblue", "darkcyan", "darkgoldenrod",
    "darkgray", "darkgreen", "darkgrey", "darkkhaki",
    "darkmagenta", "darkolivegreen", "darkorange", "darkorchid",
    "darkred", "darksalmon", "darkseagreen", "darkslateblue",
    "darkslategray", "darkslategrey", "darkturquoise", "darkviolet",
    "deeppink", "deepskyblue", "dimgray", "dimgrey",
    "dodgerblue", "firebrick", "floralwhite", "forestgreen",
    "fuchsia", "gainsboro", "ghostwhite", "gold",
    "goldenrod", "gray", "grey", "green",
    "greenyellow", "honeydew", "hotpink", "indianred",
    "indigo", "ivory", "khaki", "lavender",
    "lavenderblush", "lawngreen", "lemonchiffon", "lightblue",
    "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray",
    "lightgreen", "lightgrey", "lightpink", "lightsalmon",
    "lightseagreen", "lightskyblue", "lightslategray", "lightslategrey",
    "lightsteelblue", "lightyellow", "lime", "limegreen",
    "linen", "magenta", "maroon", "mediumaquamarine",
    "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen",
    "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred",
    "midnightblue", "mintcream", "mistyrose", "moccasin",
    "navajowhite", "navy", "oldlace", "olive",
    "olivedrab", "orange", "orangered", "orchid",
    "palegoldenrod", "palegreen", "paleturquoise", "palevioletred",
    "papayawhip", "peachpuff", "peru", "pink",
    "plum", "powderblue", "purple", "red",
    "rosybrown", "royalblue", "saddlebrown", "salmon",
    "sandybrown", "seagreen", "seashell", "sienna",
    "silver", "skyblue", "slateblue", "slategray",
    "slategrey", "snow", "springgreen", "steelblue",
    "tan", "teal", "thistle", "tomato",
    "turquoise", "violet", "wheat", "white",
    "whitesmoke", "yellow", "yellowgreen",
]
# fmt: on

FormattingKeywords = Literal[
    "thin",
    "light",
    "normal",
    "medium",
    "semibold",
    "bold",
    "italic",
    "underline",
    "overline",
    "strikeout",
]


class ColorValueModel(BaseModel):
    value: Union[ColorName, ColorHexRgb]
    alpha: NonNegativeFloat = 1.0


class TextColorModel(BaseModel):
    foreground: Optional[ColorValueModel] = None
    background: Optional[ColorValueModel] = None

    @model_validator(mode="after")
    def at_least_one_set(cls, obj: "TextColorModel"):
        validate_at_least_one_key_set(obj.model_dump())
        return obj


class TextHighlightingModel(BaseModel):
    colors: Optional[TextColorModel] = None
    formatting: Optional[List[FormattingKeywords]] = None

    @model_validator(mode="after")
    def at_least_one_set(cls, obj: "TextHighlightingModel"):
        validate_at_least_one_key_set(obj.model_dump())
        return obj


class RegexGroupsHighlightingModel(BaseModel):
    numbers: GroupNumberList
    highlighting: TextHighlightingModel


class HRuleModel(BaseModel):
    name: NonEmptyStr
    pattern: Pattern
    priority: NonNegativeInt = 500
    highlighting: Optional[TextHighlightingModel] = None
    groups: Optional[List[RegexGroupsHighlightingModel]] = None

    @model_validator(mode="after")
    def at_least_one_set(cls, obj: "HRuleModel"):
        data = obj.model_dump(include={"highlighting", "groups"})
        validate_at_least_one_key_set(data)
        return obj

    @model_validator(mode="after")
    def validate_group_num_ranges(cls, obj: "HRuleModel"):
        if obj.groups:
            if obj.pattern.groups == 0:
                msg = "Found regexp groups in rule '%s', however the pattern has no groups"
                raise ValueError(msg % obj.name)

            max_group_num = 0
            for group_rule in obj.groups:
                max_group_num = max(max(group_rule.numbers), max_group_num)

            if max_group_num > obj.pattern.groups:
                msg = "Group number (%d) used is out of range (%d-%d) in rule '%s'"
                raise ValueError(msg % (max_group_num, 1, obj.pattern.groups, obj.name))

        return obj


class HRuleSetModel(BaseModel):
    rules: List[HRuleModel]
    version: VersionString
