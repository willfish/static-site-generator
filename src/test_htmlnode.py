import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    props_to_html_cases = [
        (
            (
                "a",
                "A link somewhere",
                [],
                {"href": "https://www.google.com", "target": "_blank"}
            ),
            ' href="https://www.google.com" target="_blank"',
        ),
        (
            (
                "p",
                "Some text about something",
                [],
                {}
            ),
            ''
        ),
        (
            (
                "p",
                "Some text about something",
                [],
            ),
            ''
        )
    ]

    def test_props_to_html(self):
        for inputs, expected_props in self.props_to_html_cases:
            node = HTMLNode(*inputs)

            self.assertEqual(node.props_to_html(), expected_props)

    equal_cases = [
        [
            ("b", "Some text", [], {}),
            ("b", "Some text", [], {}),
            True
        ],
        [
            ("b", "Some text", []),
            ("b", "Some text", []),
            True
        ],
        [
            ("b", "Some text", []),
            ("i", "Some text", []),
            False
        ],
        [
            ("b", "Some text", []),
            ("b", "Some other text", []),
            False
        ],
        [
            ("b", "Some text", [HTMLNode("a", "b", [], {})]),
            ("b", "Some text", []),
            False
        ],
    ]

    def test_eq(self):
        for node_1_inputs, node_2_inputs, expected_equivalent in self.equal_cases:
            node = HTMLNode(*node_1_inputs)
            node2 = HTMLNode(*node_2_inputs)
            actual_equivalent = node == node2

            assert(expected_equivalent == actual_equivalent)

    def test_repr(self):
        node = HTMLNode("b", "Some text", [], {})

        self.assertEqual(repr(node), "HTMLNode(b, Some text, [], {})")


class TestLeafNode(unittest.TestCase):
    to_html = [
        (
            (
                "a",
                "A link somewhere",
                {"href": "https://www.google.com", "target": "_blank"}
            ),
            '<a href="https://www.google.com" target="_blank">A link somewhere</a>',
        ),
        (
            (
                "p",
                "Some text about something",
                {}
            ),
            '<p>Some text about something</p>'
        ),
        (
            (
                None,
                "Some text about something",
            ),
            "Some text about something"
        )
    ]

    def test_to_html(self):
        for inputs, expected_html in self.to_html:
            node = LeafNode(*inputs)

            self.assertEqual(node.to_html(), expected_html)

class TestParentNode(unittest.TestCase):
    bold_child = LeafNode("b", "Bold text")
    normal_child = LeafNode(None, "Normal text")
    italic_child = LeafNode("i", "italic text")

    to_html_cases = [
        (
            ParentNode("p", [bold_child, normal_child, italic_child, normal_child]),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        ),
        (
            ParentNode("p", [LeafNode("b", "Bold text")]),
            "<p><b>Bold text</b></p>"
        ),
        (
            ParentNode("p", []),
            "ValueError('Must have children')"
        ),
        (
            ParentNode(None, []),
            "ValueError('Must have a tag')"
        ),
        (
            ParentNode(
                "div",
                [
                    normal_child,
                    ParentNode(
                        "div",
                        [
                            ParentNode(
                                "p",
                                [
                                    bold_child,
                                    normal_child,
                                ]
                            ),
                            bold_child,
                        ]
                    ),
                    italic_child,
                ]
            ),
            "<div>Normal text<div><p><b>Bold text</b>Normal text</p><b>Bold text</b></div><i>italic text</i></div>"
        ),
    ]

    def test_to_html(self):
        for node, expected_html in self.to_html_cases:
            try:
                result = node.to_html()
            except Exception as e:
                result = repr(e)

            self.assertEqual(result, expected_html)

if __name__ == "__main__":
    unittest.main()
