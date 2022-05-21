from dataclasses import dataclass


@dataclass
class OptionColour:
    emoji: str
    colour: int


option_colours = [
    OptionColour("🟦", 0x55ACEE),
    OptionColour("🟥", 0xDD2E44),
    OptionColour("🟨", 0xFDCB58),
    OptionColour("🟩", 0x78B159),
    OptionColour("🟪", 0xAA8ED6),
    OptionColour("🟧", 0xF4900C),
]


def get_colour(index: int) -> OptionColour:
    return option_colours[index % len(option_colours)]


BLURPLE = 0x6F85D5
