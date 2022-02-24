#!/usr/bin/env python3

"""
Helper functions to manage displaying information returned by our commands.
"""

import csv
import io


def print_display(*args, **kwargs):
    """
    Light wrapper around our display method which takes display's multiline output and prints it.
    Exists as a separate method to allow better unit-testing of the display code.
    """

    output = display(*args, **kwargs)
    print(output)


def display(titles, data, csv=False, show_titles=True):
    """
    Main display method.  Returns a string

    :param titles:
        ordered list of column titles, defines the header row of our output
    :param data:
        ordered list of dictionaries with the data to be displayed; each dictionary's keys should
        match (or be a subset of) our titles list
    :param csv:
        TODO: better docstring
    :param notitle:
        TODO: better docstring
    """

    # if we don't have any data, just stop now
    if len(data) == 0:
        return ''

    # convert our titles list and data dict into a 2D-array
    output_array = []
    if show_titles:
        # we may or may not display the titles
        output_array.append(titles)
    for row in data:
        output_array.append([
            str(row[title]) if title in row and row[title] is not None else '-'
            for title in titles
        ])

    # we're either displaying in CSV mode or standard mode
    if csv:
        return csv_display(output_array)
    else:
        # hide duplicates
        row_start = 0 if show_titles else 1
        for i in range(len(output_array) - 1, row_start, -1):
            for j in range(len(output_array[i])):
                if output_array[i][j] == output_array[i-1][j]:
                    output_array[i][j] = ''
                else:
                    break

        return standard_display(output_array)


def standard_display(output_array):
    """ Standard output (with spacing) of our output array"""

    # before we start writing any lines, we need to know the max width of every column
    max_widths = [0] * len(output_array[0])

    # look at each column one by one
    for i in range(len(output_array[0])):
        # get all values for that column
        values = [row[i] for row in output_array]

        # find the widest string
        max_widths[i] = max([len(str(v)) for v in values])

    # write and return our multiline output, with two spaces between columns
    spacing = '  '
    output = '\n'.join([
        spacing.join([
            value.ljust(max_widths[i])
            for i, value in enumerate(row)
        ]).rstrip()  # make sure that each row doesn't have trailing whitespace
        for row in output_array
    ])
    return output


def csv_display(output_array):
    """ CSV output of our output array """

    # csv writes to file handles, so let's make a string IO handle and build our csv writer on that
    handle = io.StringIO()
    writer = csv.writer(handle)
    for row in output_array:
        writer.writerow(row)

    # return the value held in the handle
    return handle.getvalue()
