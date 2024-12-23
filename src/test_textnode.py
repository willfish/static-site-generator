import unittest

from textnode import TextNode, TextType

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

        self.assertEqual(repr(node), "TextNode(\"This is a text node\", TextType.BOLD, None)")

        node = TextNode("This is a text node", TextType.BOLD, "https://google.com")

        self.assertEqual(repr(node), "TextNode(\"This is a text node\", TextType.BOLD, \"https://google.com\")")
