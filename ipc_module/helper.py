#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import functools
import importlib
import inspect
import itertools
import math
import sys
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.axes import Axes


def get_backend_name(mat):
    return mat.__class__.__module__


def import_backend(mat):
    try:
        name = get_backend_name(mat)
        backend = importlib.import_module(name)
    except ImportError:
        raise ModuleNotFoundError(f"{name} is not found") from None
    return backend


def backend_max(mat, *args, **kwargs):
    res = mat.max(*args, **kwargs)
    if get_backend_name(mat) == "torch":
        if type(res) is importlib.import_module("torch").return_types.max:
            # Pytorch wrapper
            # See https://pytorch.org/docs/stable/generated/torch.max.html
            res = res.values
    return res


def backend_std(mat, *args, **kwargs):
    if get_backend_name(mat) == "torch":
        return mat.std(*args, unbiased=False, **kwargs)
    else:
        return mat.std(*args, **kwargs)


def zeros_like(mat, shape=None):
    module = importlib.import_module(mat.__class__.__module__)
    if shape is None:
        return module.zeros_like(module.broadcast_to(mat, mat.shape))
    else:
        return module.zeros_like(module.broadcast_to(mat.flatten()[0], shape))


@functools.cache
def make_degree_list(s, m=None):
    if m is None:
        m = s
    if s == 0:
        return [()]
    ans = []
    for d in range(1, min(s, m) + 1):
        res = make_degree_list(s - d, d)
        ans += [(d, *v) for v in res]
    return ans


def multi_combination(arr, *num):
    if len(num) == 0:
        yield ()
        return
    length = len(arr)
    if length < num[0] or num[0] < 0:
        return
    itl = itertools.combinations(arr, num[0])
    itr = list(itertools.combinations(arr, length - num[0]))[::-1]
    for left, right in zip(itl, itr, strict=False):
        for out in multi_combination(right, *num[1:]):
            yield left, *out


@functools.cache
def multi_combination_length(length, *num):
    if len(num) == 0:
        return 1
    elif length < num[0]:
        return 0
    else:
        return math.comb(length, num[0]) * multi_combination_length(length - num[0], *num[1:])


def make_delay_list(delay_range, degree_tuple):
    @functools.cache
    def _make_delay_list_wrapper(a1, a2):
        return list(map(lambda v: sum(v, ()), multi_combination(a1, *a2)))

    return _make_delay_list_wrapper(delay_range, Counter(degree_tuple).values())


@functools.cache
def make_permutation(length, seed=None, rnd=None, tolist=True):
    perm = np.arange(length, dtype=np.int32)
    if rnd is None:
        rnd = np.random.default_rng(seed)
    rnd.shuffle(perm)
    if tolist:
        return perm.tolist()
    else:
        return perm


def count_ipc_candidates(
    degree_sum: int | list = 1,
    delay_max: int | list = 100,
    maximum_component: int = None,
    zero_offset: bool = True,
    surrogate_num: int = 1000,
):
    # Sum of degrees to be calculated.
    if type(degree_sum) is list:
        degree_sum = np.sort(np.unique(degree_sum)).tolist()
    else:
        degree_sum = [degree_sum]
    # Range of delays to be calculated.
    if type(delay_max) is int:
        delay_max = [delay_max]
    degree_tuples, delay_ranges = [], []
    for degree, delay in zip(degree_sum, delay_max, strict=False):
        degree_tuple = make_degree_list(degree)
        if maximum_component is not None:
            degree_tuple = list(filter(lambda t: len(t) <= maximum_component, degree_tuple))
        degree_tuples += degree_tuple
        delay_ranges += [range(0 if zero_offset else 1, delay + 1)] * len(degree_tuple)
    # Calculate the number of iterations (# of regressor calls).
    total_length = [
        multi_combination_length(len(delay_range), *Counter(degree_tuple).values())
        for degree_tuple, delay_range in zip(degree_tuples, delay_ranges, strict=False)
    ]
    total_length = [v for v in total_length if v > 0]
    total_length = sum(total_length) + surrogate_num * len(total_length)
    return total_length


def truncate_tuple(tup: tuple[int], max_length=5):
    if len(tup) <= max_length:
        return str(tup)
    else:
        return f"({', '.join(map(str, tup[:max_length]))}, ...)"


def truncate_dataframe(df: pl.DataFrame, key="ipc", rank=None):
    columns = [column for column in df.columns if "ipc" not in column]
    df_tr = df.filter(pl.col(key) > 0)
    if rank is not None and df_tr[key].sum() > rank:
        df_tr = df_tr.sort(key, descending=True)
        df_tr = df_tr.with_columns(pl.col(key).cum_sum().alias("cum"))
        df_tr = df_tr.filter(df_tr["cum"] < rank)
    return df_tr[[*columns, key]]


def visualize_dataframe(
    ax: Axes,
    df: pl.DataFrame,
    xticks: list | np.ndarray | None = None,
    group_by: str = "degree",
    threshold: float = 0.5,
    sort_by: callable = np.nanmax,
    cmap: str | plt.Colormap = "tab10",
    x_offset: float = 0,
    min_color_coef: float = 0.5,
    fontsize: int = 12,
    step_linewidth: float = 0.5,
    bottom_min: np.ndarray | None = None,
    zero_offset: bool = True,
):
    """

    Visualizes IPC results stored in a DataFrame using a bar plot.

    Parameters:
        ax (Axes): Matplotlib Axes object to plot on.
        df (pl.DataFrame): `polars.DataFrame` containing IPC results.
        xticks (list | np.ndarray | None, optional): X-axis tick positions. If `None`, default positions are used.
        group_by (str, optional): Grouping method for IPC components. Choose from 'degree', 'component', or 'detail'.
        threshold (float, optional): Threshold for displaying IPC components. Components with values below this threshold are grouped into 'rest'.
        sort_by (callable, optional): Function to sort IPC components.
        cmap (str | plt.Colormap, optional): Colormap for coloring IPC components.
        x_offset (float, optional): Horizontal offset for the x-axis.
        min_color_coef (float, optional): Minimum color coefficient for coloring. Only used when `group_by` is 'component' or 'detail'.
        fontsize (int, optional): Font size for labels.
        step_linewidth (float, optional): Line width for step lines. If 0, no lines are drawn.
        bottom_min (np.ndarray | None, optional): Minimum bottom values for bars.
        zero_offset (bool, optional): Whether the delay offset starts from zero.

    Notes:
        `group_by` determines how IPC components are grouped and colored:

        - `'degree'`: Groups by sum of degrees (e.g., `3` for `(3,)`, `(2, 1)`, `(1, 1, 1)`).
        - `'component'`: Groups by tuple of degrees (e.g., `(3,)`, `(2, 1)`, `(1, 1, 1)` are distinct).
        - `'detail'`: Groups by tuple of degrees and delays.

        Since the number of unique components can grow rapidly, using `'component'` or `'detail'` may result in many distinct colors, making it time-consuming to render.
        Especially for `'detail'`, consider setting a higher threshold to limit the number of displayed components (e.g., `threshold=1.0`).
        Use a positive `threshold` value to group less significant components into a `rest` category.
    """

    ipc_columns = [column for column in df.columns if "ipc" in column]
    assert group_by in ["degree", "component", "detail"], "invalid `group_by` argments"
    col_cmp = sorted([column for column in df.columns if column.startswith("cmp")])
    col_del = sorted([column for column in df.columns if column.startswith("del")])
    group_by_columns = dict(degree=["degree"], component=col_cmp, detail=col_cmp + col_del)
    if type(cmap) is str:
        cmap = plt.get_cmap(cmap)

    def shape_segment(segment, get_delay=False):
        if group_by == "degree":
            return tuple(segment)
        elif group_by == "component":
            return tuple(val for val in segment if val >= 0)
        elif group_by == "detail":
            degrees = tuple(val for val in segment[: len(segment) // 2] if val >= 0)
            if get_delay:
                delays = tuple(val for val in segment[len(segment) // 2 :] if val >= 0)
                return degrees, delays
            else:
                return degrees

    def get_color_index(segment):
        if group_by == "degree":
            return segment[0], 0, 1
        elif group_by == "component":
            degrees = shape_segment(segment)
            degree = sum(degrees)
            degree_list = make_degree_list(degree)
            index = dict(zip(degree_list[::-1], range(len(degree_list)), strict=False))[degrees]
            max_index = len(degree_list)
            return degree, index, max_index
        elif group_by == "detail":
            degrees, delays = shape_segment(segment, get_delay=True)
            degree = sum(degrees)
            degree_list = make_degree_list(degree)
            index = dict(zip(degree_list[::-1], range(len(degree_list)), strict=False))[degrees]
            max_index = len(degree_list)
            return degree, index + max(0, 1 - 0.9 ** (max(delays) - (not zero_offset))), max_index

    def color_func(segment):
        white = np.ones(4)
        degree, index, max_index = get_color_index(segment)
        coef = (index / max_index) * min_color_coef
        out = np.array(cmap(degree - 1))
        out = (1 - coef) * out + coef * white
        return out

    def label_func(segment):
        if group_by == "degree":
            return str(segment[0])
        elif group_by == "component":
            out_str = str(shape_segment(segment))
            return out_str.replace("(", "{").replace(",)", "}").replace(")", "}")
        elif group_by == "detail":
            degrees, delays = shape_segment(segment, get_delay=True)
            out_str = str(tuple(zip(degrees, delays, strict=False)))
            return out_str.replace("(", "{").replace(",)", "}").replace(")", "}")

    def hatch_func(segment):
        hatches = ["//", "\\\\", "||", "--", "++", "xx", "oo", "OO", "..", "**"]
        if group_by == "degree":
            return None
        elif group_by == "component":
            return None
        elif group_by == "detail":
            _degrees, delays = shape_segment(segment, get_delay=True)
            return hatches[(max(delays) - (not zero_offset)) % len(hatches)]

    def sort_func(arg):
        segment, val = arg
        if sort_by(val) > threshold:
            if group_by == "degree":
                return segment
            elif group_by == "component":
                degrees = shape_segment(segment)
                return (sum(degrees), *(-d for d in degrees))
            elif group_by == "detail":
                degrees = shape_segment(segment)
                return (
                    sum(degrees),
                    *(-s for s in segment[: (len(segment) // 2)]),
                    *segment[(len(segment) // 2) :],
                )
        else:
            return (np.inf,)

    # Aggregation process.
    out = defaultdict(list)
    segments = df[group_by_columns[group_by]].unique()
    for column in ipc_columns:
        df_agg = df.group_by(group_by_columns[group_by]).agg(pl.col(column).sum())
        for segment in segments.iter_rows():
            out[segment].append(0)
        for *segment, val in df_agg.iter_rows():
            out[tuple(segment)][-1] = val

    # Visualization process.
    bottom, rest, legend_cnt = 0.0, 0.0, 1
    if xticks is None:
        pos = x_offset + np.arange(-1, len(ipc_columns) + 1)
        width = 1.0
    else:
        pos = np.zeros(len(ipc_columns) + 2)
        pos[1:-1] = xticks
        width = pos[1] - pos[0]
        pos[0] = pos[1] - width
        pos[-1] = pos[-2] + width

    legend_cnt = 1
    bottom = np.zeros_like(pos, dtype=float)
    rest = np.zeros_like(pos, dtype=float)
    for segment, val in sorted(out.items(), key=sort_func):
        ipc = np.zeros_like(bottom)
        ipc[1:-1] = val
        if sort_by(ipc) > threshold:
            ax.bar(
                pos[1:-1],
                ipc[1:-1],
                bottom=bottom[1:-1] if bottom_min is None else np.maximum(bottom[1:-1], bottom_min),
                width=width,
                linewidth=0.0,
                label=label_func(segment),
                color=color_func(segment),
                hatch=hatch_func(segment),
            )
            if step_linewidth > 0:
                ax.step(
                    pos,
                    ipc + bottom if bottom_min is None else np.maximum(ipc + bottom, bottom_min),
                    "#333333",
                    where="mid",
                    linewidth=step_linewidth,
                )
            legend_cnt += 1
            bottom += ipc
        else:
            rest += ipc
    if threshold > 0:
        ax.bar(
            pos[1:-1],
            rest[1:-1],
            bottom=bottom[1:-1],
            width=width,
            label="rest",
            color="darkgray",
            hatch="/",
            linewidth=0.0,
        )
        if step_linewidth > 0:
            ax.step(pos, rest + bottom, "#333333", where="mid", linewidth=step_linewidth)
    ax.tick_params(axis="both", which="major", labelsize=fontsize)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.05, 1.0),
        borderaxespad=0,
        ncol=math.ceil(legend_cnt / 18),
        fontsize=fontsize,
    )
    return out


__all__ = [name for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isroutine)]
