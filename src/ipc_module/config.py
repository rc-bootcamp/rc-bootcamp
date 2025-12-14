#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.


SHOW_PROGRESS_BAR = True


def set_progress_bar(show: bool):
    """
    Set the global flag to show or hide the progress bar.

    Parameters:
        show (bool): If True, show the progress bar; otherwise, hide it.
    """
    global SHOW_PROGRESS_BAR
    SHOW_PROGRESS_BAR = show
