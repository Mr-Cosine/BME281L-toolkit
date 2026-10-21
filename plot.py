from plot_point import Plot_point, is_NaN, number, iterable
from linear_eq import Linear_eq

import math
import matplotlib.pyplot as plotter
from matplotlib.container import BarContainer
from matplotlib.font_manager import FontProperties

class Data_serie:
    """
    One series of points drawn on a plot, with its own name, color and trendline

    :ivar _plot_points: the valid points of the series
    :ivar _regression: the fitted line, None until `lin_reg` or `save_lin_reg` is called
    :ivar _name: the name shown in the legend
    :ivar _color: any matplotlib color, None to take the matching one from the default color cycle
    """
    _plot_points: list[Plot_point]
    _regression: Linear_eq | None
    _name: str
    _color: str | None

    def __init__(self, plot_points: iterable[Plot_point], drop_invalid:bool=True, name:str="data_serie", color:str=None):
        """
        :param plot_points: the points of the series
        :param drop_invalid: whether invalid points are silently dropped instead of raising
        :param name: the name shown in the legend
        :param color: any matplotlib color, None to take the matching one from the default color cycle

        :raises ValueError: if there is no valid point, or an invalid one while `drop_invalid` is False
        """
        valid_points = [p for p in plot_points if p.valid()]

        if len(valid_points) <= 0: raise ValueError("Bruh data serie does not have any valid data point. I could hire a grade 12 coop to do better.")
        if len(valid_points) != len(plot_points) and not drop_invalid: raise ValueError("Contains invalid data point.")

        self._plot_points = valid_points
        self._regression = None
        self._name = name
        self._color = color

    def lin_reg(self):
        """
        Fit a line through the points and keep it on the instance

        :return: None, the fit is stored in `regression`
        """
        self._regression = Linear_eq()
        self._regression.lin_reg(self._plot_points)

    def save_lin_reg(self, lin_eq: Linear_eq):
        """
        Update a line to the instance using externally created Linear_eq object.

        :param lin_eq: the line to save

        :return: None, the fit is stored in `regression`
        """
        self._regression = lin_eq

    def points(self) -> list[Plot_point]:
        """:return: the valid points of the series, as a new list so the series itself is not changed"""
        return list(self._plot_points)

    def regression(self) -> Linear_eq | None:
        """:return: the fitted line, None until `lin_reg` or `save_lin_reg` is called"""
        return self._regression

    def name(self) -> str:
        """:return: the name shown in the legend"""
        return self._name

    def color(self) -> str | None:
        """:return: the color of the series, None when it takes the matching one from the default color cycle"""
        return self._color

    def copy(self) -> Data_serie:
        """:return: a copied object of the serie"""

        return Data_serie(plot_points=self._plot_points, color=self.color, name=self.name, drop_invalid=False)

class Plot:
    """
    A plot of one or more data series sharing the same axes

    :ivar _plot_series: the series being plotted, in the order they were added
    :ivar _figure: the figure object, None until `plot` is called
    :ivar _axis: the axes object, None until `plot` is called
    :ivar _show_legend: whether the legend is drawn, as set by the last `plot`
    :ivar _legend_scale: size of the legend relative to the default, as set by the last `plot`
    """
    _plot_series: list[Data_serie]

    _figure: plotter.Figure
    _axis: plotter.Axes
    _show_legend: bool
    _legend_scale: number

    def __init__(self, *series: Data_serie):
        """
        :param series: the series to plot, each a Data_serie or a plain list of points
        """
        self._plot_series = []
        self._figure = None
        self._axis = None
        self._show_legend = True
        self._legend_scale = 1

        for serie in series: self.add_serie(serie)

    def create_serie(self, plot_points: iterable[Plot_point], name: str, color: str, drop_invalid: bool) -> None:
        """
        Add a series to the plot, drawn on the next `plot`

        :param plot_points: a plain list of Plot_points
        :param drop_invalid: whether invalid points of a plain list are silently dropped instead of raising
        :param name: the name shown in the legend, None to keep the one of the series
        :param color: any matplotlib color, None to keep the one of the series

        :return: None
        """
        self._plot_series.append(Data_serie(plot_points=plot_points, drop_invalid=drop_invalid, color=color, name=name))

    def add_serie(self, data: Data_serie) -> None:
        """
        Add a series to the plot, drawn on the next `plot`

        :param data: a Data_serie, copied so the plot never changes it
        :return: None
        """
        self._plot_series.append(data.copy())

    def lin_reg(self) -> None:
        """
        Fit a line through every series

        :return: None, each fit is stored in the `regression` of its series
        """
        for serie in self._plot_series: serie.lin_reg()

    def series(self) -> list[Data_serie]:
        """:return: the series being plotted, in the order they were added, as a new list"""
        return list(self._plot_series)

    def figure(self) -> plotter.Figure | None:
        """:return: the figure drawn by `plot`, None until `plot` is called"""
        return self._figure

    def axis(self) -> plotter.Axes | None:
        """:return: the axes drawn by `plot`, None until `plot` is called"""
        return self._axis

    def _points(self) -> list[Plot_point]:
        """
        :return: the points of every series, to size the axes

        :raises ValueError: if there is no series to plot
        """
        if not self._plot_series: raise ValueError("Nothing to plot, add a serie first.")
        return [p for serie in self._plot_series for p in serie.points()]

    def _serie_color(self, index: int) -> str:
        """:return: the color of the series at `index`, its own or the matching one of matplotlib's default cycle"""
        color = self._plot_series[index].color()
        return color if color is not None else f"C{index}"

    def _serie_label(self, index: int) -> str:
        """:return: the legend entry of the points of the series at `index`, its name"""
        return self._plot_series[index].name()

    def _trend_label(self, index: int, prec: int) -> str:
        """:return: the legend entry of the trendline of the series at `index`"""
        serie = self._plot_series[index]
        return f"{serie.name()} trend: {serie.regression().to_string(prec)}"

    def _draw_legend(self, axis: plotter.Axes) -> None:
        """
        Draw the legend on `axis` following `show_legend` and `legend_scale`

        The text and the markers are both scaled, so the legend keeps its proportions.

        :param axis: the axes to draw the legend on

        :return: None
        """
        if not self._show_legend: return
        if self._legend_scale <= 0: raise ValueError("Legend scale must be positive.")

        base_size = FontProperties(size=plotter.rcParams["legend.fontsize"]).get_size_in_points()
        axis.legend(fontsize=base_size * self._legend_scale, markerscale=self._legend_scale)

    @staticmethod
    def _ticks(lo: number, hi: number, steps: int, steplen: number = None) -> list[number]:
        """
        Tick positions spanning [lo, hi]

        Ticks sit on multiples of the step length, so 0 gets a tick whenever it is in view.
        Without a step length, the smallest round step (1, 2, 2.5 or 5 times a power of ten)
        that cuts the span into at most `steps` intervals is used.

        :param lo: lower bound of the axis
        :param hi: upper bound of the axis
        :param steps: maximum number of intervals to use when no step length is given
        :param steplen: distance between two consecutive ticks

        :return: the tick positions, in ascending order
        """

        if steplen is None:
            raw = (hi - lo) / steps
            if raw <= 0: return [lo, hi]

            magnitude = 10 ** math.floor(math.log10(raw))
            steplen = next(m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw)

        if steplen <= 0: raise ValueError("Tick step length must be positive.")

        first = math.ceil(lo / steplen)
        last = math.floor(hi / steplen)
        if first > last: return [lo, hi]  # the step is wider than the axis, keep the ends labelled

        return [round(i * steplen, 10) for i in range(first, last + 1)]  # round off float noise such as 0.30000000000000004

    def show(self) -> None:
        """
        Open the figure drawn by `plot`

        :return: None
        """
        from IPython.display import display
        if self._figure is None: raise ValueError("Nothing to show, plot first.")
        display(self._figure)

    def print_stats(self, print_points:bool=True, prec:int=3) -> None:
        """
        Print the points, the fitted equation and its R² of every series to the console

        :param print_points: whether to print the individual points
        :param prec: number of decimals shown for every figure
        :return: None
        """
        for i, serie in enumerate(self._plot_series):
            print(f"SERIE: {serie.name()}")

            if print_points:
                print("PLOT POINTS")
                print("========================")
                for p in serie.points():
                    print(f"x: {p.x():.{prec}f} y: {p.y():.{prec}f}")
                print("========================")

            if serie.regression() is not None:  # nothing fitted yet, or a plot type without regression
                print(f"LINEAR REGRESSION: {serie.regression().to_string(prec=prec, rval=False)}")
                print(f"DETERMINATION COEFFICIENT: {serie.regression().R2():.{prec}f}")

            if i < len(self._plot_series) - 1: print()

# ====================================================================================================================

class Scattered(Plot):
    def plot(self,
             width:int=None, height:int=None,
             tick_steps:int=8, x_steplen:number=None, y_steplen:number=None, x_tickrot:int=0, y_tickrot:int=0,
             leftbound:number=None, rightbound:number=None, lobound:number=None, hibound:number=None,
             xlabel:str=None, ylabel=None,
             trendline:bool=False, trendl_prec:int=3,
             errorbar:bool=False,
             point_label:bool=True, px_prec:int=3, py_prec:int=3,
             legend:bool=True, legend_scale:number=1,
             grid:bool=True) -> None:
        """
        Draw the figure, ready to be shown by `show`

        Every series is drawn on the same axes in its own color.
        Bounds left as None are taken from the data, with a little padding so the
        points and their labels do not touch the frame.

        :param width: width of the figure in inches, None for default to be 6.4
        :param height: height of the figure in inches, None for default to be 4.8
        :param tick_steps: number of intervals per axis when no step length is given
        :param x_steplen: distance between two x ticks, overrides `tick_steps`
        :param y_steplen: distance between two y ticks, overrides `tick_steps`
        :param x_tickrot: rotation of the x ticks in degrees (0 is horizontal, 90 is vertical)
        :param y_tickrot: rotation of the y ticks in degrees (0 is horizontal, 90 is vertical)
        :param leftbound: left edge of the x axis
        :param rightbound: right edge of the x axis
        :param lobound: bottom edge of the y axis
        :param hibound: top edge of the y axis
        :param xlabel: label of the x axis, omitted when None
        :param ylabel: label of the y axis, omitted when None
        :param trendline: whether to draw the fitted line of each series, fitting it first if needed
        :param trendl_prec: number of decimals shown in the trendline legend
        :param errorbar: whether to draw one standard deviation as error bars on points with a nonzero stdev
        :param point_label: whether each point is annotated with its coordinates
        :param px_prec: number of decimals of x in those annotations
        :param py_prec: number of decimals of y in those annotations
        :param legend: whether the legend is drawn
        :param legend_scale: size of the legend relative to the default, 2 doubles its text and markers
        :param grid: whether the grid is drawn

        :return: None, the figure is stored in `figure`
        """
        all_points = self._points()

        xmax = max(p.x() for p in all_points)
        xmin = min(p.x() for p in all_points)
        ymax = max(p.y() for p in all_points)
        ymin = min(p.y() for p in all_points)
        maxerr = max(p.stdev() for p in all_points) if errorbar else 0

        xspan = xmax - xmin
        yspan = ymax - ymin

        SCOPE_COEFF = 0.1  # changes how tight the graph fit to the boundaries of data set

        leftdom = leftbound if leftbound is not None else xmin - SCOPE_COEFF * xspan * 1/2
        rightdom = rightbound if rightbound is not None else xmax + SCOPE_COEFF * xspan * 1/2

        LABEL_HEADROOM = SCOPE_COEFF * 1/2 if point_label else 0  # extra top padding so the labels are not clipped

        loran = lobound if lobound is not None else ymin - maxerr - SCOPE_COEFF * yspan * 1/2
        hiran = hibound if hibound is not None else ymax + maxerr + (SCOPE_COEFF * 1/2 + LABEL_HEADROOM) * yspan

        x_ticks = self._ticks(leftdom, rightdom, tick_steps, x_steplen)
        y_ticks = self._ticks(loran, hiran, tick_steps, y_steplen)

        figsize = (width, height) if not any([width is None, height is None]) else None
        new_figure, new_figure_axis = plotter.subplots(figsize=figsize)

        EDGE_MARGIN = 0.1 * (rightdom - leftdom)
        for i, serie in enumerate(self._plot_series):
            color = self._serie_color(i)

            p_x = [p.x() for p in serie.points()]
            p_val = [p.y() for p in serie.points()]
            p_err = [p.stdev() if errorbar and p.stdev() > 0 else math.nan for p in serie.points()]

            new_figure_axis.errorbar(x=p_x, y=p_val, yerr=p_err,
                        fmt='o',
                        color=color,
                        capsize=5,
                        capthick=2,
                        elinewidth=1.5,
                        ecolor=color,
                        label=self._serie_label(i))
            if point_label:
                for x, y, err in zip(p_x, p_val, p_err):
                    if x - leftdom < EDGE_MARGIN: align = "left"
                    elif rightdom - x < EDGE_MARGIN: align = "right"
                    else: align = "center"

                    new_figure_axis.annotate(f"({x:.{px_prec}f}, {y:.{py_prec}f})",
                                xy=(x, y + (0 if is_NaN(err) else err)),
                                textcoords="offset points", xytext=(0, 6),
                                ha=align, va="bottom",
                                fontsize=8)

            if trendline:
                if serie.regression() is None: serie.lin_reg()

                new_figure_axis.axline((0, serie.regression().y_intercept()),
                          slope=serie.regression().slope(),
                          color=color,
                          linestyle='--',
                          label=self._trend_label(i, trendl_prec))

        if xlabel is not None: new_figure_axis.set_xlabel(xlabel)
        if ylabel is not None: new_figure_axis.set_ylabel(ylabel)

        self._show_legend, self._legend_scale = legend, legend_scale
        self._draw_legend(new_figure_axis)

        new_figure_axis.set_xlim(leftdom, rightdom)
        new_figure_axis.set_ylim(loran, hiran)

        new_figure_axis.set_xticks(x_ticks)
        new_figure_axis.set_yticks(y_ticks)
        new_figure_axis.tick_params(axis="x", labelrotation=x_tickrot)
        new_figure_axis.tick_params(axis="y", labelrotation=y_tickrot)

        new_figure_axis.grid(grid)
        new_figure_axis.minorticks_on()
        if grid: new_figure_axis.grid(which="minor", alpha=0.2)

        new_figure.tight_layout()

        self._figure = new_figure
        self._axis = new_figure_axis
        plotter.close(new_figure)

    def highlight(self, point, label, color="red"):
        """
        Draw emphasised markers for `points` on an already-plotted figure.

        :param point: the point to highlight, must be in one of the plotted series
        :param label: the label for the legend
        :param color: the color of the marker

        :return: None

        :raises ValueError: if the point is not in the plotted series
        """

        if not any(point in serie.points() for serie in self._plot_series): raise ValueError("Point is not in the plotted series.")

        base = self._axis.containers[0].lines[0]

        self._axis.scatter([point.x()], [point.y()],
                   s=base.get_markersize() ** 2,
                   linewidths=base.get_markeredgewidth(),
                   color=color, marker="o", zorder=5, label=label)

        self._draw_legend(self._axis)

class Line(Plot):
    def plot(self,
             width:int=None, height:int=None,
             tick_steps:int=8, x_steplen:number=None, y_steplen:number=None, x_tickrot:int=0, y_tickrot:int=0,
             leftbound:number=None, rightbound:number=None, lobound:number=None, hibound:number=None,
             xlabel:str=None, ylabel=None,
             trendline:bool=False, trendl_prec:int=3,
             errorbar:bool=False,
             show_points:bool=True, point_label:bool=True, px_prec:int=3, py_prec:int=3,
             legend:bool=True, legend_scale:number=1,
             grid:bool=True) -> None:
        """
        Draw the figure, ready to be shown by `show`

        Every series is drawn on the same axes in its own color, its points joined by
        straight segments in ascending x order.
        Bounds left as None are taken from the data, with a little padding so the
        points and their labels do not touch the frame.

        :param width: width of the figure in inches, None for default to be 6.4
        :param height: height of the figure in inches, None for default to be 4.8
        :param tick_steps: number of intervals per axis when no step length is given
        :param x_steplen: distance between two x ticks, overrides `tick_steps`
        :param y_steplen: distance between two y ticks, overrides `tick_steps`
        :param x_tickrot: rotation of the x ticks in degrees (0 is horizontal, 90 is vertical)
        :param y_tickrot: rotation of the y ticks in degrees (0 is horizontal, 90 is vertical)
        :param leftbound: left edge of the x axis
        :param rightbound: right edge of the x axis
        :param lobound: bottom edge of the y axis
        :param hibound: top edge of the y axis
        :param xlabel: label of the x axis, omitted when None
        :param ylabel: label of the y axis, omitted when None
        :param trendline: whether to draw the fitted line of each series, fitting it first if needed
        :param trendl_prec: number of decimals shown in the trendline legend
        :param errorbar: whether to draw one standard deviation as error bars on points with a nonzero stdev
        :param show_points: whether a marker is drawn on each point, False leaves only the line
        :param point_label: whether each point is annotated with its coordinates
        :param px_prec: number of decimals of x in those annotations
        :param py_prec: number of decimals of y in those annotations
        :param legend: whether the legend is drawn
        :param legend_scale: size of the legend relative to the default, 2 doubles its text and markers
        :param grid: whether the grid is drawn

        :return: None, the figure is stored in `figure`
        """
        all_points = self._points()

        xmax = max(p.x() for p in all_points)
        xmin = min(p.x() for p in all_points)
        ymax = max(p.y() for p in all_points)
        ymin = min(p.y() for p in all_points)
        maxerr = max(p.stdev() for p in all_points) if errorbar else 0

        xspan = xmax - xmin
        yspan = ymax - ymin

        SCOPE_COEFF = 0.1  # changes how tight the graph fit to the boundaries of data set

        leftdom = leftbound if leftbound is not None else xmin - SCOPE_COEFF * xspan * 1/2
        rightdom = rightbound if rightbound is not None else xmax + SCOPE_COEFF * xspan * 1/2

        LABEL_HEADROOM = SCOPE_COEFF * 1/2 if point_label else 0  # extra top padding so the labels are not clipped

        loran = lobound if lobound is not None else ymin - maxerr - SCOPE_COEFF * yspan * 1/2
        hiran = hibound if hibound is not None else ymax + maxerr + (SCOPE_COEFF * 1/2 + LABEL_HEADROOM) * yspan

        x_ticks = self._ticks(leftdom, rightdom, tick_steps, x_steplen)
        y_ticks = self._ticks(loran, hiran, tick_steps, y_steplen)

        figsize = (width, height) if not any([width is None, height is None]) else None
        new_figure, new_figure_axis = plotter.subplots(figsize=figsize)

        EDGE_MARGIN = 0.1 * (rightdom - leftdom)
        for i, serie in enumerate(self._plot_series):
            color = self._serie_color(i)

            sorted_points = sorted(serie.points(), key=lambda p: p.x())  # so the line runs left to right instead of zigzagging
            p_x = [p.x() for p in sorted_points]
            p_val = [p.y() for p in sorted_points]
            p_err = [p.stdev() if errorbar and p.stdev() > 0 else math.nan for p in sorted_points]

            new_figure_axis.errorbar(x=p_x, y=p_val, yerr=p_err,
                        fmt='o-' if show_points else '-',
                        color=color,
                        linewidth=1.5,
                        capsize=5,
                        capthick=2,
                        elinewidth=1.5,
                        ecolor=color,
                        label=self._serie_label(i))

            if point_label:
                for x, y, err in zip(p_x, p_val, p_err):
                    if x - leftdom < EDGE_MARGIN: align = "left"
                    elif rightdom - x < EDGE_MARGIN: align = "right"
                    else: align = "center"

                    new_figure_axis.annotate(f"({x:.{px_prec}f}, {y:.{py_prec}f})",
                                xy=(x, y + (0 if is_NaN(err) else err)),
                                textcoords="offset points", xytext=(0, 6),
                                ha=align, va="bottom",
                                fontsize=8)

            if trendline:
                if serie.regression() is None: serie.lin_reg()

                new_figure_axis.axline((0, serie.regression().y_intercept()),
                          slope=serie.regression().slope(),
                          color=color,
                          linestyle='--',
                          label=self._trend_label(i, trendl_prec))

        if xlabel is not None: new_figure_axis.set_xlabel(xlabel)
        if ylabel is not None: new_figure_axis.set_ylabel(ylabel)

        self._show_legend, self._legend_scale = legend, legend_scale
        self._draw_legend(new_figure_axis)

        new_figure_axis.set_xlim(leftdom, rightdom)
        new_figure_axis.set_ylim(loran, hiran)

        new_figure_axis.set_xticks(x_ticks)
        new_figure_axis.set_yticks(y_ticks)
        new_figure_axis.tick_params(axis="x", labelrotation=x_tickrot)
        new_figure_axis.tick_params(axis="y", labelrotation=y_tickrot)

        new_figure_axis.grid(grid)
        new_figure_axis.minorticks_on()
        if grid: new_figure_axis.grid(which="minor", alpha=0.2)

        new_figure.tight_layout()

        self._figure = new_figure
        self._axis = new_figure_axis
        plotter.close(new_figure)

    def highlight(self, point, label, color="red"):
        """
        Draw emphasised markers for `points` on an already-plotted figure.

        :param point: the point to highlight, must be in one of the plotted series
        :param label: the label for the legend
        :param color: the color of the marker

        :return: None

        :raises ValueError: if the point is not in the plotted series
        """

        if not any(point in serie.points() for serie in self._plot_series): raise ValueError("Point is not in the plotted series.")

        base = self._axis.containers[0].lines[0]

        self._axis.scatter([point.x()], [point.y()],
                   s=base.get_markersize() ** 2,
                   linewidths=base.get_markeredgewidth(),
                   color=color, marker="o", zorder=5, label=label)

        self._draw_legend(self._axis)

class Bar(Plot):
    """
    A bar chart of the data series, one bar per point rising from y = 0

    Several series are drawn as groups, the bars sharing an x side by side.
    A trendline does not belong on a bar chart, so linear regression is disabled.
    """
    def plot(self,
             width:int=None, height:int=None,
             tick_steps:int=8, x_steplen:number=None, y_steplen:number=None, x_tickrot:int=0, y_tickrot:int=0,
             xlabel:str=None, ylabel=None,
             bar_width:number=None,
             errorbar:bool=False,
             point_label:bool=True, px_prec:int=3, py_prec:int=3,
             legend:bool=True, legend_scale:number=1,
             grid:bool=True) -> None:
        """
        Draw the figure, ready to be shown by `show`

        Bounds left as None are taken from the data, with a little padding so the
        bars and their labels do not touch the frame. The y axis always includes 0.

        :param width: width of the figure in inches, None for default to be 6.4
        :param height: height of the figure in inches, None for default to be 4.8
        :param tick_steps: number of intervals on the y axis when no step length is given
        :param x_steplen: distance between two x ticks, None to put one tick under each group of bars
        :param y_steplen: distance between two y ticks, overrides `tick_steps`
        :param x_tickrot: rotation of the x ticks in degrees (0 is horizontal, 90 is vertical)
        :param y_tickrot: rotation of the y ticks in degrees (0 is horizontal, 90 is vertical)
        :param xlabel: label of the x axis, omitted when None
        :param ylabel: label of the y axis, omitted when None
        :param bar_width: width of each group of bars in x units, split evenly between the series,
                          None for 80% of the smallest gap between two x values
        :param errorbar: whether to draw one standard deviation as error bars on bars with a nonzero stdev
        :param point_label: whether each bar is annotated with its coordinates
        :param px_prec: number of decimals of x in those annotations
        :param py_prec: number of decimals of y in those annotations
        :param legend: whether the legend is drawn
        :param legend_scale: size of the legend relative to the default, 2 doubles its text and markers
        :param grid: whether the horizontal grid is drawn

        :return: None, the figure is stored in `figure`
        """
        all_points = self._points()
        distinct_x = sorted(set(p.x() for p in all_points))

        if bar_width is None:
            gaps = [b - a for a, b in zip(distinct_x, distinct_x[1:])]
            bar_width = 0.8 * min(gaps) if gaps else 0.8

        single_width = bar_width / len(self._plot_series)

        xmax = distinct_x[-1]
        xmin = distinct_x[0]
        ymax = max(max(p.y() for p in all_points), 0)  # bars rise from 0, so 0 must stay in view
        ymin = min(min(p.y() for p in all_points), 0)
        maxerr = max(p.stdev() for p in all_points) if errorbar else 0

        xspan = xmax - xmin
        yspan = ymax - ymin

        SCOPE_COEFF = 0.1  # changes how tight the graph fit to the boundaries of data set

        leftdom = xmin - bar_width / 2 - SCOPE_COEFF * xspan * 1/2
        rightdom = xmax + bar_width / 2 + SCOPE_COEFF * xspan * 1/2

        LABEL_HEADROOM = SCOPE_COEFF * 1/2 if point_label else 0  # extra padding so the labels are not clipped

        loran = ymin - maxerr - (SCOPE_COEFF * 1/2 + LABEL_HEADROOM) * yspan if ymin < 0 else 0
        hiran = ymax + maxerr + (SCOPE_COEFF * 1/2 + LABEL_HEADROOM) * yspan

        x_ticks = distinct_x if x_steplen is None else self._ticks(leftdom, rightdom, tick_steps, x_steplen)
        y_ticks = self._ticks(loran, hiran, tick_steps, y_steplen)

        figsize = (width, height) if not any([width is None, height is None]) else None
        new_figure, new_figure_axis = plotter.subplots(figsize=figsize)

        for i, serie in enumerate(self._plot_series):
            offset = (i - (len(self._plot_series) - 1) / 2) * single_width  # centres the group on its x value

            p_x = [p.x() for p in serie.points()]
            p_val = [p.y() for p in serie.points()]
            p_err = [p.stdev() if errorbar and p.stdev() > 0 else math.nan for p in serie.points()]

            new_figure_axis.bar([x + offset for x in p_x], p_val, width=single_width,
                        yerr=p_err if errorbar else None,
                        color=self._serie_color(i),
                        capsize=5,
                        error_kw={"capthick": 2, "elinewidth": 1.5, "ecolor": "black"},
                        label=self._serie_label(i))

            if point_label:
                for x, y, err in zip(p_x, p_val, p_err):
                    err = 0 if is_NaN(err) else err
                    upward = y >= 0  # labels sit past the end of the bar, above it or below a negative one

                    new_figure_axis.annotate(f"({x:.{px_prec}f}, {y:.{py_prec}f})",
                                xy=(x + offset, y + err if upward else y - err),
                                textcoords="offset points", xytext=(0, 6 if upward else -6),
                                ha="center", va="bottom" if upward else "top",
                                fontsize=8)

        if xlabel is not None: new_figure_axis.set_xlabel(xlabel)
        if ylabel is not None: new_figure_axis.set_ylabel(ylabel)

        self._show_legend, self._legend_scale = legend, legend_scale
        self._draw_legend(new_figure_axis)

        new_figure_axis.set_xlim(leftdom, rightdom)
        new_figure_axis.set_ylim(loran, hiran)

        new_figure_axis.set_xticks(x_ticks)
        new_figure_axis.set_yticks(y_ticks)
        new_figure_axis.tick_params(axis="x", labelrotation=x_tickrot)
        new_figure_axis.tick_params(axis="y", labelrotation=y_tickrot)

        new_figure_axis.grid(grid, axis="y")  # vertical grid lines would cut through the bars
        new_figure_axis.minorticks_on()
        new_figure_axis.tick_params(axis="x", which="minor", bottom=False)
        if grid: new_figure_axis.grid(which="minor", axis="y", alpha=0.2)
        new_figure_axis.set_axisbelow(True)

        new_figure.tight_layout()

        self._figure = new_figure
        self._axis = new_figure_axis
        plotter.close(new_figure)

    def highlight(self, point, label, color="red"):
        """
        Redraw the bar of `point` in another color on an already-plotted figure.

        :param point: the point to highlight, must be in one of the plotted series
        :param label: the label for the legend
        :param color: the color of the bar

        :return: None

        :raises ValueError: if the point is not in the plotted series
        """

        serie_index = next((i for i, serie in enumerate(self._plot_series) if point in serie.points()), None)
        if serie_index is None: raise ValueError("Point is not in the plotted series.")

        bar_groups = [c for c in self._axis.containers if isinstance(c, BarContainer)]  # the error bars get their own container
        base = bar_groups[serie_index].patches[self._plot_series[serie_index].points().index(point)]

        self._axis.bar(base.get_x() + base.get_width() / 2, point.y(), width=base.get_width(), color=color, label=label)

        self._draw_legend(self._axis)
