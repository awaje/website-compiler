#!/usr/bin/env python3

import operator
from pathlib import Path
import datetime
import sys
import html
from types import SimpleNamespace


newline = "\n"


config = SimpleNamespace(
    **{
        "prefixes": SimpleNamespace(
            **{
                "raw": "-RAW-",
                "ignore": "-IGNORE-",
                "link": "-LINK-",
            }
        ),
        "ignore": [
            ".DS_Store",
            ".git",
            ".fleet",
            ".idea",
            ".vscode",
        ],
        "username": "awaje",
        "groupname": "awaje",
        "hostname": "awaje",
        "guestname": "guest",
    }
)


def format_path(path: str) -> str:
    if path == "/":
        return "/"
    else:
        return path + "/"


def main():
    if len(sys.argv) < (3 + 1):
        print("please provide directory, base path, and output file")
        quit(1)

    go_through_dir(Path(sys.argv[1]), Path(sys.argv[2]), format_path(sys.argv[3]))


def go_through_dir(
    dir_: Path, base_output: Path, base_path: str, is_first: bool = True
):
    if is_first:
        print("DIR:      " + base_path + " " + str(dir_.absolute()))

        output = open(base_output / "index.html", "w")
        output.write(dir_listing(dir_, base_path))
        output.close()

    for file in dir_.iterdir():
        if file.is_file():
            if config.prefixes.raw in file.name:
                output = open(base_output / file.name[5:], "wb")
                output.write(get_raw(file))
                output.close()
                print(
                    "RAW:      "
                    + base_path
                    + file.name[5:]
                    + " "
                    + str(file.absolute())
                )
            elif file.name in config.ignore or config.prefixes.ignore in file.name:
                print("IGNORING: " + base_path + file.name + " " + str(file.absolute()))
            elif config.prefixes.link in file.name:
                print(
                    "LINK:     "
                    + base_path
                    + file.name[6:]
                    + " "
                    + str(file.absolute())
                )
                print("ERROR: Not Implimented")
            else:
                output = open(base_output / (str(file.name) + ".html"), "w")
                output.write(cat_listing(file, base_path))
                output.close()
                print("FILE:     " + base_path + file.name + " " + str(file.absolute()))

        elif file.is_dir():
            print(
                "DIR:      " + base_path + file.name + "/" + " " + str(file.absolute())
            )
            if not (base_output / file.name).is_dir():
                (base_output / file.name).mkdir()

            output = open(base_output / file.name / "index.html", "w")
            output.write(dir_listing(file, base_path + file.name))
            output.close()

            go_through_dir(file, base_output / file.name, base_path + file.name, False)


def cat_listing(path: Path, base_path: str):
    return put_in_body(
        [ls(path.parent, base_path), cat(path, base_path), prompt(base_path)], base_path
    )


def dir_listing(path: Path, base_path: str):
    return put_in_body([ls(Path(path), base_path), prompt(base_path)], base_path)


def put_in_body(elements: list[str], base_path: str):
    base_path = base_path.strip()
    return f"""<html lang="en">
        <head>
        <title>{config.guestname}@{config.hostname}:~{"" if base_path == "/" else base_path}$</title>
            <link rel="stylesheet" type="text/css" href="/style.css">
        </head>
        <body>
            {newline.join(elements)}
        </body>
    </html>"""


def ls(path: Path, base_path: str) -> str:
    files = []
    lengths = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for file in path.iterdir():
        if file.is_file() and (
            file.name not in config.ignore and not prefix_in_name(file.name)
        ):
            files.append(
                [
                    "-rw-r--r--",
                    "1",
                    config.username,
                    config.groupname,
                    str(file.stat().st_size),
                    datetime.datetime.fromtimestamp(file.stat().st_mtime).strftime(
                        "%b"
                    ),
                    str(datetime.datetime.fromtimestamp(file.stat().st_mtime).day),
                    str(datetime.datetime.fromtimestamp(file.stat().st_mtime).year),
                    file.name,
                ]
            )
        if file.is_dir() and (
            file.name not in config.ignore and not prefix_in_name(file.name)
        ):
            files.append(
                [
                    "drwxr-xr-x",
                    str((sum(1 for _ in file.iterdir()) + 2)),
                    config.username,
                    config.groupname,
                    "4096",
                    datetime.datetime.fromtimestamp(file.stat().st_mtime).strftime(
                        "%b"
                    ),
                    str(datetime.datetime.fromtimestamp(file.stat().st_mtime).day),
                    str(datetime.datetime.fromtimestamp(file.stat().st_mtime).year),
                    file.name,
                ]
            )

    files.append(
        [
            "drwxr-xr-x",
            str((sum(1 for _ in path.iterdir()) + 2)),
            config.username,
            config.groupname,
            "4096",
            datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%b"),
            str(datetime.datetime.fromtimestamp(path.stat().st_mtime).day),
            str(datetime.datetime.fromtimestamp(path.stat().st_mtime).year),
            ".",
        ]
    )

    files.append(
        [
            "drwxr-xr-x",
            str((sum(1 for _ in path.parent.iterdir()) + 2)),
            config.username,
            config.groupname,
            "4096",
            datetime.datetime.fromtimestamp(path.parent.stat().st_mtime).strftime("%b"),
            str(datetime.datetime.fromtimestamp(path.parent.stat().st_mtime).day),
            str(datetime.datetime.fromtimestamp(path.parent.stat().st_mtime).year),
            "..",
        ]
    )

    files = sorted(files, key=operator.itemgetter(-1))

    for row in range(len(files)):
        for col in range(len(files[row])):
            if len(files[row][col]) > lengths[col]:
                lengths[col] = len(files[row][col])

    output = prompt(base_path, "ls -al")

    for row in files:
        output += "<span>"
        for col in range(len(row) - 1):
            output += (
                "&nbsp;" * (lengths[col] - len(row[col])) + html.escape(row[col]) + " "
            )
        if row[0][0] == "d":
            if row[-1] == ".":
                output += f'<a href="{base_path}" class="dir">{html.escape(row[-1])}</a></span><br>\n'
            elif row[-1] == "..":
                output += f'<a href="{base_path.rpartition("/")[0]}/{row[-1]}/" class="dir">{html.escape(row[-1])}</a></span><br>\n'
            else:
                output += f'<a href="{base_path}{row[-1]}/" class="dir">{html.escape(row[-1])}</a></span><br>\n'
        elif row[0][0] == "-":
            output += f'<a href="{base_path}{row[-1]}.html" class="file">{html.escape(row[-1])}</a></span><br>\n'
        else:
            output += f"{html.escape(row[-1])}</span><br>\n"

    return output


def cat(path: Path, base_path: str):
    file = open(path, "r")
    contents = file.read()
    file.close()
    return f"{prompt(base_path, f'cat {path.name}')}<pre>{html.escape(contents)}</pre>"


def get_raw(path: Path, _base_path: str = ""):
    file = open(path, "rb")
    contents = file.read()
    file.close()
    return contents


def prompt(path: str, command: str = ""):
    path = path.strip()
    return f'<span><span class="user">{config.guestname}@{config.hostname}</span>:<span class="path">~{"" if path == "/" else path}</span>${"" if command.strip == "" else " " + command}</span><br>\n'


def prefix_in_name(name: str) -> bool:
    for prefix in config.prefixes.__dict__.values():
        if prefix in name:
            return True
    return False


if __name__ == "__main__":
    main()
