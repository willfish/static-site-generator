import unittest

from htmlnode import LeafNode
from textnode import (
    TextNode,
    TextType,
    split_nodes_delimiter,
    split_nodes_with_source,
    text_node_to_html_node,
)

class TestTextNode(unittest.TestCase):
    equal_cases = [
        [
            ("This is a text node", TextType.BOLD, None),
            ("This is a text node", TextType.BOLD, None),
            True
        ],
        [
            ("This is a text node", TextType.BOLD),
            ("This is a text node", TextType.BOLD),
            True
        ],
        [
            ("This is not a text node", TextType.BOLD),
            ("This is a text node", TextType.BOLD),
            False
        ],
        [
            ("This is a text node", TextType.NORMAL),
            ("This is a text node", TextType.BOLD),
            False
        ],
        [
            ("This is a text node", TextType.NORMAL, "https:/google.com" ),
            ("This is a text node", TextType.BOLD),
            False
        ],
    ]

    def test_eq(self):
        for node_1_inputs, node_2_inputs, expected_equivalent in self.equal_cases:
            node = TextNode(*node_1_inputs)
            node2 = TextNode(*node_2_inputs)
            actual_equivalent = node == node2

            assert(expected_equivalent == actual_equivalent)

    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD)

        self.assertEqual(repr(node), "TextNode(This is a text node, TextType.BOLD, None)")



# def text_node_to_html_node(text_node):
#     match text_node.type:
#         case TextType.NORMAL:
#             return LeafNode(None, text_node.text)
#         case TextType.BOLD:
#             return LeafNode("b", text_node.text)
#         case TextType.ITALIC:
#             return LeafNode("i", text_node.text)
#         case TextType.CODE:
#             return LeafNode("code", text_node.text)
#         case TextType.LINK:
#             return LeafNode("a", text_node.text, { "href": text_node.url })
#         case TextType.IMAGE:
#             return LeafNode("img", "", { "src": text_node.url, "alt": text_node.text })
#         case _:
#             raise ValueError("Unknown type")

class TestTextNodeToHtmlNode(unittest.TestCase):
    text_to_html_node_cases = [
        (
            TextNode("Normal text", TextType.NORMAL),
            LeafNode(None, "Normal text"),
        ),
        (
            TextNode("Bold text", TextType.BOLD),
            LeafNode("b", "Bold text"),
        ),
        (
            TextNode("Italic text", TextType.ITALIC),
            LeafNode("i", "Italic text"),
        ),
        (
            TextNode("lambda x: x * x", TextType.CODE),
            LeafNode("code", "lambda x: x * x"),
        ),
        (
            TextNode("Some link text", TextType.LINK, "https://www.google.com"),
            LeafNode("a", "Some link text", { "href": "https://www.google.com"}),
        ),
        (
            TextNode("Image alt text", TextType.IMAGE, "/path/to/image.png"),
            LeafNode("img", "", { "src": "/path/to/image.png", "alt": "Image alt text"}),
        ),
        (
            TextNode("Something odd has happened", "foo", "/something/something"),
            "ValueError('Unknown type')"
        )
    ]

    def test_text_to_html_node(self):
        for text_node, expected_leaf_node in self.text_to_html_node_cases:
            try:
                result = text_node_to_html_node(text_node)
            except ValueError as e:
                result = repr(e)


            self.assertEqual(
                result,
                expected_leaf_node
            )

class TestSplitNodesDelimiter(unittest.TestCase):
    split_nodes_delimiter_cases = [
        # No tokens to split
        (
            [TextNode("Some text", TextType.TEXT)],
            "*",
            TextType.BOLD,
            [TextNode("Some text", TextType.TEXT)]
        ),
        # No splitting due to unparsed text_type
        (
            [TextNode("Some text", TextType.BOLD)],
            "*",
            TextType.BOLD,
            [TextNode("Some text", TextType.BOLD)]
        ),
        # Splitting unbalanced bold text
        (
            [TextNode("Some *text", TextType.TEXT)],
            "*",
            TextType.BOLD,
            "ValueError('Unbalanced inline markdown node')"
        ),
        # Splitting multiple unbalanced bold delimiters
        (
            [TextNode("Some *text* and *some other text", TextType.TEXT)],
            "*",
            TextType.BOLD,
            "ValueError('Unbalanced inline markdown node')"
        ),
        # Splitting balanced bold delimiters
        (
            [TextNode("Some *text*", TextType.TEXT)],
            "*",
            TextType.BOLD,
            [
                TextNode("Some ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode("", TextType.TEXT),
            ],
        ),
        # Splitting multiple balanced bold delimiters
        (
            [TextNode("Some *text* and *some other bold* text", TextType.TEXT)],
            "*",
            TextType.BOLD,
            [
                TextNode("Some ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("some other bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        ),
    ]

    def test_split_nodes_delimiter(self):
        for text_node, delimiter, text_type, expected_nodes in self.split_nodes_delimiter_cases:
            try:
                result = split_nodes_delimiter(text_node, delimiter, text_type)
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, expected_nodes)

class TestSplitNodesWithSourceDelimiter(unittest.TestCase):
    split_nodes_with_source_cases = [
        (
            [
                TextNode(
                    "A [link](https://foo.bar) can be a nice place to have ![pandas](/assets/panda.png)",
                    TextType.TEXT
                ),
            ],
            [
                TextNode(
                    "A ",
                    TextType.TEXT
                ),
                TextNode(
                    "link",
                    TextType.LINK,
                    "https://foo.bar"
                ),
                TextNode(
                    " can be a nice place to have ",
                    TextType.TEXT,
                ),
                TextNode(
                    "pandas",
                    TextType.IMAGE,
                    "/assets/panda.png"
                ),
            ],
        ),
        (
            [
                TextNode(
                    "Some random text with no *links* or images",
                    TextType.TEXT
                ),
            ],
            [
                TextNode(
                    "Some random text with no *links* or images",
                    TextType.TEXT
                ),
            ],
        )
    ]

    def test_split_nodes_with_source(self):
        for text_nodes, expected_nodes in self.split_nodes_with_source_cases:
            try:
                result = split_nodes_with_source(text_nodes)
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, expected_nodes)

if __name__ == "__main__":
    unittest.main()
