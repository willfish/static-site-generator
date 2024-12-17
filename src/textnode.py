from enum import Enum
from htmlnode import LeafNode
from functools import reduce

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
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.NORMAL:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, { "href": text_node.url })
        case TextType.IMAGE:
            return LeafNode("img", "", { "src": text_node.url, "alt": text_node.text })
        case _:
            raise ValueError("Unknown type")

# TODO: Nested inline nodes are not supported which is something we can expect in markdown text
def split_nodes_delimiter(old_nodes: list[TextNode], delimiter, text_type):
    def accumulate_nodes(acc: list, node):
        if node.text_type == TextType.TEXT:
            candidate_nodes = node.text.split(delimiter)
            candidate_node_count = len(candidate_nodes)

            balanced = candidate_node_count % 2 != 0

            if balanced and candidate_node_count == 1:
                acc.extend(old_nodes)
            elif balanced:
                for node_index in range(0, len(candidate_nodes)):
                    node_text = candidate_nodes[node_index]
                    odd_node = node_index % 2 != 0

                    # Odd nodes are surrounded by the delimiter
                    if odd_node:
                        node = TextNode(node_text, text_type)
                    else:
                        node = TextNode(node_text, TextType.TEXT)

                    acc.append(node)
            else:
                raise ValueError(f"Unbalanced inline markdown node")
        else:
            acc.append(node)

        return acc

    return reduce(accumulate_nodes, old_nodes, [])
