#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import copy
import json
import re


def check_and_fix_notebook(path, fix=False, default_metadata=None, dry_run=False, is_build=False):
    if not path.endswith(".ipynb"):
        return f"Not a notebook file: {path}"
    with open(path, "r") as f:
        input_file = json.load(f)
    basename = path.split("/")[-1]
    output_file = copy.deepcopy(input_file)

    # Regex patterns for both code and markdown cells
    empty_pat = re.compile(r"\s*")
    trim_begin_nl_pat = re.compile(r"^\n+")
    trim_end_nl_pat = re.compile(r"\n+$")
    trim_space_pat = re.compile(r"^(.*\S|)[ 　]+$", re.MULTILINE)
    trim_space_each_pat = re.compile(r"^(.*\S|)[ 　]+$")

    # Regex patterns for markdown cells
    md_header_pat = re.compile(r"^#+\s+.*$", re.MULTILINE)
    md_header_only_pat = re.compile(r"^((#+\s+.*|\[(.+)\]\:\s?#.*|)\n?)+$")
    md_trim_consec_nl_pat = re.compile(r"(```.*?```)|\n{3,}", re.DOTALL)
    md_trim_end_pat = re.compile(r"\n\n\[END\]: #$")

    def replace_consecutive_newlines(match):
        if match.group(1):
            return match.group(1)
        else:
            return "\n\n"

    cells, corrected = [], False

    # Check notebook-level metadata
    if default_metadata is not None:
        if output_file.get("metadata", {}) != default_metadata:
            message = f"Notebook's metadata issue found in {basename} ({output_file.get('metadata', {})})"
            if fix:
                corrected = True
                output_file["metadata"] = default_metadata
            else:
                return message

    for cell_id, cell in enumerate(output_file["cells"]):
        # Check if the cell has empty metadata
        metadata = cell.get("metadata", {})
        if len(metadata) > 0:
            message = f"Cell metadata issue found at cell #{cell_id + 1} in {basename} ({metadata})"
            if fix:
                print(message)
                corrected = True
                cell["metadata"] = {}
            else:
                return message

        # Check if there are empty cells
        if empty_pat.fullmatch(cell_content := "".join(cell["source"])):
            message = f"Empty cell found at cell #{cell_id + 1} in {basename}."
            if fix:
                print(message)
                corrected = True
                continue
            else:
                return message

        # Check and fix leading newlines
        if res := trim_begin_nl_pat.search(cell_content := "".join(cell["source"])):
            message = f"Leading newlines found in cell #{cell_id + 1} in {basename} ({repr(res.group(0))})."
            if fix or is_build:
                print(message)
                corrected = True
                # remove leading newlines
                cell_content = cell_content[res.end() :]
                cell["source"] = cell_content.splitlines(keepends=True)
            else:
                return message

        # Check if there are trailing newlines
        if res := trim_end_nl_pat.search(cell_content := "".join(cell["source"])):
            message = f"Trailing newlines found in cell #{cell_id + 1} in {basename} ({repr(res.group(0))})."
            if fix or is_build:  # Always fix trailing newlines during build
                print(message)
                corrected = True
                new_source = cell_content[: res.start()].splitlines(keepends=True)
                cell["source"] = new_source
            else:
                return message

        # Check if there is trailing whitespace in each line of markdown cells
        if res := trim_space_pat.search("".join(cell["source"])):
            message = f"Trailing whitespace found in cell #{cell_id + 1} in {basename} ({repr(res.group(0))})."
            if fix or is_build:
                print(message)
                corrected = True
                new_source = []
                for line in cell["source"]:
                    new_line = trim_space_each_pat.sub(r"\1", line)
                    new_source.append(new_line)
                cell["source"] = new_source
            else:
                return message

        if cell.get("cell_type", "") == "markdown":
            # Check whether header cells contain only headers in markdown cells
            cleaned_source = re.sub(r"```.*?```", "", "".join(cell["source"]), flags=re.DOTALL)
            if res := md_header_pat.search(cleaned_source):
                if not md_header_only_pat.fullmatch(cleaned_source):
                    message = (
                        f"Non-header content found in header cell #{cell_id + 1} in {basename} ({repr(res.group(0))})."
                    )
                    if fix:
                        print(f"Warning: {message}. But not fixed.")
                    else:
                        return message

            # Check if there are consecutive newlines in markdown cells
            cell_content = "".join(cell["source"])
            new_content = md_trim_consec_nl_pat.sub(replace_consecutive_newlines, cell_content)
            if new_content != cell_content:
                message = f"Consecutive newlines found in cell #{cell_id + 1} in {basename}."
                if fix or is_build:
                    print(message)
                    corrected = True
                    new_source = new_content.splitlines(keepends=True)
                    cell["source"] = new_source
                else:
                    return message

            # Check if there are redundant `[END]: #`` at the end of markdown cells
            if res := md_trim_end_pat.search(cell_content := "".join(cell["source"])):
                message = f"Redundant `[END]: #` found in cell #{cell_id + 1} in {basename} ({repr(res.group(0))})."
                if fix:
                    print(message)
                    corrected = True
                    new_source = cell_content[: res.start()].splitlines(keepends=True)
                    cell["source"] = new_source
                else:
                    return message

        if cell.get("cell_type", "") == "code":
            # Check if execution_count is null and outputs is empty in code cells
            if cell.get("execution_count", None) is not None:
                message = f"Non-null execution_count found in code cell #{cell_id + 1} in {basename}."
                if fix:
                    print(message)
                    corrected = True
                    cell["execution_count"] = None
                else:
                    return message

            # Check if outputs is empty in code cells
            if cell.get("outputs", []) != []:
                message = f"Non-empty outputs found in code cell #{cell_id + 1} in {basename}."
                if fix:
                    print(message)
                    corrected = True
                    cell["outputs"] = []
                else:
                    return message
        cells.append(cell)

    if corrected and (not dry_run):
        output_file["cells"] = cells
        with open(path, "w") as f:
            json.dump(output_file, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"Fixed notebook saved to {basename}\n")
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pathes", type=str, nargs="+")
    parser.add_argument("--python_version_file", type=str, default="./.python-version")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--dry_run", action="store_true")
    parser.add_argument("--is_build", action="store_true")
    args, unknown = parser.parse_known_args()
    with open(args.python_version_file, "r") as f:
        python_version = f.read().strip()
    default_metadata = {
        "kernelspec": {"display_name": f"rc-bootcamp ({python_version})", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": python_version},
    }
    for path in args.pathes:
        assert (
            res := check_and_fix_notebook(
                path, fix=args.fix, default_metadata=default_metadata, dry_run=args.dry_run, is_build=args.is_build
            )
        ) is None, res
