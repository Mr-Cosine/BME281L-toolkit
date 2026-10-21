from plot_point import Plot_point
from plot import Scattered, Line, Bar, Data_serie

from _collections_abc import Sequence

number = float | int
iterable = Sequence

def analyze(data: list[list], x_loc: int = 0, y_loc: int = 1, xname: str = "x", yname: str = "y", trial_per_data: int = 0) -> list[Plot_point]:
    """
    analyze the data extracted from the datasheet

    :param data: the 2D data sheet, column first
    :param x_loc: the location of the dependent variable in each column / row
    :param y_loc: the location of the independent variable in each column / row
    :param trial_per_data: the number of trials per data point

    :return: the display function to call and show graph

    :raises ValueError: if the parameters are invalid (location out of range, overlapping for x and y data location, invalid number of trials)
    """
    if x_loc < 0 or x_loc >= len(data[0]): raise ValueError("x_loc is out of range.")
    if y_loc < 0 or y_loc >= len(data[0]): raise ValueError("y_loc is out of range.")
    if trial_per_data < 0 or trial_per_data >= len(data[0]): raise ValueError("trial_per_data is invalid.")
    if trial_per_data != 0 and x_loc >= y_loc and x_loc < y_loc + trial_per_data: raise ValueError("x_loc and y_loc are overlapping.")
    if trial_per_data == 0 and x_loc >= y_loc: raise ValueError("x_loc and y_loc are overlapping.")

    plot_points = []
    for col in data:
        new_plot_point = Plot_point(xname=xname,
                                    yname=yname,
                                    input_x=col[x_loc],
                                    input_y=col[y_loc:y_loc + trial_per_data] if trial_per_data > 0 and trial_per_data < len(col) else col[y_loc]
                                   )
        if new_plot_point.valid(): plot_points.append(new_plot_point)

    return plot_points

def generate_scattered(*series: Data_serie | iterable[Plot_point], lin_reg:bool = False) -> Scattered:
    """
    generate a scattered point plot with linear regression

    :param series: the series to plot, each a Data_serie or the data points obtained from analyze
    :param lin_reg: whether to include linear regression with the plot.

    :return: the scatterred plot object
    """
    plotted = Scattered(*series)
    if lin_reg: plotted.lin_reg()
    return plotted

def generate_line(*series: Data_serie | iterable[Plot_point], lin_reg:bool = False) -> Line:
    """
    generate a line plot with linear regression

    :param series: the series to plot, each a Data_serie or the data points obtained from analyze
    :param lin_reg: whether to include linear regression with the plot.

    :return: the line plot object
    """
    plotted = Line(*series)
    if lin_reg: plotted.lin_reg()
    return plotted

def generate_bar(*series: Data_serie | iterable[Plot_point]) -> Bar:
    """
    generate a bar plot

    :param series: the series to plot, each a Data_serie or the data points obtained from analyze

    :return: the bar plot object
    """
    return Bar(*series)