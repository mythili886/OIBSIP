
import re

EMOJI_MAP = {
    ":smile:": "😄",
    ":grin:": "😁",
    ":laugh:": "😂",
    ":heart:": "❤️",
    ":love:": "😍",
    ":sad:": "😢",
    ":cry:": "😭",
    ":angry:": "😠",
    ":cool:": "😎",
    ":thumbsup:": "👍",
    ":thumbsdown:": "👎",
    ":clap:": "👏",
    ":fire:": "🔥",
    ":star:": "⭐",
    ":wave:": "👋",
    ":hello:": "👋",
    ":party:": "🎉",
    ":rocket:": "🚀",
    ":check:": "✅",
    ":ok:": "👌",
    ":thinking:": "🤔",
    ":coffee:": "☕",
    ":sun:": "☀️",
    ":moon:": "🌙"
}


def convert_emojis(message):
    """Convert supported emoji shortcodes into emojis."""
    if not isinstance(message, str):
        return message

    for shortcode, emoji in EMOJI_MAP.items():
        message = message.replace(shortcode, emoji)

    return message


def get_available_emojis():
    """Return all supported emoji shortcodes."""
    return EMOJI_MAP.copy()


if __name__ == "__main__":
    sample = "Hello :smile: :heart: :rocket:"
    print("Original:", sample)
    print("Converted:", convert_emojis(sample))
