# BME 281L Toolkit

Toolkit for library for analysis in BME 281L
Python helpers for reading lab data from Excel spreadsheets, organizing it into data points, fitting linear trendlines, and plotting the results.

## Files

- **file_read.py**: Reads an Excel file into a 2D list (`extract_data`), with helpers to transpose a matrix (`transpose`) and unpack single-element lists (`unpack_list`).
- **plot_point.py**: `Plot_point`, a single data point: an x value and one or more repeated y measurements. Also includes `is_NaN` and shared type aliases.
- **linear_eq.py**: `Linear_eq`, a line `y = slope * x + y_intercept` that you either give directly or fit to data points.
- **plot.py**: The plotting classes, built on matplotlib.
  - `Data_serie`: one series of points with its own name, color, and trendline
  - `Plot`: base class for a plot of one or more series that share the same axes
  - `Scattered`, `Line`, `Bar`: scatter, line, and bar charts
- **analysis.py**: Functions that tie everything together.
  - `analyze`: turns a data sheet into a list of `Plot_point`s
  - `generate_scattered`, `generate_line`, `generate_bar`: build a plot from one or more series, with optional linear regression for scatter and line plots

## Dependencies

- numpy
- pandas (plus an Excel engine such as openpyxl)
- matplotlib
