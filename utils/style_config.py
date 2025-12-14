#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from .figure import Figure

# matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["grid.linewidth"] = 0.75
matplotlib.rcParams["lines.markersize"] = 8.0
matplotlib.rcParams["lines.markeredgewidth"] = 0.0
sns.set_theme(font_scale=1.5, font="Arial")
sns.set_palette("tab10")
sns.set_style("whitegrid", {"grid.linestyle": "--"})

cmap = plt.get_cmap("tab10")
Figure
