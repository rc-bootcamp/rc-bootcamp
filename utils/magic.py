#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import os

from IPython.core.magic import needs_local_scope, register_cell_magic, register_line_magic


@needs_local_scope
@register_cell_magic
def run_and_save(line, cell, local_ns=None):
    code = compile(cell, line, "exec")
    exec(code, local_ns)
    print(f"save to {line}")
    os.makedirs(os.path.dirname(line), exist_ok=True)
    with open(line, "w") as f:
        f.write(cell)


@needs_local_scope
@register_line_magic
def load_and_run(line, local_ns=None):
    for path in line.split():
        print(f"load {path}")
        with open(path, "r") as f:
            code = f.read()
        exec(code, local_ns)


colab_script = """
import os
import sys

from IPython.core.magic import register_cell_magic, register_line_magic


@register_cell_magic
def run_and_save(line, cell):
    code = compile(cell, line, "exec")
    exec(code, globals())
    print("save to {}".format(line))
    os.makedirs(os.path.dirname(line), exist_ok=True)
    with open(line, "w") as f:
        f.write(cell)

@register_line_magic
def load_and_run(line):
    for path in line.split():
        print("load {}".format(path))
        with open(path, "r") as f:
            code = f.read()
        exec(code, globals())
"""
