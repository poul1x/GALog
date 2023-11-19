from re import Pattern
from typing import List, Optional, Union

from pydantic import (
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    model_validator,
)
from pydantic.types import Annotated, StringConstraints
from typing_extensions import Literal

NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
ColorHexRgb = Annotated[str, StringConstraints(pattern=r"#[0-9a-fA-F]{6}")]
VersionString = Annotated[str, StringConstraints(pattern=r"\d+\.\d+\.\d+")]

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

FormattingEntry = Literal[
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


def validate_at_least_one_key_set(fields: dict):
    if all(not x for x in fields.values()):
        keys = "{%s}" % ", ".join(fields.keys())
        msg = "At least one property must be set: %s" % keys
        raise ValueError(msg)


class ColorEntry(BaseModel):
    value: Union[ColorName, ColorHexRgb]
    alpha: NonNegativeFloat = 1.0


class LogMessageColors(BaseModel):
    foreground: Optional[ColorEntry] = None
    background: Optional[ColorEntry] = None

    @model_validator(mode="after")
    def at_least_one_set(cls, obj: "ColorEntry"):
        validate_at_least_one_key_set(obj.model_dump())
        return obj


class StyleEntry(BaseModel):
    colors: Optional[LogMessageColors] = None
    formatting: Optional[List[FormattingEntry]] = None

    @model_validator(mode="after")
    def at_least_one_set(cls, obj: "StyleEntry"):
        validate_at_least_one_key_set(obj.model_dump())
        return obj


class HRuleConfigEntry(BaseModel):
    name: NonEmptyStr
    pattern: Pattern
    style: StyleEntry
    priority: NonNegativeInt = 500

    # None -> Highlight match
    # [] -> Highlight all groups
    # [1,2,3] -> Highlight groups 1,2,3
    groups: Optional[List[PositiveInt]] = None


class HRulesConfig(BaseModel):
    rules: List[HRuleConfigEntry]
    version: VersionString
