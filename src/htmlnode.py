from functools import reduce


class HTMLNode():
    def __init__(self, tag: str | None, value: str | None, children: list, props: dict = {}):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        raise NotImplementedError()

    def props_to_html(self) -> str:
        return reduce(lambda acc, item: acc + f" {item[0]}=\"{item[1]}\"", self.props.items(), "")

    def start_tag_html(self) -> str:
        if self.props:
            return f"<{self.tag}{self.props_to_html()}>"
        else:
            return f"<{self.tag}>"

    def end_tag_html(self) -> str:
        return f"</{self.tag}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.tag == other.tag and self.value == other.value and self.children == other.children

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag: str | None, value: str, props: dict = {}):
        super().__init__(tag, value, [], props)

    def to_html(self) -> str:
        if self.value:
            if self.tag:
                return f"{self.start_tag_html()}{self.value}{self.end_tag_html()}"
            else:
                return self.value
        else:
            raise ValueError("All leaf nodes must have a value")

class ParentNode(HTMLNode):
    def __init__(self, tag: str, children: list, props: dict = {}):
        super().__init__(tag, None, children, props)

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("Must have a tag")

        if not self.children:
            raise ValueError("Must have children")

        children_html =  reduce(lambda acc, n: acc + n.to_html(), self.children, "")

        return f"{self.start_tag_html()}{children_html}{self.end_tag_html()}"
