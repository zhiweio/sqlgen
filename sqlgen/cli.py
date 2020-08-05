#!/usr/bin/python
# -*- coding: utf8
import os
import sys

import click

from sqlgen import __version__, ddlgenerator, reader
from sqlgen.log import configure_logger


def version_msg():
    python_version = sys.version[:3]
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f'Porter %(version)s from {location} (Python {python_version})'


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__, '-V', '--version', message=version_msg())
@click.option(
    '-t', '--template', type=click.Path(exists=True, readable=True),
    help='file template'
)
@click.option(
    '--index', type=int, default=0, show_default=True,
    help='index of excel sheets'
)
@click.option(
    '-o', '--output', type=click.Path(), help='Save task template into file'
)
@click.option(
    '--debug-file', type=click.Path(), default=None,
    help='File to be used as a stream for DEBUG logging',
)
@click.option(
    '-v', '--verbose', is_flag=True, default=False, help='Print debug information'
)
def main(template, index, output, verbose, debug_file):
    configure_logger(stream_level='DEBUG' if verbose else 'INFO', debug_file=debug_file)
    template_data = reader.parse(template, index=index)
    sql = ddlgenerator.parse(template_data)
    if output:
        with open(output, 'w') as f:
            f.write(sql)
    else:
        print(sql)
