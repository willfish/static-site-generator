import os
import shutil

from orchestration import extract_title, markdown_to_html_node

def copy(paths, current_path, destination):
    for path in paths:
        fully_qualified_path = os.path.join(current_path, path)

        if os.path.isdir(fully_qualified_path):
            copy(os.listdir(fully_qualified_path), fully_qualified_path, destination)
        else:
            fully_qualified_destination = os.path.join(destination, *fully_qualified_path.split("/")[1:])
            os.mkdir(os.path.dirname(fully_qualified_destination))
            shutil.copy(fully_qualified_path, fully_qualified_destination)


def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)

def generate_page(from_path, to_path, template_path):
    print(f"Generating page from {from_path} to {to_path} using {template_path}")

    markdown = open(from_path, "r").read()
    page = open(template_path, "r").read()
    title = extract_title(markdown)
    content = markdown_to_html_node(markdown).to_html()
    page = page.replace("{{ Title }}", title)
    page = page.replace("{{ Content }}", content)

    with open(to_path, "w") as f:
        f.write(page)

def generate_pages(dir_path_content, template_path, dest_dir_path, current_path):
    for path in dir_path_content:
        from_path = os.path.join(current_path, path)

        if os.path.isdir(from_path):
            generate_pages(
                os.listdir(from_path),
                template_path,
                dest_dir_path,
                from_path,
            )
        else:
            to_path = os.path.join(
                dest_dir_path,
                *from_path.split("/")[1:]
            )

            to_dir = os.path.dirname(to_path)

            if not os.path.exists(to_dir):
                os.mkdir(to_dir)

            if to_path.endswith(".md"):
                to_path = to_path.replace(".md", ".html")

            generate_page(
                from_path,
                to_path,
                template_path
            )

def main():
    clear_directory("public")
    copy(
        os.listdir("static"),
        "static",
        "public"
    )
    generate_pages(
        os.listdir("content"),
        "template.html",
        "public",
        "content"
    )

if __name__ == '__main__':
    main()
