# -*- coding: utf-8 -*-
"""Module to generate ascii charts.

This module provides a single function `plot` that can be used to generate an
ascii chart from a series of numbers. The chart can be configured via several
options to tune the output.
"""

from __future__ import division
from math import ceil, floor, isnan

__all__ = ['plot']

# Python 3.2 has math.isfinite, which could have been used, but to support older
# versions, this little helper is shorter than having to keep doing not isnan(),
# plus the double-negative of "not is not a number" is confusing, so this should
# help with readability.
def _isnum(n):
    return not isnan(n)

def plot(series, cfg=None):
    """Generate an ascii chart for a series of numbers.

    `series` should be a list of ints or floats. Missing data values in the
    series can be specified as a NaN. In Python versions less than 3.5, use
    float("nan") to specify an NaN. With 3.5 onwards, use math.nan to specify a
    NaN.

        >>> series = [1,2,3,4,float("nan"),4,3,2,1]
        >>> print(plot(series))
            4.00  ┤  ╭╴╶╮
            3.00  ┤ ╭╯  ╰╮
            2.00  ┤╭╯    ╰╮
            1.00  ┼╯      ╰

    `cfg` is an optional dictionary of various parameters to tune the appearance
    of the chart. `minimum` and `maximum` will clamp the y-axis and all values:

        >>> series = [1,2,3,4,float("nan"),4,3,2,1]
        >>> print(plot(series, {'minimum': 0}))
            4.00  ┼  ╭╴╶╮
            3.00  ┤ ╭╯  ╰╮
            2.00  ┤╭╯    ╰╮
            1.00  ┼╯      ╰
            0.00  ┤

        >>> print(plot(series, {'minimum': 2}))
            4.00  ┤  ╭╴╶╮
            3.00  ┤ ╭╯  ╰╮
            2.00  ┼─╯    ╰─

        >>> print(plot(series, {'minimum': 2, 'maximum': 3}))
            3.00  ┤ ╭─╴╶─╮
            2.00  ┼─╯    ╰─

    `height` specifies the number of rows the graph should occupy. It can be
    used to scale down a graph with large data values:

        >>> series = [10,20,30,40,50,40,30,20,10]
        >>> print(plot(series, {'height': 4}))
           50.00  ┤   ╭╮
           40.00  ┤  ╭╯╰╮
           30.00  ┤ ╭╯  ╰╮
           20.00  ┤╭╯    ╰╮
           10.00  ┼╯      ╰

    `format` specifies a Python format string used to format the labels on the
    y-axis. The default value is "{:8.2f} ". This can be used to remove the
    decimal point:

        >>> series = [10,20,30,40,50,40,30,20,10]
        >>> print(plot(series, {'height': 4, 'format':'{:8.0f}'}))
              50 ┤   ╭╮
              40 ┤  ╭╯╰╮
              30 ┤ ╭╯  ╰╮
              20 ┤╭╯    ╰╮
              10 ┼╯      ╰

    `color` is a list of ANSI escape sequences to colour the plot line on the
    graph. ANSI colours must be specified in the same order as the data series
    being plotted (when using multiple series). The colour list must contain
    an extra entry on the end which must be the clear/blanking ANSI colour
    code. If a single data series is being used, only one colour code needs to
    be provided in addition to the escape code. If no colours are provided the
    default terminal colour is used.

        >>> series = [10,20,30,40,50,40,30,20,10]
        >>> print(plot(series, {'height': 4, 'colors': ['\033[94m', '\033[0m']}))
           50.00  ┼   ╭╮
           37.50  ┤  ╭╯╰╮
           25.00  ┤╭─╯  ╰─╮
           12.50  ┼╯      ╰
            0.00  ┤
	"""

    if len(series) == 0:
        return ''

    if not isinstance(series[0], list):
        if all(isnan(n) for n in series):
            return ''
        else:
            series = [series]

    cfg = cfg or {}
    minimum = cfg.get('minimum', 0)
    maximum = cfg.get('maximum', 0)

    for i in range(0, len(series)):
        for j in range(0, len(series[i])):
            minimum = min(minimum, series[i][j])
            maximum = max(maximum, series[i][j])

    default_symbols = ['┼', '┤', '╶', '╴', '─', '╰', '╭', '╮', '╯', '│']
    symbols = cfg.get('symbols', default_symbols)
    colors = cfg.get('colors', ['\033[0m' for i in range(0, len(series)+1)])

    if minimum > maximum:
        raise ValueError('The minimum value cannot exceed the maximum value.')

    interval = maximum - minimum
    offset = cfg.get('offset', 3)
    height = cfg.get('height', interval)
    ratio = height / interval if interval > 0 else 1

    min2 = int(floor(minimum * ratio))
    max2 = int(ceil(maximum * ratio))

    def clamp(n):
        return min(max(n, minimum), maximum)

    def scaled(y):
        return int(round(clamp(y) * ratio) - min2)

    rows = max2 - min2

    width = 0
    for i in range(0, len(series)):
        width = max(width, len(series[i]))
    width += offset

    placeholder = cfg.get('format', '{:8.2f} ')

    result = [[' '] * width for i in range(rows + 1)]

    # axis and labels
    for y in range(min2, max2 + 1):
        label = placeholder.format(maximum - ((y - min2) * interval / (rows if rows else 1)))
        result[y - min2][max(offset - len(label), 0)] = label
        result[y - min2][offset - 1] = symbols[0] if y == 0 else symbols[1]  # zero tick mark

    # first value is a tick mark across the y-axis
    d0 = series[0][0]
    if _isnum(d0):
        result[rows - scaled(d0)][offset - 1] = symbols[0]

    for i in range(0, len(series)):

        # plot the line
        for x in range(0, len(series[i]) - 1):
            d0 = series[i][x + 0]
            d1 = series[i][x + 1]

            if isnan(d0) and isnan(d1):
                continue

            if isnan(d0) and _isnum(d1):
                result[rows - scaled(d1)][x + offset] = colors[i] + symbols[2] + colors[-1]
                continue

            if _isnum(d0) and isnan(d1):
                result[rows - scaled(d0)][x + offset] = colors[i] + symbols[3] + colors[-1]
                continue

            y0 = scaled(d0)
            y1 = scaled(d1)
            if y0 == y1:
                result[rows - y0][x + offset] = colors[i] + symbols[4] + colors[-1]
                continue

            result[rows - y1][x + offset] = (colors[i] + symbols[5] + colors[-1]) if y0 > y1 else (colors[i] + symbols[6] + colors[-1])
            result[rows - y0][x + offset] = (colors[i] + symbols[7] + colors[-1]) if y0 > y1 else (colors[i] + symbols[8] + colors[-1])

            start = min(y0, y1) + 1
            end = max(y0, y1)
            for y in range(start, end):
                result[rows - y][x + offset] = colors[i] + symbols[9] + colors[-1]

    return '\n'.join([''.join(row).rstrip() for row in result])