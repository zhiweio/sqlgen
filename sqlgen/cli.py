#!/usr/bin/python
# -*- coding: utf8
import os
import re
import sys

import click

from sqlgen import __version__, ddlgenerator, reader
from sqlgen.log import configure_logger


def parse_sheets(arg):
    sheets = list()
    # one sheet
    if re.match(r"^\d+$", arg):
        sheets.append(int(arg))

    # range of sheets
    elif re.match(r"^\d+\-\d+$", arg):
        start, end = arg.split("-")
        start, end = int(start), int(end)
        if end < start:
            raise click.BadParameter(
                "end sheet index must be greater than start sheet index"
            )
        sheets.extend(list(range(start, end + 1)))

    elif re.match(r"^\d+(,\d+)*$", arg):
        sheets.extend(set([int(s) for s in arg.split(",")]))

    else:
        raise click.BadParameter("Invalid sheet index")

    return sheets


def version_msg():
    python_version = sys.version[:3]
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f"Porter %(version)s from {location} (Python {python_version})"


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "-V", "--version", message=version_msg())
@click.option(
    "-t",
    "--template",
    type=click.Path(exists=True, readable=True),
    help="file template",
)
@click.option(
    "-s",
    "--sheets",
    type=str,
    default="0",
    show_default=True,
    help="index of excel sheets, eg: 1-6",
)
@click.option("-o", "--output", type=click.Path(), help="Save task template into file")
@click.option(
    "--debug-file",
    type=click.Path(),
    default=None,
    help="File to be used as a stream for DEBUG logging",
)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Print debug information"
)
def main(template, sheets, output, verbose, debug_file):
    configure_logger(stream_level="DEBUG" if verbose else "INFO", debug_file=debug_file)

    clauses = list()
    for sheet in parse_sheets(sheets):
        template_data = reader.parse(template, index=sheet)
        table = ddlgenerator.parse(template_data)
        sql = table.clause()
        clauses.append(sql)

    clauses = "\n".join(clauses)

    if output:
        with open(output, "w") as f:
            f.write(clauses)
    else:
        print(clauses)
