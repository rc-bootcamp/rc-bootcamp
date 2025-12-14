#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import copy
import json
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("pathes", type=str, nargs="+")
parser.add_argument("--output_dir", type=str, default="./build")
parser.add_argument("--lang", type=str, default="en")
parser.add_argument("--mode", type=str, default="ex", choices=["ex", "sol"])
args, unknown = parser.parse_known_args()


def convert(path):
    if not path.endswith(".ipynb"):
        return
    with open(path, "r") as f:
        input_file = json.load(f)
    output_file = copy.deepcopy(input_file)

    img_expr = re.compile(r"^\!\[.+\]\(..\/assets\/(.+)\)")
    att_expr = re.compile(r"^\!\[.+\]\(attachment:(.+)\)")
    cmd_expr = re.compile(r"^\[(.+)\]\:\s?#.*")

    blank_expr = re.compile(r"^(\s*)(\S.+\s)# BLANK(|\s.*)$")
    right_expr = re.compile(r"^(\s*.*)(\S*\s[-+*/]?=\s)(.*\s)# RIGHT(|\s.*)$")
    begin_expr = re.compile(r"^(\s*)# BEGIN(|\s.*)$")
    end_expr = re.compile(r"^(\s*)# END(|\s.*)$")
    right_b_expr = re.compile(r"^(\s*)# RIGHT_B(|\s.*)$")
    right_e_expr = re.compile(r"^(\s*)# RIGHT_E(|\s.*)$")
    right_i_expr = re.compile(r"^(\s*.*)(\S*\s[-+*/]?=\s)(.*)$")

    cells = []
    for cell in output_file["cells"]:
        if cell["cell_type"] == "markdown":
            source, is_skip = [], False
            for line in cell["source"]:
                if img_expr.match(line):
                    file_name = img_expr.sub(r"\1", line.strip())
                    ext = file_name.split(".")[-1].lower()
                    with open(f"./assets/{file_name}", "rb") as f:
                        data = base64.b64encode(f.read())
                    line = f'<img src="data:image/{ext};base64,{data.decode()}" alt="{file_name}">'
                    source.append(line)
                    continue
                elif att_expr.match(line):
                    file_name = att_expr.sub(r"\1", line.strip())
                    if "attachments" in cell and file_name in cell["attachments"]:
                        for key in cell["attachments"][file_name]:
                            if key.startswith("image/"):
                                ext = key.split("/")[-1].lower()
                                data = cell["attachments"][file_name][key]
                                line = f'<img src="data:image/{ext};base64,{data}" alt="{file_name}">'
                    cell["attachments"] = {}
                    source.append(line)
                    continue
                elif cmd_expr.match(line):
                    command = cmd_expr.sub(r"\1", line.strip())
                    if len(command) == 2:
                        is_skip = not (args.lang.lower() == command.lower())
                        # print(args.lang.lower(), command.lower(), is_skip)
                    elif command == "END":
                        is_skip = False
                    elif command == "tips":
                        source.append(f"<details><summary>{command}</summary>\n\n")
                    elif command == "/tips":
                        source.append("</details>")
                    elif command == "figc":
                        source.append('<figcaption align = "center">\n')
                    elif command == "/figc":
                        source.append("</figcaption>")
                    # print(repr(command), repr(args.lang), repr(line), is_skip)
                elif not is_skip:
                    source.append(line)
            cell["source"] = source
        if cell["cell_type"] == "code":
            if args.mode == "ex":
                source1, source2, is_skip, is_right = [], [], False, False
                for line in cell["source"]:
                    line = blank_expr.sub(r"\1...  # TODO\3", line)
                    line = right_expr.sub(r"\1\2...  # TODO\4", line)
                    source1.append(line)
                for line in source1:
                    if begin_expr.match(line):
                        line = begin_expr.sub(r"\1# TODO\2", line)
                        source2.append(line)
                        is_skip = True
                    elif end_expr.match(line):
                        line = end_expr.sub(r"\1...", line)
                        source2.append(line)
                        is_skip = False
                        # print(line)
                    elif right_b_expr.match(line):
                        line = right_b_expr.sub(r"\1# TODO\2", line)
                        source2.append(line)
                        is_right = True
                    elif right_e_expr.match(line):
                        line = right_e_expr.sub(r"\1# end of TODO\2", line)
                        source2.append(line)
                        is_right = False
                    else:
                        if not is_skip:
                            if is_right:
                                line = right_i_expr.sub(r"\1\2...", line)
                            source2.append(line)
                cell["source"] = source2
            else:
                source = []
                for line in cell["source"]:
                    line = blank_expr.sub(r"\1\2# TODO\3", line)
                    line = right_expr.sub(r"\1\2\3# TODO\4", line)
                    line = begin_expr.sub(r"\1# TODO\2", line)
                    line = end_expr.sub(r"\1# end of TODO\2", line)
                    line = right_b_expr.sub(r"\1# TODO\2", line)
                    line = right_e_expr.sub(r"\1# end of TODO\2", line)
                    source.append(line)
                cell["source"] = source

            cell["execution_count"] = None
            cell["outputs"] = []
        if cell["cell_type"] == "code":
            project_name = "rc-bootcamp"
            branch_name = f"{args.lang.lower()}"
            if args.mode != "ex":
                branch_name += f"_{args.mode.lower()}"
            source = []
            for line in cell["source"]:
                line = re.sub(r"\[\[PROJECT_NAME\]\]", project_name, line)
                line = re.sub(r"\[\[BRANCH_NAME\]\]", branch_name, line)
                source.append(line)
            cell["source"] = source
        cells.append(cell)
    output_file["cells"] = cells
    # print(f"{args.output_dir}/{os.path.basename(path)}")

    with open(f"{args.output_dir}/{os.path.basename(path)}", "w") as f:
        # print(path)
        json.dump(output_file, f)


if __name__ == "__main__":
    for path in args.pathes:
        convert(path)
