#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import asyncio
import functools
import time

import ipywidgets as widgets
import numpy as np
from IPython.display import clear_output, display

from utils.reservoir import ESN, Linear
from utils.style_config import Figure, plt


class InteractiveViewer(object):
    def __init__(
        self,
        net: ESN,
        w_out: Linear,
        w_pulse: np.ndarray,
        pulse_amp: float,
        pulse_period: int,
        plot_num: int = 5,
        input_num: int = 1,
        max_time_steps: int = 10000,
        cmap: str = "Reds",
    ):
        self.net, self.w_out = net, w_out
        self.w_pulse, self.pulse_amp, self.pulse_period = w_pulse, pulse_amp, pulse_period
        self.plot_num, self.input_num = plot_num, input_num
        self.max_time_steps = max_time_steps
        self.t_now, self.t_till = 0, 0
        self.cmap = plt.get_cmap(cmap)

        self.xs = np.zeros((max_time_steps, plot_num))
        self.ys = np.zeros((max_time_steps, 2))
        assert w_pulse.shape[0] >= self.input_num
        assert w_pulse.shape[1] == net.dim
        assert w_out.output_dim == 2

        self.lines = []
        self.fig = Figure(figsize=(6, 8))
        self.fig.create_grid(2, 1, height_ratios=(1, 4))
        for idx in range(plot_num):
            self.lines.append((idx, self.fig[0], self.fig[0].plot([], [])[0]))
        self.fig[0].xaxis.set_major_locator(plt.MaxNLocator(3))
        self.fig[0].set_xlim([self.t_now - max_time_steps, self.t_now - 1])
        self.fig[0].set_ylim([-1.1, 1.1])
        self.fig[0].set_yticklabels([])

        self.rects = []
        self.tasks = dict()
        self.fps, self.time_render_pre = 0.0, 0.0

        self.points = self.fig[1].scatter([], [], s=2.0)
        self.fig[1].set_xlim([-2.1, 2.1])
        self.fig[1].set_ylim([-2.1, 2.1])
        self.fig[1].xaxis.set_major_locator(plt.MaxNLocator(3))
        self.fig[1].yaxis.set_major_locator(plt.MaxNLocator(3))

        xlim = widgets.FloatRangeSlider(
            value=[-2.1, 2.1],
            min=-10.1,
            max=10.0,
            step=0.1,
            description="xlim",
            disabled=False,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format=".1f",
        )
        xlim.observe(self.on_view_range_value_changed, "value")
        self.xlim = xlim

        ylim = widgets.FloatRangeSlider(
            value=[-2.1, 2.1],
            min=-10.1,
            max=10.0,
            step=0.1,
            description="ylim",
            disabled=False,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format=".1f",
        )
        ylim.observe(self.on_view_range_value_changed, "value")
        self.ylim = ylim

        play = widgets.Play(
            value=1,
            min=0,
            max=1000,
            step=1,
            interval=0,
            repeat=True,
            show_repeat=False,
            playing=False,
        )
        play.observe(self.on_play_playing_changed, "playing")
        play.observe(self.on_play_value_changed, "value")
        self.play = play

        speed = widgets.IntSlider(
            value=100,
            min=1,
            max=500,
            step=1,
            readout=True,
            readout_format="d",
            description="speed",
        )
        self.speed = speed

        view_range = widgets.IntSlider(
            value=1500,
            min=10,
            max=max_time_steps,
            step=10,
            readout=True,
            readout_format="d",
            description="view",
        )
        view_range.observe(self.on_view_range_value_changed, "value")
        self.view_range = view_range

        self.input_buttons = []
        self.input_ranges = {}
        for idx in range(input_num):
            input_button = widgets.Button(description=f"input #{idx}", disabled=False, button_style="")
            input_button.on_click(functools.partial(self.on_input_button_click, index=idx))
            self.input_buttons.append(input_button)

        output = widgets.interactive_output(self.render, {"pos": self.play})
        self.output = output

        sliders = widgets.VBox([speed, view_range, xlim, ylim])
        buttons = widgets.VBox(self.input_buttons)
        ui = widgets.VBox([widgets.HBox([play, sliders, buttons]), output])
        self.ui = ui

    def view(self):
        clear_output()
        display(self.ui)

    def __del__(self):
        clear_output()
        self.fig.close()

    def update(self):
        self.xs[:-1] = self.xs[1:]
        self.xs[-1] = self.net.x[: self.plot_num]
        self.ys[:-1] = self.ys[1:]
        self.ys[-1] = self.w_out(self.net.x)
        ranges = list(filter(lambda t: t[0] <= self.t_now < t[1], self.input_ranges.keys()))
        if len(ranges) == 0:
            self.net.step()
        else:
            ins = 0
            for _t0, _t1, index in ranges:
                ins += self.pulse_amp * self.w_pulse[index]
            self.net.step(ins)
        self.t_now += 1

    async def emulate(self, *_args, **_kwargs):
        while True:
            while self.t_now < self.t_till:
                self.update()
            await asyncio.sleep(1e-2)

    def render(self, *_args, **_kwargs):
        for idx, ax, line in self.lines:
            line.set_data(
                range(-self.view_range.value + self.t_now, self.t_now),
                self.xs[-self.view_range.value :, idx],
            )
            ax.set_xlim([-self.view_range.value + self.t_now, self.t_now - 1])
        fps_str = "{:.1f}".format(self.fps)
        self.fig[0].set_title(rf"$t={{{self.t_now}}}$ (fps: {fps_str})")
        self.fig[1].set_xlim(self.xlim.value)
        self.fig[1].set_ylim(self.ylim.value)
        self.points.set_offsets(self.ys[-self.view_range.value :: 2])
        self.points.set_facecolors(self.cmap(np.linspace(0, 1, self.view_range.value)[::2]))
        for t0, t1, t2 in list(self.input_ranges.keys()):
            if t1 < self.t_now - self.max_time_steps:
                rect = self.input_ranges.pop((t0, t1, t2), None)
                rect.remove()
        if self.play.playing:
            self.t_till += self.speed.value

    def on_input_button_click(self, *_args, index=0, **kwargs):
        rect = plt.Rectangle(
            xy=[self.t_now, -1.1],
            width=100,
            height=2.2,
            edgecolor=None,
            facecolor="k",
            alpha=0.5,
            zorder=0,
            **kwargs,
        )
        self.fig[0].add_patch(rect)
        self.input_ranges[(self.t_now, self.t_now + self.pulse_period, index)] = rect

    def on_play_playing_changed(self, *_change):
        if task := self.tasks.pop("emulate", None):
            print("stop emulation")
            task.cancel()
        if self.play.playing:
            print("start emulation")
            self.tasks["emulate"] = asyncio.create_task(self.emulate())

    def on_view_range_value_changed(self, *_change):
        if not self.play.playing:
            self.render()

    def on_play_value_changed(self, *_change):
        time_render_now = time.time()
        self.fps = 1 / (time_render_now - self.time_render_pre)
        self.time_render_pre = time_render_now
