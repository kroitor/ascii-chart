"use strict";

(function (exports) {
    // control sequences for coloring
    exports.black = "\x1b[30m"
    exports.red = "\x1b[31m"
    exports.green = "\x1b[32m"
    exports.yellow = "\x1b[33m"
    exports.blue = "\x1b[34m"
    exports.magenta = "\x1b[35m"
    exports.cyan = "\x1b[36m"
    exports.lightgray = "\x1b[37m"
    exports.default = "\x1b[39m"
    exports.darkgray = "\x1b[90m"
    exports.lightred = "\x1b[91m"
    exports.lightgreen = "\x1b[92m"
    exports.lightyellow = "\x1b[93m"
    exports.lightblue = "\x1b[94m"
    exports.lightmagenta = "\x1b[95m"
    exports.lightcyan = "\x1b[96m"
    exports.white = "\x1b[97m"
    exports.reset = "\x1b[0m"

    /**
     * Wraps a given character in ANSI color escape codes if color is passed in
     * 
     * @param {string} char - symbol to color
     * @param {string} color - ANSI color code
     * @returns {string}
     */
    function colored (char, color) {
        // do not color it if color is not specified
        return color ? `${color}${char || ''}${exports.reset}` : char
    }

    exports.colored = colored

    /**
     * @typedef {Object} Config
     * @property {number} [min] - minimum value of any series (default: auto)
     * @property {number} [max] - maximum value of any series (default: auto)
     * @property {number} [offset=3] - axis offset from the left
     * @property {string} [padding='       '] - padding string for label formatting
     * @property {number} [height] - height of the chart (default: max - min)
     * @property {string[]} [colors] - array of ANSI color codes to use for each series (default: built-in presets)
     * @property {string[]} [symbols] - array of symbols to use for each series (defaults: ┼, ┤, ╶, ╴, ─, ╰, ╭, ╮, ╯, and │)
     * @property {(x: number, i: number) => string} [format] - function to format each label. Optional second parameter is the index
     */

    /**
     * Takes in a series of numbers and "plots" them as a line chart 
     * using ASCII characters. Returned as a string with newlines 
     * separating each line.
     * 
     * @param {number[] | number[][]} series - if an array of numbers is passed in, it will be transformed into an array of a single series
     * @param {Config} [cfg={}] - configuration object
     * @returns {string}
     */
    const plot = function (series, cfg = {}) {
        if (typeof(series[0]) == "number") series = [series]

        const defaultSymbols = [ '┼', '┤', '╶', '╴', '─', '╰', '╭', '╮', '╯', '│' ]
        const defaultPadding = '           '

        let { 
            min       = Math.min(...series.flat()), 
            max       = Math.max(...series.flat()),
            offset    = 3,
            padding   = defaultPadding,
            height,
            colors    = [],
            symbols   = defaultSymbols,
            format
        } = cfg;
        const range   = Math.abs(max - min)
        height        = height ?? range
        format        = format ?? (x => (padding + x.toFixed(2)).slice(-padding.length))
        const ratio   = range ? height / range : 1
        const min2    = Math.round(min * ratio)
        const max2    = Math.round(max * ratio)
        const rows    = Math.abs(max2 - min2)
        const width   = offset + Math.max(0, ...series.map(s => s.length))

        // instantiate result as 2d array of spaces of size (rows + 1) x width
        let result = Array.from(new Array(rows + 1), () => new Array(width).fill(' '))

        // axis + labels
        for (let y = min2; y <= max2; ++y) {
            let label = format(rows ? max - (y - min2) * range / rows : y, y - min2)
            result[y - min2][Math.max(offset - label.length, 0)] = label
            result[y - min2][offset - 1] = (y == 0) ? symbols[0] : symbols[1]
        }

        // plot each series
        for (let j = 0; j < series.length; j++) {
            let currentColor = colors[j % colors.length]
            let y0 = Math.round(series[j][0] * ratio) - min2
            result[rows - y0][offset - 1] = colored(symbols[0], currentColor) // first value

            // plot the line
            for (let x = 0; x < series[j].length - 1; x++) {
                let y0 = Math.round(series[j][x + 0] * ratio) - min2
                let y1 = Math.round(series[j][x + 1] * ratio) - min2
                if (y0 == y1) {
                    result[rows - y0][x + offset] = colored(symbols[4], currentColor)
                } else {
                    result[rows - y1][x + offset] = colored((y0 > y1) ? symbols[5] : symbols[6], currentColor)
                    result[rows - y0][x + offset] = colored((y0 > y1) ? symbols[7] : symbols[8], currentColor)
                    let from = Math.min (y0, y1)
                    let to = Math.max (y0, y1)
                    for (let y = from + 1; y < to; y++) {
                        result[rows - y][x + offset] = colored(symbols[9], currentColor)
                    }
                }
            }
        }

        return result.map(x => x.join('')).join('\n')
    }

    exports.plot = plot
}) (typeof exports === 'undefined' ? /* istanbul ignore next */ this['asciichart'] = {} : exports);
