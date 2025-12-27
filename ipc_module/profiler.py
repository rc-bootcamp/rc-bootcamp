#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

__all__ = ["UnivariateViewer", "UnivariateProfiler"]

import functools
import os
from collections import Counter

import joblib
import numpy as np
import polars as pl
import polars.selectors as cs

from . import config, polynomial
from .helper import (
    get_backend_name,
    import_backend,
    make_degree_list,
    make_delay_list,
    make_permutation,
    multi_combination_length,
    truncate_tuple,
    zeros_like,
)
from .regressor import BatchRegressor
from .tqdm import tqdm


class UnivariateViewer(object):
    """
    Viewer class to load and visualize profiling results.
    This class does not have the original time series (i.e., `us` and `xs`), so it cannot calculate IPC.
    """

    def __init__(self, path: str, method: int | tuple | None = None):
        """
        Parameters:
            path (str): File path to load results.
            method (int | tuple | None, optional): Filter method (see `filter_by` method).

        Notes:
            You can partially load results by specifying the `method` argument.

        Examples:
            ```python
            viewer = UnivariateViewer("path/to/results.npz")  # Load all results
            viewer = UnivariateViewer("path/to/results.npz", method=3)  # Load only degree sums of 3
            viewer = UnivariateViewer("path/to/results.npz", method=(2, 1))  # Load only degree tuple of (2, 1)
            ```
        """
        self.backend = np
        if path is None:
            self.results = {}
            self.rank = []
            self.info = {}
        else:
            self.load(path, method=method)

    def __getitem__(self, degree_tuple: tuple):
        """
        Retrieves profiling results for a given degree tuple.

        Parameters:
            degree_tuple (tuple): Degree tuple to fetch results for (e.g., (1, 2), (3,), etc.).

        Returns:
            delay (list): Evaluated delays (e.g., [(0,), (1,), ...]), with length matching the number of delays.
            ipc_base (np.ndarray): IPCs for original data, shaped as [# of delays, *batch_shape, 1].
            ipc_surr (np.ndarray): IPCs for surrogate data, shaped as [# of surrogates, *batch_shape, 1].

        Examples:
            ```python
            delay, ipc_base, ipc_surr = viewer[(2, 1)]  # Fetch results for degree tuple (2, 1)
            ```
        """
        assert type(degree_tuple) is tuple
        if degree_tuple not in self.results:
            return None
        delay, base, surr = self.results[degree_tuple]
        return delay, self.to_numpy(base), self.to_numpy(surr)

    def __len__(self):
        return len(self.results)

    @property
    def backend_name(self):
        return self.backend.__name__

    @staticmethod
    def filter_by(method: int | tuple | None = None):
        """
        Creates a filter function based on the specified method.

        Parameters:
            method (int | tuple | None, optional): Method to filter by. Either an integer, a tuple of degrees, or None.

        Returns:
            filter_func (callable | None): A function that takes a degree tuple as input and returns True if it matches the filter criteria, or None if no filtering is applied.

        Notes:
            You might not directly use this method; a function with `method` argument in other methods calls this internally.
            The filter function works as follows based on the `method` type:

            |Type of `method`|Description|
            |-|-|
            | `int` (positive) | Extract degree tuples where the sum of degrees equals the specified value (e.g., `3` extracts with degree sums of 3, such as `(1, 2)` and `(3,)`). |
            | `int` (negative) | Extract degree tuples where the length of degree tuple equals the specified value (e.g., `-3` extracts with degree lengths of 3, such as `(1, 1, 1)` and `(2, 2, 3)`). |
            | `tuple` | Extract only degree tuples that match the specified tuple of degrees. |
            | `None` | No filtering, i.e., extract all degree tuples (default). |
        """
        if type(method) is int:
            if method > 0:
                return lambda key: sum(key) == method
            elif method < 0:
                return lambda key: len(key) == -method
            else:
                raise ValueError("filter method should be non-zero value.")
        elif type(method) is tuple:
            return lambda key: key == method
        else:
            return method

    @staticmethod
    def to_numpy(val):
        name = val.__class__.__module__
        if name == "torch":
            return val.detach().cpu().numpy()
        elif name == "cupy":
            return import_backend(val).asnumpy(val)
        else:
            return val

    def to_backend(self, val: np.ndarray):
        name = self.backend_name
        if name == "torch":
            return self.backend.from_numpy(val).to(self.us.device)
        elif name == "cupy":
            return self.backend.asarray(val)
        else:
            return val

    def keys(self, method: int | tuple | None = None):
        if method is None:
            return self.results.keys()
        else:
            return filter(self.filter_by(method), self.results.keys())

    def items(self, method: int | tuple | None = None):
        return map(lambda key: (key, self[key]), self.keys(method))

    def values(self, method: int | tuple | None = None):
        return map(lambda key: self[key], self.keys(method))

    def calc_surr_max(self, key=None, surr=None, max_scale=1.0):
        if surr is None:
            surr = self.to_numpy(self.results[key][2])
        surr = self.to_numpy(surr)
        surr_max = np.max(surr, axis=0)
        return surr_max * max_scale

    def to_dataframe(
        self,
        method: int | tuple | None = None,
        extracted_batch: tuple = (...,),
        squeeze: bool = False,
        truncate_by_rank: bool = True,
        leave: bool = False,
        max_scale: float = 1.0,
    ):
        """
        Converts the profiling results to a polars DataFrame for easier analysis and visualization.

        Parameters:
            method (int | tuple | None, optional): Filter method (see `filter_by` method).
            extracted_batch (tuple, optional): Batch indices to extract from the results.
            squeeze (bool, optional): Whether to squeeze singleton dimensions in the IPCs.
            truncate_by_rank (bool, optional): Whether to truncate IPCs by rank.
            leave (bool, optional): Whether to leave the progress bar after completion.
            max_scale (float, optional): Surrogate max scaling factor for IPC thresholding.

        Returns:
            df (pl.DataFrame): `polars.DataFrame` containing the profiling results.
            rank (np.ndarray): Rank array. The shape is equal to the batch shape.

        Examples:
            ```python
            df, rank = viewer.to_dataframe(method=3, squeeze=True)  # Convert results with degree sums of 3 to DataFrame
            df, rank = viewer.to_dataframe(method=(2, 1), truncate_by_rank=False)  # Convert results for degree tuple (2, 1) without truncation
            df, rank = viewer.to_dataframe(max_scale=2.0)  # Convert all results with surrogate max scaled by 2.0
            ```
        """
        keys = list(self.keys(method))
        batch = (slice(None), *extracted_batch, 0)
        max_length = max([len(key) for key in keys]) if len(keys) > 0 else 0
        degrees, components, delays, ipcs = [], [], [], []
        for degree_tuple, (delay, base, surr) in tqdm(
            self.items(method), total=len(keys), leave=leave, disable=not config.SHOW_PROGRESS_BAR
        ):
            degrees.append(np.full(len(delay), sum(degree_tuple), dtype=np.int32))
            c_mat = np.full((len(delay), max_length), -1, dtype=np.int32)
            c_mat[:, : len(degree_tuple)] = degree_tuple
            components.append(c_mat)
            d_mat = np.full((len(delay), max_length), -1, dtype=np.int32)
            d_mat[:, : len(degree_tuple)] = delay
            delays.append(d_mat)
            ipc = base[batch] * (
                base[batch]
                > self.calc_surr_max(surr=surr[batch], key=degree_tuple, max_scale=max_scale)
            )
            ipcs.append(ipc)
        rank = self.rank
        if max_length == 0:
            degrees = np.empty((0,), dtype=np.int32)
            components = np.empty((0,), dtype=np.int32)
            delays = np.empty((0,), dtype=np.int32)
            ipcs = np.empty((0, *rank.shape), dtype=np.float64)
        else:
            degrees = np.concatenate(degrees, axis=0)
            components = np.concatenate(components, axis=0)
            delays = np.concatenate(delays, axis=0)
            ipcs = np.concatenate(ipcs, axis=0)
        if squeeze:
            batch_shape = [dim for dim in ipcs.shape[1:] if dim != 1]
            ipcs = ipcs.reshape(-1, *batch_shape)
            rank = rank.reshape(*batch_shape)
        df = pl.DataFrame(
            {
                "degree": np.array(degrees),
                **{f"cmp_{idx}": components[:, idx] for idx in range(max_length)},
                **{f"del_{idx}": delays[:, idx] for idx in range(max_length)},
                **{
                    f"ipc_{'_'.join(map(str, idx))}": ipcs[(slice(None), *idx)]
                    for idx in np.ndindex(*ipcs.shape[1:])
                },
            }
        )
        if truncate_by_rank:
            for idx in np.ndindex(*ipcs.shape[1:]):
                col = f"ipc_{'_'.join(map(str, idx))}"
                df = df.sort(pl.col(col), descending=True)
                df = df.with_columns(pl.col(col).cum_sum().name.prefix("acc_"))
                df = df.with_columns(
                    pl.when(pl.col(f"acc_{col}") > rank[(*idx,)])
                    .then(0.0)
                    .otherwise(pl.col(col))
                    .alias(col)
                )
            df = df.select(~cs.starts_with("acc_")).sort(pl.col("degree"))
        return df, rank

    def total(self, method: int | tuple | None = None, max_scale: float = 1.0):
        """
        Calculates the total IPCs over all degree tuples stored in the results,
        optionally filtered by a specified method.

        Parameters:
            method (int | tuple | None, optional): Filter method (see `filter_by` method).
            max_scale (float, optional): Surrogate max scaling factor for IPC thresholding.

        Returns:
            total_ipc (np.ndarray | None): Total IPCs over all degree tuples. The shape is equal to the batch shape.

        Examples:
            ```python
            ipc_all = viewer.total()  # Calculate total IPCs for all degree tuples
            ipc_3 = viewer.total(method=3)  # Calculate total IPCs for degree sums of 3
            ipc_2_1 = viewer.total(method=(2, 1))  # Calculate total IPCs for degree tuple (2, 1)
            ```
        """
        ipcs = []
        for degree_tuple in self.keys(method):
            res = self[degree_tuple]
            if res is None:
                continue
            _delay, base, surr = res
            ipcs.append(
                base * (base > self.calc_surr_max(surr=surr, key=degree_tuple, max_scale=max_scale))
            )
        if len(ipcs) > 0:
            return np.concatenate(ipcs, axis=0).sum(axis=0)[..., 0]

    def save(self, path: str, **kwargs):
        """
        Saves the profiling results to a specified file path in either `.npz` or joblib format.

        Parameters:
            path (str): File path to save the results.
            kwargs (dict): Additional information to save alongside the results.

        Notes:
            If the extension is `.npz`, the results are saved in compressed format using [`numpy.savez_compressed`](https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html).
            Otherwise, they are saved using [`joblib.dump`](https://joblib.readthedocs.io/en/latest/generated/joblib.dump.html).

            `kwargs` can be used to store any additional metadata or information you want to associate with the profiling results.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if self.backend_name == "torch":
            self.backend.cuda.synchronize(self.us.device)
        if path.endswith(".npz"):
            with open(path, mode="wb") as f:
                np.savez_compressed(
                    f,
                    **{
                        "_".join(map(str, degree_tuple)) + f"/{key}": np.asarray(val)
                        for degree_tuple, (delay, base, surr) in self.items()
                        for key, val in dict(delay=delay, base=base, surr=surr).items()
                    },
                    **{f"kwargs/{key}": value for key, value in kwargs.items()},
                    rank=self.rank,
                )
        else:
            with open(path, mode="wb") as f:
                joblib.dump(
                    [{key: value for key, value in self.items()}, self.rank, kwargs],
                    f,
                    compress=True,
                )

    def load(self, path: str, method: int | tuple | None = None):
        if path.endswith(".npz"):
            with open(path, mode="rb") as f:
                npz = np.load(f)
                keys = sorted(
                    [
                        tuple(map(int, degree_str.split("_")))
                        for degree_str in set(
                            key.split("/")[0]
                            for key in npz.keys()
                            if key != "rank" and not key.startswith("kwargs")
                        )
                    ],
                    key=lambda v: (sum(v), *v),
                )
                if method is not None:
                    keys = filter(self.filter_by(method), keys)
                func = dict(
                    # delay=lambda v: list(map(tuple, v)),
                    delay=np.asarray,
                    base=np.asarray,
                    surr=np.asarray,
                )
                self.results = {
                    degree: tuple(
                        func[name](npz[f"{'_'.join(map(str, degree))}/{name}"])
                        for name in ["delay", "base", "surr"]
                    )
                    for degree in keys
                }
                self.rank = npz["rank"]
                rest = {
                    key.split("/")[1]: npz[key] for key in npz.keys() if key.startswith("kwargs")
                }

        else:
            with open(path, mode="rb") as f:
                self._results, self.rank, *rest = joblib.load(f)
            if len(rest) > 0:
                rest = rest[0]
            else:
                rest = {}
        self.info = rest


class UnivariateProfiler(UnivariateViewer):
    """
    Profiler class to calculate the IPCs for univariate input time series.

    Notes:
        This class inherits from `UnivariateViewer`, enabling it to load and convert profiling results into a DataFrame.
        It stores `us` and `xs`, allowing IPC calculations via the `calc` method.
        However, it does not support saving or loading time series data directly, as they can be large.
    """

    def __init__(
        self,
        us,
        xs,
        poly_name: str = "GramSchmidt",
        poly_param: dict | None = None,
        surrogate_num: int = 1000,
        surrogate_seed: int = 0,
        axis1: int = 0,
        axis2: int = -1,
        **regressor_kws,
    ):
        """
        Parameters:
            us (Any): Input time series. Must be at least 2D and univariate (shape: [t, ..., 1]).
            xs (Any): Output time series. Must be at least 2D (shape: [t, ..., N]).
            poly_name (str, optional): Polynomial class name to use, selectable from the `polynomial` module.
            poly_param (dict | None, optional): Parameters for the polynomial class.
            surrogate_num (int, optional): Number of surrogate datasets to generate.
            surrogate_seed (int, optional): Random seed for generating surrogate data.
            axis1 (int, optional): Axis for time steps; `us` and `xs` must match along this axis.
            axis2 (int, optional): Axis for variables; defaults to -1 (last axis) for both `us` and `xs`.
            regressor_kws (dict): Additional arguments for the `BatchRegressor` class.

        Notes:
            Currently supported backends are NumPy, CuPy, and PyTorch.
            The following conditions must be met for `us` and `xs`:

            - Both must use the same backend.
            - Both must be at least 2D arrays.
            - `axis1` and `axis2` must be different.
            - They must have the same size along `axis1` (time steps).
            - `us` must be univariate along `axis2` (i.e., size 1).

            `GramSchmidt` is recommended as the default polynomial class.
            If you know the specific distribution of `us`, other polynomial classes may perform better.
            See the table below for the correspondence between distributions and polynomial classes
            (Reference: [D. Xiu et al. 2002](https://epubs.siam.org/doi/10.1137/S1064827501387826)):

            | Distribution of `us` | Polynomial | Support |
            |-|-|-|
            | Normal (Gaussian) | `Hermite` | (-∞, ∞) |
            | Gamma | `Laguerre` | [0, ∞) |
            | Beta | `Jacobi` | [0, 1] |
            | Uniform | `Legendre` | [-1, 1] |
            | Binomial | `Krawtchouk` | {0, 1, ..., n} |

            `BatchRegressor` is used internally to compute IPCs in batches, allowing efficient processing of large datasets.
            The keyword arguments for `BatchRegressor` can be passed via `**regressor_kws`.

            | Option | Description | Default |
            |-|-|-|
            | `offset` | The offset applied to the time series data. | `1000` |
            | `debias` | If `True`, removes the mean from the data. | `True` |
            | `normalize` | If `True`, scales the data to unit variance. | `False` |
            | `threshold_mode` | Determines the singular value thresholding mode, either 'linear' or 'sqrt'. | `'linear'` |
        """
        assert get_backend_name(us) in ["numpy", "cupy", "torch"]
        assert get_backend_name(xs) in ["numpy", "cupy", "torch"]
        assert get_backend_name(us) == get_backend_name(xs)
        assert us.ndim >= 2 and xs.ndim >= 2, "us and xs should be multidimensional."
        assert axis1 != axis2, "axis1 and axis2 should be different"
        assert us.shape[axis1] == xs.shape[axis1], "should share the same time steps."
        assert us.shape[axis2] == 1, (
            f"us should be univariate (`us.shape[{axis2}] = 1`) but us's shape is {us.shape}."
        )
        assert hasattr(polynomial, poly_name), f"polynomial class named {poly_name} not found."
        self.axis1, self.axis2 = axis1, axis2
        self.backend = import_backend(us)
        self.us = self.backend.moveaxis(us, [self.axis1, self.axis2], [-2, -1])
        xs = self.backend.moveaxis(xs, [self.axis1, self.axis2], [-2, -1])
        if poly_param is None:
            poly_param = {}
        self.poly_cls = functools.partial(
            getattr(polynomial, poly_name), axis=-2, **poly_param
        )  # NOTE: GramSchmidt requires axis to be normalized
        self.poly = self.poly_cls(self.us)
        self.regressor = BatchRegressor(xs, **regressor_kws)
        length = self.us.shape[-2]
        rnd = np.random.default_rng(surrogate_seed)
        pbar = tqdm(
            rnd.spawn(surrogate_num), total=surrogate_num, disable=not config.SHOW_PROGRESS_BAR
        )
        pbar.set_description("random_seq")
        self.perms = np.zeros((surrogate_num, length), dtype=np.int32)
        for idx, rnd in enumerate(pbar):
            self.perms[idx] = make_permutation(length, rnd=rnd, tolist=False)
        self.perms = self.to_backend(self.perms)
        self.results = dict()
        if self.backend_name == "torch":
            # Pytorch wrapper
            if not hasattr(self.backend, "concatenate"):
                self.backend.concatenate = self.backend.concat

    @property
    def rank(self):
        return self.to_numpy(self.regressor.rank)

    def calc(
        self,
        degree_sum: int | tuple[int, ...] | list[int | tuple[int, ...]] = 1,
        delay_max: int | list[int] = 100,
        zero_offset: bool | int = True,
        method: int | tuple | None = None,
    ):
        """
        Calculate the IPCs for the given degree sums and delay ranges.

        Parameters:
            degree_sum (int | tuple | list, optional): Degree sums to compute.
            delay_max (int | list, optional): Delay ranges for the degree sums.
            zero_offset (bool | int, optional): Include zero delay or specify an offset.
            method (int | tuple | None, optional): Filter method (refer to `filter_by` method).

        Notes:
            The following table explains how `degree_sum` and `delay_max` parameters work together:

            | `degree_sum` | `delay_max` | Description |
            |-|-|-|
            | `int` | `int` | Calculate IPCs for all degree tuples with the specified degree sum and delay range. |
            | `list` | `list` | Calculate IPCs for each degree sum with corresponding delay ranges from the lists. |
            | Other combinations | - | Raises an assertion error. |

        Examples:
            ```python
            profiler.calc(1, 5)  # (1,) with delays 0 to 4.
            profiler.calc(2, 6, zero_offset=False)  # (1, 1), (2,) with delays 1 to 6.
            profiler.calc(2, 6, zero_offset=2) # (1, 1), (2,) with delays 2 to 7.
            profiler.calc([2, 3], [7, 8])  # (1, 1), (2,) with delays 0 to 6; (1, 1, 1), (2, 1), (3,) with delays 0 to 7.
            profiler.calc(4, 9, method=lambda key: max(key) >= 2)  # (4,), (3, 1), (2, 2), (2, 1, 1) with delays 0 to 8.
            profiler.calc(5, 10, method=-2)  # (4, 1), (3, 2) with delays 0 to 9.
            ```
        """
        assert type(degree_sum) in [int, tuple, list], "degree_sum should be int, tuple, or list."
        assert type(delay_max) in [int, list], "delay_max should be int or list."

        if type(degree_sum) is int:  # Sum of degrees to evaluate.
            degree_sum = [degree_sum]
        if type(delay_max) is int:  # Range of maximum delays.
            delay_max = [delay_max] * len(degree_sum)
        assert len(degree_sum) == len(delay_max)

        all_degree_tuples, all_delay_ranges = [], []
        for degree, delay in zip(degree_sum, delay_max, strict=True):
            degree_tuples = make_degree_list(degree)
            if method is not None:
                degree_tuples = list(filter(self.filter_by(method), degree_tuples))
            all_degree_tuples += degree_tuples
            if type(zero_offset) is int:
                all_delay_ranges += [range(zero_offset, zero_offset + delay)] * len(degree_tuples)
            elif zero_offset:
                all_delay_ranges += [range(0, delay)] * len(degree_tuples)
            else:
                all_delay_ranges += [range(1, delay + 1)] * len(degree_tuples)

        # Calculate the number of iteration (# of regressor call).
        total_length = [
            multi_combination_length(len(delay_range), *Counter(degree_tuple).values())
            for degree_tuple, delay_range in zip(all_degree_tuples, all_delay_ranges, strict=True)
        ]
        total_length = [v for v in total_length if v > 0]
        total_length = sum(total_length) + len(self.perms) * len(total_length)

        # Main loops.
        pbar = tqdm(total=total_length, disable=not config.SHOW_PROGRESS_BAR)
        for degree_tuple, delay_range in zip(all_degree_tuples, all_delay_ranges, strict=True):
            pbar.set_description(f"{truncate_tuple(degree_tuple)}")
            delay_list = make_delay_list(delay_range, degree_tuple)
            if len(delay_list) == 0:
                continue
            # Surrogate IPCs.
            ipc_surr = None
            delays = list(range(1, len(degree_tuple) + 1))
            for idx, perm in enumerate(self.perms):
                out = self.regressor(
                    self.poly, degree_tuple, delays, formatter=(..., perm, slice(None))
                )
                if ipc_surr is None:
                    ipc_surr = zeros_like(self.us, (len(self.perms), *out.shape))
                ipc_surr[idx] = out
                pbar.update(1)
            # Base IPCs.
            ipc_base = None
            for idx, delays in enumerate(delay_list):
                out = self.regressor(self.poly, degree_tuple, delays)
                if ipc_base is None:
                    ipc_base = zeros_like(self.us, (len(delay_list), *out.shape))
                ipc_base[idx] = out
                pbar.update(1)
            self.results[degree_tuple] = (delay_list, ipc_base, ipc_surr)
        pbar.close()
