import os
import shutil

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

def main():
    clear_directory("public")
    copy(os.listdir("static"), "static", "public")

if __name__ == '__main__':
    main()
