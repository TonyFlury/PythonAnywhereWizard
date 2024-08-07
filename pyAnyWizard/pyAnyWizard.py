#!/usr/bin/env python3
# coding=utf-8
"""
    PythonAnywhereWizard.pyAnyWizard :

Summary :
    
    
Use Case :
    
    
Testable Statements :
    ...
"""
import os

import click
from os.path import basename
from pathlib import Path
from io import TextIOWrapper

from configparser import ConfigParser

from wizard_logging import logging, logging_levels,WizardLogger
from remote import PyAnyWhere
from pprint import pprint

CONFIG_FILE = 'pyAnyWizard.cfg'

# Define two CUSTOM logger levels for Verbosity 1 & 2

logger:WizardLogger = logging.getLogger('PythonAnywhereWizard')


@click.command()
@click.option('--config', '-c', type=click.File('r'), help='Config file with credentials',
              default=lambda: open(CONFIG_FILE, 'r') if Path(CONFIG_FILE).exists() else None,
              show_default = f'{CONFIG_FILE}')
@click.option('--verbose', '-v', type=click.IntRange(0,3), default=0,
              help = 'Verbosity level - 0 to 3 - 0 : Errors only, '
                     '1: High level progress, '
                     '2: lower level progress, '
                     '3 all details')
def main( config: TextIOWrapper = None, verbose=0):
    logger.setLevel(logging_levels[verbose])

    logger.info_v2(msg=f'Config file : {basename(config.name) if config else "None"}, Verbosity {verbose}')

    if config is None:
        click.secho('pyAnyWizard : Error - No Config file available. Wizard unable to continue - Aborting', fg='red')
        logger.critical('No Config file - execution aborted')
        exit()

    cfg = ConfigParser()
    cfg.read_file(config)
    missing_sections = {'PythonAnywhere', 'GitHub'}.difference(set(cfg.sections()))

    if missing_sections:
        missing = ','.join(f'[{x}]' for x in missing_sections)
        logger.critical( f'Incorrect Config file format - missing sections : {missing} - Execution Aborted')
        click.secho(f'PythonAnywhereWizard : Error - Config file does not contain the expected sections - missing {missing} - Aborting', fg='red')
        exit()

    e: Exception
    try:
        py_anywhere_access = PyAnyWhere(**cfg['PythonAnywhere'])
    except (AttributeError, ValueError) as e :
        logger.critical(f'Error with pythonAnywhere config : {str(e)} - Aborting')
        click.secho(f'PythonAnywhereWizard : {str(e)} - wizard unable to continue - aborting', fg='red')
        exit()

    try:
        py_anywhere_access.verify()
    except ConnectionRefusedError as e:
        logger.critical(f'Unable to verify connection to PythonAnywhere : {str(e)} - Aborting')
        click.secho(f'PythonAnywhereWizard : {str(e)} - wizard unable to continue - aborting', fg='red')

    print(list(py_anywhere_access.apps()))

    print(dict(list(x for x in py_anywhere_access.consoles_for_apps())))

    for out in py_anywhere_access.send_to_console(console_name='LiveTest', commands=['pwd','ls']):
        print(out)

if __name__ == '__main__':
    main()