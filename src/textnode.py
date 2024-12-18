from enum import Enum
from htmlnode import LeafNode
from functools import reduce

import re

image_or_link_regex = re.compile(r"(!?)\[(.*?)\]\((.*?)\)")

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

def split_nodes_with_source(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            split_text_images_and_links = image_or_link_regex.split(node.text)

            kind = "text"
            node_parts = []
            parts_counter = 0

            for split in split_text_images_and_links:
                if parts_counter == 0:
                    if split == '':
                        kind = 'link'

                        parts_counter += 1
                    elif split == '!':
                        kind = 'image'

                        parts_counter += 1
                    else:
                        kind = 'text'

                        new_nodes.append(TextNode(split, TextType.TEXT))
                elif parts_counter == 1:
                    node_parts.append(split)
                    parts_counter += 1
                elif parts_counter == 2:
                    parts_counter = 0

                    if kind == "image":
                        text_type = TextType.IMAGE
                    else:
                        text_type = TextType.LINK

                    node_parts.append(text_type)
                    node_parts.append(split)

                    new_node = TextNode(*node_parts)
                    new_nodes.append(new_node)

                    node_parts = []

            return new_nodes
        else:
            new_nodes.append(node)

    pass
