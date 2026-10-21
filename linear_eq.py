from plot_point import Plot_point

from _collections_abc import Sequence
number = float | int
iterable = Sequence

class Linear_eq:
    """
    A line y = slope * x + y_intercept, either given or fitted to data

    :ivar _slope: slope of the line
    :ivar _y_intercept: value of the line at x = 0
    :ivar _equation: the line as a callable, None until both coefficients are known
    :ivar _det_coeff: coefficient of determination R², only set by a fit or by the caller
    """
    _slope: number | None
    _y_intercept: number | None
    _equation: callable
    _det_coeff: number | None

    def __init__(self, slope = None, y_intercept = None, rval = None):
        """
        Build a line from known coefficients, or an empty one to fit later

        :param slope: slope of the line
        :param y_intercept: value of the line at x = 0
        :param rval: coefficient of determination R², if it is already known
        """
        self._slope = slope
        self._y_intercept = y_intercept
        self._equation = lambda x: self._slope * x + self._y_intercept if not any([slope is None, y_intercept is None]) else None
        self._det_coeff = rval

    def lin_reg(self, plot_points: iterable[Plot_point]) -> None:
        """
        Least-squares fit of y = slope * x + y_intercept

        slope = (sum(XY) - sum(X) * sum(Y) / n) / (sum(X^2) - sum(X)^2 / n)

        :param plot_points: the points to fit, one point (x, mean) each

        :return: None, the coefficients and R² are stored on the instance

        :raises ValueError: with fewer than two points, or if every x is the same
        """
        n = len(plot_points)
        if n < 2: raise ValueError("Linear regression needs at least two points.")

        sum_x = sum(d.x() for d in plot_points)
        sum_y = sum(d.y() for d in plot_points)
        sum_xy = sum(d.x() * d.y() for d in plot_points)
        sum_xx = sum(d.x() ** 2 for d in plot_points)

        denominator = sum_xx - sum_x ** 2 / n
        if denominator == 0: raise ValueError("All x values are identical, the fit is a vertical line.")

        self._slope = (sum_xy - sum_x * sum_y / n) / denominator
        self._y_intercept = sum_y / n - self._slope * sum_x / n

        self._equation = lambda x: self._slope * x + self._y_intercept

        res_sum = sum((d.y() - self._equation(d.x())) ** 2 for d in plot_points)
        tot_sum = sum((d.y() - sum_y/n) ** 2 for d in plot_points)
        self._det_coeff = 1 - res_sum / tot_sum

    def predict(self, x: number):
        """
        Evaluate the line at one point

        :param x: the abscissa to evaluate at

        :return: the value of the line at `x`

        :raises ValueError: if the line has no coefficients yet
        """
        if any([self._slope is None, self._y_intercept is None]): raise ValueError("Parameter is not complete.")
        if self._equation is not None: return self._equation(x)

    def to_string(self, prec:int=3, rval:bool=False):
        """
        Render the line as readable text, for a legend or a printout

        :param prec: number of decimals shown for every figure
        :param rval: whether the R² of the fit is appended

        :return: the equation, e.g. "y = 2.000 * x + 1.000  R² = 0.999" / "y = 2.000 * x + 1.000"

        :raises ValueError: if any value is missing (did not perform lin_reg() or did not pass the corresponding value when initialize)
        """
        if any([self._slope is None, self._y_intercept is None, rval is True and self._det_coeff is None]): raise ValueError("Parameter is not complete.")
        sign = "-" if self._y_intercept < 0 else "+"
        return f"y = {self._slope:.{prec}f} * x {sign} {abs(self._y_intercept):.{prec}f}" + (f"  R² = {self._det_coeff:.{prec}f}" if rval else "")

    def slope(self) -> number:
        """
        :return: the slope of the fit

        :raises ValueError: if no fit has been run and none was given
        """
        if self._slope is None: raise ValueError("Parameter is not complete.")
        return self._slope

    def y_intercept(self) -> number:
        """
        :return: the y intercept of the fit

        :raises ValueError: if no fit has been run and none was given
        """
        if self._y_intercept is None: raise ValueError("Parameter is not complete.")
        return self._y_intercept

    def R2(self) -> number:
        """
        :return: the coefficient of determination of the fit

        :raises ValueError: if no fit has been run and none was given
        """
        if self._det_coeff is None: raise ValueError("Parameter is not complete.")
        return self._det_coeff
