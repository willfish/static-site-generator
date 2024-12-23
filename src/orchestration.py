from htmlnode import LeafNode, ParentNode
from textnode import TextNode, TextType
from functools import reduce

import re

image_or_link_regex = re.compile(r"(!?)\[(.*?)\]\((.*?)\)")
block_type_regexes = {
    "heading": re.compile(r"(^#{1,6}) (.*)"),
    "code": re.compile(r"```(\w+)?(.*?\n)?```", flags=re.DOTALL),
    "quote": re.compile(r"^(>)(.*?)(?=\n|$)", flags=re.MULTILINE),
    "unordered_list": re.compile(r"^(-|\*) (.*)(?=\n|$)", flags=re.MULTILINE),
    "ordered_list": re.compile(r"^(\d+|\*). (.*)(?=\n|$)", flags=re.MULTILINE),
    "paragraph": re.compile(r".*"),
}

def extract_title(doc):
    title_parts = re.findall(r"(^# )(.*)", doc, re.MULTILINE)

    if title_parts:
        _, title = title_parts[0]
    else:
        raise ValueError("Missing title from markdown document")

    return title

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
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

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter, text_type):
    def accumulate_nodes(acc: list, node):
        if node.text_type == TextType.TEXT:
            candidate_nodes = node.text.split(delimiter)
            candidate_node_count = len(candidate_nodes)

            balanced = candidate_node_count % 2 != 0

            if balanced and candidate_node_count == 1:
                acc.append(node)
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
        else:
            new_nodes.append(node)

    return new_nodes

def text_to_textnodes(text):
    initial_text_node = TextNode(text, TextType.TEXT)

    split = split_nodes_with_source([initial_text_node])
    split = split_nodes_delimiter(split, "**", TextType.BOLD)
    split = split_nodes_delimiter(split, "*", TextType.ITALIC)
    split = split_nodes_delimiter(split, "`", TextType.CODE)

    return split

def block_to_block_type(block):
    for block_type, matcher in block_type_regexes.items():
        matches = matcher.findall(block)
        if matches:
            return block_type

def markdown_to_blocks(doc) -> list[str]:
    blocks = (doc or "").split("\n\n")

    return list(map(lambda block: block.strip(), blocks))

def block_to_html_node(block: str):
    blocktype = block_to_block_type(block)
    matcher = block_type_regexes[blocktype]
    matches = matcher.findall(block)

    tag = ""
    children = []
    props = {}

    match blocktype:
        case "heading":
            heading_level, heading_text = matches[0]
            tag = f"h{len(heading_level)}"
            text_nodes = text_to_textnodes(heading_text)
            children = list(map(text_node_to_html_node, text_nodes))
        case "code":
            language, content = matches[0]
            tag = "pre"

            if language:
                props = {"class": f"highlight-source-{language}"}

            children = [LeafNode("code", content)]
        case "quote":
            tag = "blockquote"
            content = block.replace(">", "").strip()
            text_nodes = text_to_textnodes(content)
            children = list(map(text_node_to_html_node, text_nodes))
        case "unordered_list":
            tag = "ul"
            list_items_content = map(lambda match: match[1], matches)
            children = list(map(list_content_to_html_list_item, list_items_content))
        case "ordered_list":
            tag = "ol"
            list_items_content = map(lambda match: match[1], matches)
            children = list(map(list_content_to_html_list_item, list_items_content))
        case "paragraph":
            tag = "p"
            text_nodes = text_to_textnodes(block)
            children = list(map(text_node_to_html_node, text_nodes))

    return ParentNode(tag, children, props)

def list_content_to_html_list_item(content):
    text_nodes = text_to_textnodes(content)
    children = list(map(text_node_to_html_node, text_nodes))

    return ParentNode("li", children)

def markdown_to_html_node(doc):
    blocks = markdown_to_blocks(doc)
    children = list(map(block_to_html_node, blocks))
    content = ParentNode("div", children)

    return content
