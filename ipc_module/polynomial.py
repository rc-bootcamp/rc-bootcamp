#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Katsuma Inoue. All rights reserved.
# This code is licensed under the MIT License.

import inspect
import math
import sys
import warnings


class BasePolynomial(object):
    """
    Base class for polynomial classes using recurrence relations.

    Notes:
        When implementing a new polynomial type, follow these guidelines:

        - Inherit `BasePolynomial`.
        - `calc` method should be overridden in subclasses.
        - `super().__init__` should be called in the subclass constructor.
    """

    def __init__(self, xs, **_kwargs):
        self.xs = xs
        self.caches = {}

    def __getitem__(self, args):
        if type(args) is tuple:
            deg, sli = args[0], args[1:]
        else:
            deg, sli = args, ()
        assert deg >= 0
        if deg not in self.caches:
            self.caches[deg] = self.calc(deg)
        if len(sli) > 0:
            return self.caches[deg][sli]
        else:
            return self.caches[deg]

    def calc(self, *args, **kwargs):
        raise NotImplementedError


class Jacobi(BasePolynomial):
    """
    Jacobi polynomial class using recurrence relation
    (Cf. [Wikipedia](https://en.wikipedia.org/wiki/Jacobi_polynomials#Recurrence_relation)).
    """

    def __init__(self, xs, a: float, b: float, **_kwargs):
        """
        Parameters:
            xs (Any): Input values.
            a (float): Parameter a of the Jacobi polynomial.
            b (float): Parameter b of the Jacobi polynomial.
        """
        super(Jacobi, self).__init__(xs)
        self.a, self.b = a, b
        self.caches[0] = 1
        self.caches[1] = self.xs * (a + b + 2) / 2 + (a - b) / 2

    def calc(self, n: int):
        a = n + self.a
        b = n + self.b
        c = a + b
        d = 2 * n * (c - n) * (c - 2)
        e = (c - 1) * (c - 2) * c
        f = (c - 1) * (c - 2 * n) * (a - b)
        g = -2 * (a - 1) * (b - 1) * c

        res = (e / d) * self.xs * self[n - 1]
        res += (f / d) * self[n - 1]
        res += (g / d) * self[n - 2]
        return res


class Legendre(Jacobi):
    """
    Legendre polynomial is a special case of Jacobi polynomial with `a = b = 0`
    (Cf. [Wikipedia](https://en.wikipedia.org/wiki/Legendre_polynomials)).
    """

    def __init__(self, xs, **_kwargs):
        """
        Parameters:
            xs (Any): Input values.
        """
        super(Legendre, self).__init__(xs, 0, 0)


class Hermite(BasePolynomial):
    """
    Hermite polynomial class using recurrence relation
    (Cf. [Wikipedia](https://en.wikipedia.org/wiki/Hermite_polynomials#Recurrence_relation)).
    """

    def __init__(self, xs, normalize: bool = False, **_kwargs):
        """
        Parameters:
            xs (Any): Input values.
            normalize (bool, optional): Whether to use normalized Hermite polynomials.
        """
        super(Hermite, self).__init__(xs)
        if normalize:
            exp = math.e ** (-0.25 * (self.xs * self.xs))
            exp *= (2 * math.pi) ** -0.25
            self.caches[0] = exp
            self.caches[1] = exp * self.xs
        else:
            self.caches[0] = 1
            self.caches[1] = self.xs

    def calc(self, n: int):
        # res = self.xs * self[n - 1]
        # res -= (n - 1) * self[n - 2]
        res = math.sqrt(1 / n) * self.xs * self[n - 1]
        res -= math.sqrt((n - 1) / n) * self[n - 2]
        return res


class Laguerre(BasePolynomial):
    """
    Laguerre polynomial class using recurrence relation
    (Cf. [Wikipedia](https://en.wikipedia.org/wiki/Laguerre_polynomials#Generalized_Laguerre_polynomials)).
    """

    def __init__(self, xs, a=0, **_kwargs):
        """
        Parameters:
            xs (Any): Input values.
            a (float, optional): Parameter a of the Laguerre polynomial.
        """
        super(Laguerre, self).__init__(xs)
        self.a = a
        self.caches[0] = 1
        self.caches[1] = (a + 1) - self.xs

    def __getitem__(self, n: int):
        a = self.a
        res = ((2 * n - 1 + a) / n) * self[n - 1]
        res -= (1 / n) * self.xs * self[n - 1]
        res -= ((n - 1 + a) / n) * self[n - 2]
        return res


class Krawtchouk(BasePolynomial):
    """
    Krawtchouk polynomial class using three-term recurrence relation
    (Cf. [Wikipedia](https://en.wikipedia.org/wiki/Kravchuk_polynomials#Three_term_recurrence)).
    """

    def __init__(self, xs, N=2, p=0.5, **_kwargs):
        """
        Parameters:
            xs (Any): Input values.
            N (int, optional): Parameter N of the Krawtchouk polynomial.
            p (float, optional): Parameter p of the Krawtchouk polynomial.
        """
        super(Krawtchouk, self).__init__(xs)
        self.N, self.p = N, p
        self.caches[0] = 1
        self.caches[1] = 1 - self.xs * (1 / (self.N * self.p))

    def calc(self, n: int):
        assert n <= self.N, f"argument should be equal or less than N={self.N}, but {n} was given."
        res = (self.p * (self.N - n + 1) + (n - 1) * (1 - self.p) - self.xs) * self[n - 1]
        res -= (n - 1) * (1 - self.p) * self[n - 2]
        res /= self.p * (self.N - n + 1)
        return res


class GramSchmidt(BasePolynomial):
    """
    Gram-Schmidt polynomial class using the Gram-Schmidt process.
    """

    def __init__(self, xs, axis=None, depth=None, **_kwargs):
        """
        Parameters:
            xs (Any): Input values.
            axis (int | None, optional): Axis along which to perform the Gram-Schmidt process.
            depth (int | None, optional): Depth of orthogonalization. If `None`, full depth is used.

        Notes:
            If `axis` is `None`, be cautious when `xs` is multidimensional, as it might cause unexpected behavior.
            `axis=-2` is specified by the `BatchRegressor` class since the time dimension is the second-to-last dimension.
        """
        super(GramSchmidt, self).__init__(xs)
        if axis is None:
            warnings.warn(
                "Note that axis is set to `None`. Be careful when xs is multidimensional.",
                stacklevel=2,
            )
        self.axis = axis
        self.depth = depth
        self.caches[0] = 1

    def offset(self, n: int):
        return max(1, 1 if self.depth is None else n - self.depth)

    def calc(self, n: int):
        if n > 1:
            base = self[1] * self[n - 1]
        else:
            base = self.xs
        out = base - base.mean(axis=self.axis, keepdims=True)
        for i in range(self.offset(n), n):
            out -= (base * self[i]).sum(axis=self.axis, keepdims=True) * self[i]
        out *= (out * out).sum(axis=self.axis, keepdims=True) ** (-0.5)
        return out


__all__ = [name for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
