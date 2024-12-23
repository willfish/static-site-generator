from enum import Enum

class TextType(Enum):
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"


class TextNode():
    def __init__(self, text, text_type, url = None) -> None:
        self.text: str = text
        self.text_type = text_type
        self.url: str | None = url

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.text == other.text and self.text_type == other.text_type and self.url == other.url

    def __repr__(self) -> str:
        if self.url:
            url = f"\"{self.url}\""
        else:
            url = self.url

        return f"TextNode(\"{self.text}\", {self.text_type}, {url})"
