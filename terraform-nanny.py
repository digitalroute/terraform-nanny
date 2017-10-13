#!/usr/bin/python3

# This script will check all terraform workspaces defined in tf_workspaces.json

# Imports
import sys
import json
import shlex
import configparser
from subprocess import Popen, PIPE, STDOUT


# Read config
config = configparser.ConfigParser()
config.read('nanny.ini')


# Variables
jobFile = 'terraform-nanny.json'
errors = 0

if config.has_option('alert', 'command'):
    alertCmd = config.get('alert', 'command')


# Functions
def run_command(command, directory):

    cmd = shlex.split(command)
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=directory)
    output = proc.communicate()[0]

    return (output.decode('utf-8'), proc.returncode)


def run_terraform(workspace=None, directory='.'):
    if workspace:
        cmd = 'terraform plan -input=false -refresh=true -module-depth=-1 \
        -var-file=terraform.tfvars -var-file=env/' + workspace + '.tfvars \
        -detailed-exitcode'
    else:
        cmd = 'terraform plan -detailed-exitcode'

    result = run_command(cmd, directory)

    if result[1] == 0:
        return('No diff found!')
    elif result[1] == 2:
        if alertCmd:
            alertCmdFormatted = alertCmd.format(project=directory,
                                                workspace=workspace)
            run_command(alertCmdFormatted, '.')
        return('Diff found!\n' + result[0])
    else:
        global errors
        errors += 1
        return('Something went wrong!\n' + result[0])


# Read workspaces.json
with open(jobFile) as json_data:
    job = json.load(json_data)

    # For all folders, run plan on all defined workspaces
    for task in job['tasks']:
        msg = 'For folder "' + task['folder'] + '" '
        run_command('terraform init', task['folder'])
        if 'workspaces' in task:
            msg += str(len(task['workspaces'])) + ' workspaces found'
            print(msg)
            for workspace in task['workspaces']:
                print('  ' + workspace)
                print('    ' + run_terraform(workspace=workspace,
                                             directory=task['folder']))
        else:
            msg += 'no workspaces found'
            print(msg)
            print('  ' + run_terraform(workspace=None,
                                       directory=task['folder']))

# Check for errors
if errors > 0:
    sys.exit(1)
else:
    sys.exit(0)
