#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import numpy as np
import pandas as pd
import plotly.express as px
import scipy as sp

from .style_config import Figure, cmap


def show_record(record, plot_keys, xlim=None, view_slice=(Ellipsis,)):
    def plot_x(ax):
        t = record["t"]
        x = record["x"]
        ax.plot(t, x[(*view_slice, slice(0, 10))], lw=0.75)
        ax.set_ylim([-1.1, 1.1])
        ax.line_y(1.0, lw=0.75, ls=":", color="k")
        ax.line_y(-1.0, lw=0.75, ls=":", color="k")
        ax.set_ylabel("ESN dynamics")
        return [ax]

    def plot_y(ax):
        t = record["t"]
        y = record["y"]
        d = record["d"] if "d" in record else None
        if y.shape[-1] == 1:
            ax.plot(t[:-1], y[(*view_slice, 0)], lw=0.75, color=cmap(0))
            if d is not None:
                ax.plot(t[:-1], d[(*view_slice, 0)], ls=":", lw=0.75, color="k")
            ax.set_ylabel("y & d" if "d" in record else "y")
            return [ax]
        else:
            axes = []
            num_out = y.shape[-1]
            ax.create_grid(num_out, 1, hspace=0.1)
            for idx in range(num_out):
                ax[idx].plot(t[:-1], y[(*view_slice, idx)], lw=0.75, color=cmap(idx))
                if d is not None:
                    ax[idx].plot(t[:-1], d[(*view_slice, idx)], ls=":", lw=0.75, color="k")
                axes.append(ax[idx])
            ax[int(num_out // 2)].set_ylabel("y & d" if "d" in record else "y")
            return axes

    def plot_dw(ax):
        t = record["t"]
        w = record["w"]
        dw = np.linalg.norm(w[1:] - w[:-1], axis=tuple(range(1, w.ndim)))
        ax.plot(t[:-1], dw, lw=0.75, color="purple")
        ax.set_ylabel("Δw")
        return [ax]

    plot_func = dict(x=(plot_x, 1), y=(plot_y, 0.5), dw=(plot_dw, 0.5))

    height_ratios = []
    for key in plot_keys:
        size = plot_func[key][1]
        if key == "y":
            size *= record["y"].shape[-1]
        height_ratios.append(size)

    fig = Figure(figsize=(12, sum(height_ratios) * 4))
    fig.create_grid(len(height_ratios), 1, hspace=0.05, height_ratios=height_ratios)

    axes = []
    for idx, key in enumerate(plot_keys):
        func = plot_func[key][0]
        axes += func(fig[idx])

    for idx, ax in enumerate(axes):
        if xlim is not None:
            ax.set_xlim(xlim)
        if "open_range" in record:
            ax.fill_x(*record["open_range"], alpha=0.4, facecolor="cyan")
        if "train_range" in record:
            ax.fill_x(*record["train_range"], alpha=0.4, facecolor="pink")
        if "pulse_range" in record:
            ax.fill_x(*record["pulse_range"], alpha=0.4, facecolor="gray")
        if "innate_range" in record:
            ax.fill_x(*record["train_range"], alpha=0.4, facecolor="pink")
        ax.get_yaxis().set_tick_params(labelsize=12)
        ax.get_yaxis().set_label_coords(-0.1, 0.5)
        ax.get_yaxis().set_tick_params(labelsize=14)
        if idx < len(axes) - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("Time steps")
    return fig


def show_trajectory(y):
    if y.ndim == 1:
        fig = Figure(figsize=(16, 4))
        fig[0].plot(y, lw=0.75)
        fig[0].set_xlabel("Time steps")
    else:
        n_y = y.shape[1]
        fig = Figure(figsize=(16, 2 * n_y))
        fig.create_grid(n_y, 1, hspace=0.0)
        for idx in range(n_y):
            fig[idx].plot(y[:, idx], lw=0.75, color=cmap(idx))
            if idx < n_y - 1:
                fig[idx].set_xticklabels([])
        fig[n_y - 1].set_xlabel("Time step")
    return fig


def construct_delayed_coord(data, tau, ndim=2):
    assert data.ndim == 1 or data.shape[-1] == 1
    if data.ndim == 1:
        data = data[:, None]
    length = data.shape[0]
    return np.concatenate([data[tau * d : length - tau * (ndim - d)] for d in range(ndim)], axis=-1)


def show_delayed_coord(*args, tau=10, labels=None, **kwargs):
    if len(args) == 1:
        y = args[0]
        fig = Figure(figsize=(6, 6))
        fig[0].plot(y[:-tau], y[tau:], lw=0.2, **kwargs)
    else:
        n_fig = len(args) + 1
        fig = Figure(figsize=(8 * n_fig, 6))
        fig.create_grid(1, n_fig, hspace=0.15)
        for idx, y in enumerate(args):
            fig[idx].plot(y[:-tau], y[tau:], lw=0.25, color=cmap(idx), **kwargs)
            fig[idx].set_xlabel(r"$x_{}(t)$".format(idx + 1))
            fig[idx].set_ylabel(r"$x_{}(t+\tau)$".format(idx + 1))
            fig[-1].plot(y[:-tau], y[tau:], lw=0.25, color=cmap(idx), **kwargs)
            fig[idx].set_aspect("equal", "datalim")
            if labels is not None and idx < len(labels):
                fig[idx].set_title(labels[idx])
        fig[-1].set_aspect("equal", "datalim")
    return fig


def get_maxima_and_minima(xs, **kwargs):
    id_maxima = sp.signal.find_peaks(xs, **kwargs)[0]
    id_minima = sp.signal.find_peaks(-xs, **kwargs)[0]
    return id_maxima, id_minima


def show_return_map(**kwargs):
    fig = Figure(figsize=(8, 6))
    for label, data in kwargs.items():
        id_maxima, _ = get_maxima_and_minima(data)
        maxima = data[id_maxima]
        fig[0].plot(maxima[:-1], maxima[1:], marker=".", markersize=5.0, ls="", label=label)
    fig[0].legend()
    fig[0].set_xlabel(r"$M_n$")
    fig[0].set_ylabel(r"$M_{n+1}$")


def show_3d_coord(*args, axes=None, **data_dict):
    axes = axes if axes is not None else ["x", "y", "z"]
    if len(args) > 0:
        data_dict = dict(enumerate(args))
    df_list = []
    for key, val in data_dict.items():
        assert val.ndim == 2 and val.shape[-1] == 3
        cols = dict(zip(axes, [val[:, idx] for idx in range(3)], strict=False))
        df = pd.DataFrame(cols)
        df = df.assign(label=str(key))
        df_list.append(df)
    df = pd.concat(df_list)
    fig = px.line_3d(
        data_frame=df,
        x=axes[0],
        y=axes[1],
        z=axes[2],
        color="label" if len(data_dict) > 1 else None,
    )
    fig.update_layout(
        autosize=False,
        width=800,
        height=800,
        scene=dict(
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.25, y=-1.25, z=1.25),
            )
        ),
    )
    return fig


def show_innate_record(
    record,
    plot_range,
    t_range=None,
    fig=None,
    title=None,
    clear=False,
    cmap=None,
    pulse_range=None,
    innate_range=None,
    **kwargs,
):
    t_range = t_range if t_range is not None else slice(None)
    ts, xs = record["t"], record["x"]
    plot_num = len(plot_range)
    create_new_fig = fig is None
    if create_new_fig:
        fig = Figure(figsize=(12, plot_num * 1.6))
        fig.create_grid(plot_num, 1, wspace=0.0, hspace=0.0)

    if clear or create_new_fig:
        for idx in range(plot_num):
            fig[idx].cla()
            fig[idx].set_xlim([ts[0], ts[-1]])
            fig[idx].set_ylim([-1.1, 1.1])
            if pulse_range is not None:
                fig[idx].fill_x(*pulse_range, facecolor="gray", alpha=0.5)
            if innate_range is not None:
                fig[idx].fill_x(*innate_range, facecolor="pink", alpha=0.5)

    if title is not None:
        fig[0].set_title(title)
    for idx in range(plot_num):
        fig[idx].set_yticklabels([])
        if idx < plot_num - 1:
            fig[idx].set_xticklabels([])
        fig[idx].grid(True)

    for symbol_id, x in enumerate(np.rollaxis(xs, -2)):
        if cmap is not None:
            kwargs["color"] = cmap(symbol_id)
        for idx, node_id in enumerate(plot_range):
            fig[idx].plot(ts[t_range], x[t_range, ..., node_id], **kwargs)
    return fig


def show_innate_error(error_history, fig=None, logscale=True, **kwargs):
    if fig is None:
        fig = Figure(figsize=(8, 5))
    else:
        fig[0].cla()
    error_mean = np.mean(error_history, axis=1)
    error_std = np.std(error_history, axis=1)
    error_best_epoch = error_mean.sum(axis=1).argmin()
    for mean, std in zip(error_mean.T, error_std.T, strict=False):
        fig[0].fill_std(np.arange(mean.shape[0]), mean, std)
    if logscale:
        fig[0].set_yscale("log")
    else:
        fig[0].set_ylim([0, None])
    fig[0].line_x(error_best_epoch, ls=":", color="black")
    fig[0].set_title("best: #{}".format(error_best_epoch))
    return fig
