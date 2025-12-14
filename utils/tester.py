#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import functools
import glob
import importlib.util
import inspect
import itertools
import math
import sys
import time

import numpy as np
from IPython.lib.pretty import pretty


def to_args(*args, rel_tol=1e-9, abs_tol=0.0, **kwargs):
    return args, kwargs, dict(rel_tol=rel_tol, abs_tol=abs_tol)


def calc_time(func, *args, **kwargs):
    t_begin = time.time()
    ret = func(*args, **kwargs)
    t_elapsed = time.time() - t_begin
    return ret, t_elapsed


def get_variables_info(*args, **kwargs):
    out = {}
    iterations = itertools.chain([(f"#{idx + 1}", arg) for idx, arg in enumerate(args)], kwargs.items())
    for key, val in iterations:
        if type(val) is np.ndarray:
            with np.printoptions(edgeitems=10, threshold=5, linewidth=np.inf, precision=2):
                val_str = pretty(val).replace("\n", "").replace(" ", "")[6:-1]
            if len(val_str) > 25:
                val_str = val_str[:25] + "..."
            out[key] = dict(shape=val.shape, dtype=val.dtype, value=val_str)
        else:
            out[key] = repr(val)
    return out


def recursive_print_dict(d, indent=0, size=2):
    space = " " * indent * size
    for k, v in d.items():
        if isinstance(v, dict):
            print(f"{space}{k}:")
            recursive_print_dict(v, indent + 1, size=size)
        else:
            print(f"{space}{k}: {v}")


def check_match(ret_sol, ret_out, rel_tol=1e-9, abs_tol=0.0) -> tuple[bool, str]:
    try:
        assert len(ret_sol) == len(ret_out), "The number of returns are different!"
        for out_id, (sol, out) in enumerate(zip(ret_sol, ret_out, strict=False)):
            t_sol, t_out = type(sol), type(out)
            assert t_sol is t_out, f"#{out_id + 1}'s types are different!"
            if t_sol is np.ndarray:
                assert sol.shape == out.shape, f"#{out_id + 1}'s shapes are different!"
                assert sol.dtype == out.dtype, f"#{out_id + 1}'s dtypes are different!"
                assert np.allclose(sol, out), f"#{out_id + 1}'s values are not close!"
            elif t_sol is float:
                assert math.isclose(sol, out, abs_tol=abs_tol, rel_tol=rel_tol), (
                    f"#{out_id + 1}'s values are not close!"
                )
            else:
                assert sol == out, f"#{out_id + 1}'s values are not equal!"
        return True, ""
    except AssertionError as errmsg:
        return False, errmsg


def load_module(file_name: str, data_dir: str = "./data"):
    files = glob.glob(f"{data_dir}/{file_name}.py")
    if len(files) == 0:
        raise FileNotFoundError("Solution file was not found !")
    ans_file_name = files[0]
    spec = importlib.util.spec_from_file_location("module.name", ans_file_name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_func(func, file_name, debug_mode=0, multiple_output=False, **kwargs):
    mod = load_module(file_name, **kwargs)
    solution, dataset = mod.solution, mod.dataset
    for idx, (args, kwargs, toleance) in enumerate(dataset()):
        ret_sol, t_sol = calc_time(solution, *args, **kwargs)
        ret_out, t_out = calc_time(func, *args, **kwargs)
        if not multiple_output:
            ret_sol = (ret_sol,)
            ret_out = (ret_out,)
        match, errmsg = check_match(ret_sol, ret_out, **toleance)
        if debug_mode >= 1 or abs(debug_mode) == 1:
            t_sol_s = "t_sol {:.2e}[s]".format(t_sol)
            t_out_s = "t_out {:.2e}[s]".format(t_out)
            print("{:<6}{:>4}{:>35}{:>35}".format("time", idx + 1, t_sol_s, t_out_s))
        if debug_mode >= 2 or abs(debug_mode) == 2:
            args_s = pretty(args).replace("\n", "").replace(" ", "")
            if len(args_s) > 65:
                args_s = args_s[:65] + "..."
            print("{:<6}{:>4}{:>70}".format("input", idx + 1, args_s))
        if debug_mode >= 3 or abs(debug_mode) == 3:
            ret_sol_s = pretty(ret_sol[0]).replace("\n", "").replace(" ", "")
            if len(ret_sol_s) > 25:
                ret_sol_s = ret_sol_s[:25] + "..."
            ret_out_s = pretty(ret_out[0]).replace("\n", "").replace(" ", "")
            if len(ret_out_s) > 25:
                ret_out_s = ret_out_s[:25] + "..."
            print("{:<6}{:>4}{:>35}{:>35}".format("output", idx + 1, ret_sol_s, ret_out_s))
        if not match:
            info_dict = {}
            info_dict["Argument(s)"] = get_variables_info(*args, **kwargs)
            info_dict["Return(s) (desired)"] = get_variables_info(*ret_sol)
            info_dict["Return(s) (yours)"] = get_variables_info(*ret_out)
            print(f"Failed! (case #{idx + 1}): {errmsg}")
            # print(info_dict)
            recursive_print_dict(info_dict)
            return
    print(f"OK! (pass all {idx + 1} cases)")


def show_solution(file_name, name="solution", **kwargs):
    mod = load_module(file_name, **kwargs)
    print(inspect.getsource(getattr(mod, name)))


def load_from_chapter_name(chapter_name: str, data_dir: str = "./data"):
    test_func_part = functools.partial(test_func, data_dir=f"{data_dir}/{chapter_name}")
    show_solution_part = functools.partial(show_solution, data_dir=f"{data_dir}/{chapter_name}")
    return test_func_part, show_solution_part
