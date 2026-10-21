import numpy as np
import math

from _collections_abc import Sequence
number = float | int
iterable = Sequence

def is_NaN(num: number):
    return float(num) != float(num)

class Plot_point:
    """
    One column of the datasheet: an x value followed by its repeated measurements

    :ivar _xval: the x value, taken from the first usable entry of the column
    :ivar _yval: the remaining measurements
    :ivar _mean: average of `_yval`, the y value of the point
    :ivar _stdev: sample standard deviation of `_yval`, 0 for a single measurement
    """
    _xval: number | None
    _xname: str
    _yname: str
    _yval: np.ndarray | None
    _mean: float | None
    _stdev: float | None

    def __init__(self, input_x: number, input_y: list | number, xname: str = "x", yname: str = "y"):
        """
        Build a series from one raw column

        Non numeric entries, booleans and NaNs are dropped; if nothing is left
        every attribute stays None and the series should be skipped.

        :param xname: the name for independent variable
        :param yname: the name for dependent variable
        :param input_x: the independent variable data
        :param input_y: the dependent variable data across trials
        """
        yval = []
        for y in input_y if hasattr(input_y, "__iter__") and not isinstance(input_y, str) else [input_y]:
            try:
                numeric_y = float(y)
                if not is_NaN(numeric_y): yval.append(numeric_y)
            except (ValueError, TypeError): continue

        try:
            if len(yval) == 0: raise ValueError()
            self._xval = float(input_x)
            self._yval = np.array(yval)
            self._get_charactertistics()
        except Exception:
            self._xval = None
            self._yval = None
            self._mean = None
            self._stdev = None
        finally:
            self._xname = xname
            self._yname = yname

    @staticmethod
    def _calc_mean(data: np.ndarray) -> float:
        return float(sum(data)) / len(data)
    @staticmethod
    def _calc_stdev(data: np.ndarray, mean: float) -> float:
        return pow((sum((float(d) - mean) ** 2 for d in data) / (len(data)-1)), 1/2) if len(data) > 1 else 0

    def _get_charactertistics(self) -> None:
        """
        Get mean and standard deviation of the measurements

        :return: None, both are stored on the instance
        """
        self._mean = self._calc_mean(self._yval)
        self._stdev = self._calc_stdev(self._yval, self._mean)

    def x(self):
        """:return: the x coordinate of the point, the x value of the column"""
        return self._xval

    def y(self):
        """:return: the y coordinate of the point, the mean of the measurements"""
        return self._mean

    def stdev(self) -> float:
        """:return: the sample standard deviation of the measurements, 0 for a single measurement"""
        return self._stdev

    def measurements(self) -> np.ndarray | None:
        """:return: a copy of the measurements, None if the point is invalid"""
        return None if self._yval is None else self._yval.copy()

    def valid(self):
        return all([self._mean is not None, self._stdev is not None, self._xval is not None])

    def offset_y(self, offset: number) -> None:
        """
        Add a constant to the y values. Changes its mean, but not its standard deviation

        :param offset: the value to add

        :return: None, the y value is changed on the instance
        """
        for i in range(len(self._yval)): self._yval[i] += offset
        self._get_charactertistics()

    def scale_y(self, factor: number) -> None:
        """
        Scale the y values by a factor. Changes its mean, and standard deviation accordingly

        :param factor: the scaling factor

        :return: None, the y value is changed on the instance
        """
        self._yval *= factor
        self._get_charactertistics()

    def scale_x(self, factor: number) -> None:
        """
        Scale the x value by a factor

        :param factor: the scaling factor

        :return: None, the x value is changed on the instance
        """
        self._xval *= factor

    def log_x(self) -> None:
        """
        Take the natural logarithm of the x value

        :return: None, the x value is changed on the instance
        """
        self._xval = math.log(self._xval)

    def log_y(self) -> None:
        """
        Take the natural logarithm of the y values. Changes its mean, and standard deviation accordingly

        :return: None, the y value is changed on the instance
        """
        for i in range(len(self._yval)): self._yval[i] = np.log(self._yval[i])
        self._get_charactertistics()

    def __str__(self):
        s = f"Plot_point({self._xname}={self._xval}, {self._yname}={self._mean}"
        s += f", stdev={self._stdev}" if len(self._yval) > 1 else ""
        return f"{s})"
