#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

__all__ = ["Figure"]

# import warnings
import math
import os
import sys

# importing matplotlib previously for avoiding Qt Errors
import matplotlib
import numpy as np
from scipy.ndimage import gaussian_filter

run_on_server = (os.getenv("DISPLAY") is None) and (os.name != "nt") and ("google.colab" not in sys.modules)
if run_on_server:
    matplotlib.use("Agg")

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.axes import Axes
from matplotlib.colors import BoundaryNorm, CenteredNorm, LogNorm, TwoSlopeNorm
from matplotlib.ticker import LogFormatterMathtext
from mpl_toolkits.axes_grid1 import make_axes_locatable


# override Axes class
def __getitem__(self, key, hide_parent=True):
    if hasattr(self, "grid_spec"):
        if hide_parent:
            self.axis("off")
        spec_key = self.grid_spec[key]
        if spec_key not in self.specs:
            self.ax_dict[spec_key] = self.figure.add_subplot(spec_key)
            self.specs.append(spec_key)
        return self.ax_dict[spec_key]
    else:
        return None


def create_grid(self, nrows, ncols, **kwargs):
    self.ax_dict = {}
    self.specs = []
    self.grid_spec = gridspec.GridSpecFromSubplotSpec(nrows, ncols, subplot_spec=self.get_subplotspec(), **kwargs)


def share_x(self, ax):
    self.get_shared_x_axes().join(self, ax)


def convert_3d(self):
    return self.figure.add_subplot(self.get_subplotspec(), projection="3d")


def line_x(self, x, **kwargs):
    self.axvline(x, 0, 1, **kwargs)


def line_y(self, y, **kwargs):
    self.axhline(y, 0, 1, **kwargs)


def fill_x(self, x0, x1, edgecolor=None, facecolor="pink", alpha=0.7, zorder=0, **kwargs):
    y0, y1 = self.get_ylim()
    rect = plt.Rectangle(
        xy=[min(x0, x1), y0],
        width=abs(x1 - x0),
        height=y1 - y0,
        edgecolor=edgecolor,
        facecolor=facecolor,
        alpha=alpha,
        zorder=zorder,
        **kwargs,
    )
    self.add_patch(rect)


def fill_y(self, y0, y1, edgecolor=None, facecolor="cyan", alpha=0.7, zorder=0, **kwargs):
    x0, x1 = self.get_xlim()
    rect = plt.Rectangle(
        xy=[x0, min(y0, y1)],
        width=abs(x1 - x0),
        height=y1 - y0,
        edgecolor=edgecolor,
        facecolor=facecolor,
        alpha=alpha,
        zorder=zorder,
        **kwargs,
    )
    self.add_patch(rect)


def fill_std(self, x, y, std, alpha=0.5, **kwargs):
    self.plot(x, y, **kwargs)
    self.fill_between(x, y - std, y + std, alpha=alpha)


def plot_dataframe(self, df, **kwargs):
    print(df)
    x = df.columns.tolist()
    y = df.index.tolist()
    y.reverse()
    z = df.values
    print(z)
    self.plot_matrix(z, x=x, y=y, **kwargs)


def plot_matrix(
    self,
    mat,
    x=None,
    y=None,
    index=None,
    column=None,
    aspect=None,
    zscale=None,
    origin="lower",
    flip_axis=False,
    formatter=None,
    vmin=None,
    vmax=None,
    vcenter=0.0,
    halfrange=None,
    boundaries=None,
    boundary_kws=None,
    xticks_kws=None,
    xlabel=None,
    yticks_kws=None,
    ylabel=None,
    colorbar=True,
    cax=None,
    barloc="right",
    barsize=0.05,
    barpad=0.1,
    contour=False,
    contour_filter=None,
    contour_blur=None,
    contour_kws=None,
    contour_label=True,
    clabel_kws=None,
    **kwargs,
):
    boundary_kws = dict(clip=False, extend="neither") if boundary_kws is None else boundary_kws
    xticks_kws = dict(num_tick=3, fmt="{:g}") if xticks_kws is None else xticks_kws
    yticks_kws = dict(num_tick=3, fmt="{:g}") if yticks_kws is None else yticks_kws
    contour_kws = dict(levels=None, colors="k") if contour_kws is None else contour_kws
    clabel_kws = dict(fmt="{:g}".format, fontsize=10) if clabel_kws is None else clabel_kws

    if x is None:
        x = np.arange(mat.shape[1]) if column is None else column
    if y is None:
        y = np.arange(mat.shape[0]) if index is None else index
    x_size, y_size = len(x), len(y)
    # setting aspect of figure
    if aspect == "square":
        aspect = x_size / y_size
    # setting zscale
    if zscale == "log":
        norm = LogNorm(vmin=vmin, vmax=vmax)
        formatter = LogFormatterMathtext()
        sacle_kws = dict(norm=norm)
    elif zscale == "discrete":
        boundaries = np.linspace(np.min(mat), np.max(mat), 11) if boundaries is None else boundaries
        norm = BoundaryNorm(boundaries, len(boundaries), **boundary_kws)
        sacle_kws = dict(norm=norm)
    elif zscale == "centered":
        norm = CenteredNorm(vcenter=vcenter, halfrange=halfrange)
        sacle_kws = dict(norm=norm)
    elif zscale == "two":
        vmin = np.min(mat) if vmin is None else vmin
        vmax = np.max(mat) if vmax is None else vmax
        norm = TwoSlopeNorm(vcenter=vcenter, vmin=vmin, vmax=vmax)
        sacle_kws = dict(norm=norm)
    else:
        sacle_kws = dict(norm=None, vmin=vmin, vmax=vmax)

    def format_axis(axis, raw_data, num_tick=3, fmt="{:g}", sci=False):
        num_data = len(raw_data)
        interval = (num_data - 1) // (num_tick - 1) if num_tick > 1 else num_data
        interval = 1 if interval < 1 else interval
        if sci:

            def fmt(val):
                return r"$10^{{{:g}}}$".format(math.log10(val))

        if not callable(fmt):
            fmt = fmt.format
        ticks = list(map(fmt, raw_data))
        axis.set_ticks(np.arange(num_data)[::interval], ticks[::interval])

    im = self.imshow(mat, aspect=aspect, origin=origin, **sacle_kws, **kwargs)
    if contour:
        mat2 = contour_filter(mat) if contour_filter is not None else mat
        if contour_blur is not None:
            mat2 = gaussian_filter(mat2, sigma=contour_blur, order=0)
        imc = self.contour(np.arange(x.shape[0]), np.arange(y.shape[0]), mat2, **sacle_kws, **contour_kws)
        if contour_label:
            self.clabel(imc, imc.levels, inline=True, **clabel_kws)

    format_axis(self.xaxis, x, **xticks_kws)
    format_axis(self.yaxis, y, **yticks_kws)
    if xlabel is not None:
        self.set_xlabel(xlabel)
    if ylabel is not None:
        self.set_ylabel(ylabel)

    if flip_axis:
        self.invert_yaxis()
    if colorbar:
        if cax is None:
            divider = make_axes_locatable(self)
            cax = divider.append_axes(barloc, size="{}%".format(100 * barsize), pad=barpad)
        cb = self.figure.colorbar(im, cax=cax, format=formatter)
        if contour and not contour_label:
            cb.add_lines(imc)
        return im, cb
    else:
        return im


def bar_stack(self, data, **kwargs):
    if not hasattr(self, "bar_data"):
        self.bar_data = []
    self.bar_data.append((data, kwargs))


def bar_plot(self, margin=0.2, space=0):
    ndata = len(self.bar_data)
    width = (1.0 - (2 * margin + (ndata - 1) * space)) / ndata
    for idx, y in enumerate(self.bar_data):
        if type(y) is tuple:
            x = [margin + width * (idx + 0.5) + space * idx + idx - 0.5 for idx in range(len(y[0]))]
            self.bar(x, y[0], width=width, align="center", **y[1])
        else:
            x = [margin + width * (idx + 0.5) + space * idx + idy - 0.5 for idy in range(len(y))]
            self.bar(x, y, width=width, align="center")
    self.set_xticks([idx for idx in range(max([len(y[0]) for y in self.bar_data]))])
    self.bar_data = []


def add_zoom_func(self, base_scale=1.5):
    def zoom_reset():
        if not hasattr(zoom_func, "xlim"):
            return
        self.set_xlim(zoom_func.xlim)
        self.set_ylim(zoom_func.ylim)
        self.figure.canvas.draw()

    def zoom_func(event):
        bbox = self.get_window_extent()
        if not (bbox.x0 < event.x < bbox.x1):
            return
        if not (bbox.y0 < event.y < bbox.y1):
            return
        if event.xdata is None or event.ydata is None:
            return
        if not hasattr(zoom_func, "xlim"):
            zoom_func.xlim = self.get_xlim()
            zoom_func.ylim = self.get_ylim()
        if event.button == 2:
            self.zoom_reset()
            return
        cur_xlim = self.get_xlim()
        cur_ylim = self.get_ylim()
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        # print(event.button, event.x, event.y, event.xdata, event.ydata)
        if event.button == "up":
            # deal with zoom in
            scale_factor = base_scale
        elif event.button == "down":
            # deal with zoom out
            scale_factor = 1 / base_scale
        else:
            # deal with something that should never happen
            return
        # set new limits
        self.set_xlim(
            [
                xdata - (xdata - cur_xlim[0]) / scale_factor,
                xdata + (cur_xlim[1] - xdata) / scale_factor,
            ]
        )
        self.set_ylim(
            [
                ydata - (ydata - cur_ylim[0]) / scale_factor,
                ydata + (cur_ylim[1] - ydata) / scale_factor,
            ]
        )
        self.figure.canvas.draw()

    self.zoom_reset = zoom_reset
    self.figure.canvas.mpl_connect("scroll_event", zoom_func)
    self.figure.canvas.mpl_connect("button_press_event", zoom_func)


def scientific_ticker(self, axis, sci_format="%1.10e"):
    f = mticker.ScalarFormatter(useOffset=False, useMathText=True)

    def g(x, pos):
        return "${}$".format(f._formatSciNotation("%1.10e" % x))

    if "x" in axis:
        self.xaxis.set_major_formatter(mticker.FuncFormatter(g))

    if "y" in axis:
        self.yaxis.set_major_formatter(mticker.FuncFormatter(g))


def set_log_grid(self, axis="y"):
    self.grid(True)
    if "y" in axis or axis == "both":
        self.set_yscale("log")
        locmin = mticker.LogLocator(base=10, subs=np.arange(0.1, 1, 0.1), numticks=10)
        self.yaxis.set_minor_locator(locmin)
        self.yaxis.set_minor_formatter(mticker.NullFormatter())
    if "x" in axis or axis == "both":
        self.set_xscale("log")
        locmin = mticker.LogLocator(base=10, subs=np.arange(0.1, 1, 0.1), numticks=10)
        self.xaxis.set_minor_locator(locmin)
        self.xaxis.set_minor_formatter(mticker.NullFormatter())


func_list = [
    __getitem__,
    create_grid,
    share_x,
    convert_3d,
    line_x,
    line_y,
    fill_x,
    fill_y,
    fill_std,
    plot_matrix,
    plot_dataframe,
    bar_stack,
    bar_plot,
    add_zoom_func,
    scientific_ticker,
    set_log_grid,
]

for func in func_list:
    setattr(Axes, func.__name__, func)


class FigureWrapper(plt.Figure):
    def __init__(self, **kwargs):
        super(FigureWrapper, self).__init__(**kwargs)
        self.ax_dict = {}
        self.specs = []

    def __getitem__(self, key) -> Axes:
        spec_key = self.grid_spec[key]
        if spec_key not in self.specs:
            self.ax_dict[spec_key] = self.add_subplot(spec_key)
            self.specs.append(spec_key)
        return self.ax_dict[spec_key]

    @staticmethod
    def show(block=True, interval=0.2, tight_layout=True):
        if run_on_server:
            print("no display detected")
        else:
            if tight_layout:
                plt.tight_layout()
            if block:
                plt.show(block=True)
            else:
                plt.show(block=False)
                plt.pause(interval)

    @staticmethod
    def pause(interval):
        plt.pause(interval)

    def create_grid(self, nrows, ncols, **kwargs):
        self.grid_spec = gridspec.GridSpec(nrows, ncols, **kwargs)

    def set_figsize(self, *args, **kwargs):
        self.set_size_inches(*args, **kwargs)

    def close(self):
        plt.close(self)

    def savefig(self, file_name, tight_layout=True, **kwargs):
        if type(file_name) is str:
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
        if tight_layout:
            self.tight_layout()
        super(FigureWrapper, self).savefig(file_name, **kwargs)


class Figure(FigureWrapper):
    def __new__(_cls, *args, nrows=1, ncols=1, grid_options=None, **kwargs) -> FigureWrapper:
        self: FigureWrapper = plt.figure(*args, **kwargs, FigureClass=FigureWrapper)
        self.create_grid(nrows=nrows, ncols=ncols, **(grid_options or {}))
        return self
