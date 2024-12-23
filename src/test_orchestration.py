import unittest

from htmlnode import LeafNode
from textnode import TextNode, TextType
from orchestration import (
    block_to_block_type,
    extract_title,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_with_source,
    text_node_to_html_node,
    text_to_textnodes,
)

class TestOrchestration(unittest.TestCase):
    extract_title_cases = [
        (
            """
            # Some title

            Embedded in a document somehow
            """,
            "Some title"
        ),
        (
            """
            Some text without a title # Some time

            Hmm what shall we do
            """,
            "ValueError('Missing title from markdown document')"
        )
    ]

    def test_extract_title(self):
        for doc, expected in self.extract_title_cases:
            doc = doc.strip()
            try:
                result = extract_title(doc)
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, expected)

    text_to_html_node_cases = [
        (
            TextNode("Normal text", TextType.TEXT),
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
        (
            [
                TextNode("This is **text** with an *italic* word and a `code block` and an ", TextType.TEXT, None),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT, None),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            "**",
            TextType.BOLD,
            [
                TextNode("This is ", TextType.TEXT, None),
                TextNode("text", TextType.BOLD, None),
                TextNode(" with an *italic* word and a `code block` and an ", TextType.TEXT, None),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT, None),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )
    ]

    def test_split_nodes_delimiter(self):
        for text_node, delimiter, text_type, expected_nodes in self.split_nodes_delimiter_cases:
            try:
                result = split_nodes_delimiter(text_node, delimiter, text_type)
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, expected_nodes)

    split_nodes_with_source_cases = [
        (
            [
                TextNode(
                    "A [link](https://foo.bar) can be a nice place to have ![pandas](/assets/panda.png)",
                    TextType.TEXT
                ),
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

    text_to_textnodes_cases = [
        (
            "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)",
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ]
        ),
        (
            "",
            []
        )
    ]

    def test_text_to_textnodes(self):
        for text, expected_nodes in self.text_to_textnodes_cases:
            try:
                result = text_to_textnodes(text)
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, expected_nodes)

    markdown_to_blocks_cases = [
        (
            """
# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

  * This is the first list item in a list block
* This is a list item
* This is another list item
            """,
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                "* This is the first list item in a list block\n* This is a list item\n* This is another list item",
            ]
        )
    ]

    def test_split_nodes_with_source(self):
        for doc, blocks in self.markdown_to_blocks_cases:
            try:
                result = markdown_to_blocks(doc)
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, blocks)

    block_to_block_type_cases = [
        ("# This is a heading", "heading"),
        ("## This is a heading", "heading"),
        ("### This is a heading", "heading"),
        ("#### This is a heading", "heading"),
        ("##### This is a heading", "heading"),
        ("###### This is a heading", "heading"),
        ("####### This is no longer a heading", "paragraph"),
        ("This is a paragraph", "paragraph"),
        (
"""
```ruby
def the_better_language
  puts "But not as widely adopted or packed with libraries"
end
```
""",
            "code"
        ),
        (
"""
```
```
""",
            "code"
        ),
        (
"""
```ruby
```
""",
            "code"
        ),
        (
            """
> something quoted
> across lines
            """,
            "quote"
        ),
        (
            """
- a bullet
- can be useful
            """,
            "unordered_list"
        ),
        (
            """
* a bullet
* can be useful
            """,
            "unordered_list"
        ),
        (
            """
1. order
1. over chaos
            """,
            "ordered_list"
        )
    ]

    def test_split_nodes_with_source(self):
        for block, expected_block_type in self.block_to_block_type_cases:
            try:
                result = block_to_block_type(block)
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, expected_block_type)

    markdown_to_html_node_cases = [
        (
"""
# Introduction to ruby

Ruby is a `great` language that *all* people should know.
The syntax is **clean** and the `concepts` are consistently object oriented like
small talk.

Get started with the following example

```ruby
def the_better_language
  puts "But not as widely adopted or packed with libraries"
end
```

> I recommend doing *serious* examples in ruby
> Instead of in **python** which is an inferior language

## Requirements

- ruby
- `neovim`

Sometimes we like to ask questions about the language:

1. Why is **ruby** better than *python*?
2. Under which circumstances will our bias come clear?

### This has been **fun**

Thanks for listening. Reach me at [my website](https://tibbs.fun) or see my face ![some ugly mug](/path/to/my/ugly/mug.png)
""",
            open("src/fixtures/markdown_to_html_node.html", "r").read().strip()
        )
    ]

    def test_markdown_to_html_node_cases(self):
        for doc, expected_html in self.markdown_to_html_node_cases:
            try:
                result = markdown_to_html_node(doc).to_html()
            except ValueError as e:
                result = repr(e)

            self.assertEqual(result, expected_html)



if __name__ == "__main__":
    unittest.main()
