#!/usr/bin/python3

# This script will check all terraform workspaces defined in tf_workspaces.json

# Imports
import sys
import json
import shlex
from subprocess import Popen, PIPE, STDOUT
from termcolor import colored


# Variables
jobFile = 'terraform-nanny.json'
errors = 0

# Check for path prefix
if len(sys.argv) > 1:
    pathPrefix = sys.argv[1]
    jobFile = pathPrefix + '/' + jobFile
else:
    pathPrefix = None


# Functions
def run_command(command, directory):

    cmd = shlex.split(command)
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=directory)
    output = proc.communicate()[0]

    return (output.decode('utf-8'), proc.returncode)


def run_terraform(workspace=None, directory='.'):
    cmd = "terraform plan -detailed-exitcode -lock=false"

    if workspace:
        cmd += ' -input=false -module-depth=-1 -var-file=terraform.tfvars \
        -var-file=env/' + workspace + '.tfvars'

    if refreshCmd:
        cmd += refreshCmd

    result = run_command(cmd, directory)

    if result[1] == 0:
        return(colored('No diff found!', 'green'))
    elif result[1] == 2:
        if alertCmd:
            alertCmdFormatted = alertCmd.format(project=directory,
                                                workspace=workspace)
            run_command(alertCmdFormatted, '.')
        return(colored('Diff found!\n' + result[0], 'yellow'))
    else:
        global errors
        errors += 1
        return(colored('Something went wrong!\n' + result[0], 'red'))


# Read workspaces.json
with open(jobFile) as json_data:
    job = json.load(json_data)

    print('\n' + colored('Running Terraform Nanny with:',
                         'magenta', attrs=['bold']))

    # Should we alert
    if job['alert']:
        alertCmd = job['alert']
        print('  Alert\t\t' + colored('True', 'green'))
    else:
        alertCmd = None
        print('  Alert\t\t' + colored('False', 'red'))

    # Should we run plan without refresh
    if job['refresh']:
        if job['refresh'] is True:
            refreshCmd = ' -refresh=true'
            print('  Refresh\t' + colored('True', 'green'))
        else:
            refreshCmd = None
            print('  Refresh\t' + colored('False', 'red'))

    # For all folders, run plan on all defined workspaces
    for task in job['tasks']:
        # Check for path prefix
        if pathPrefix:
            currentFolder = pathPrefix + '/' + task['folder']
        else:
            currentFolder = task['folder']

        msg = 'For folder "' + currentFolder + '" '
        run_command('terraform init', currentFolder)
        if 'workspaces' in task:
            msg += str(len(task['workspaces'])) + ' workspaces found'
            print(msg)
            for workspace in task['workspaces']:
                print('  ' + workspace)
                print('    ' + run_terraform(workspace=workspace,
                                             directory=currentFolder))
        else:
            msg += 'no workspaces found'
            print(msg)
            print('  ' + run_terraform(workspace=None,
                                       directory=currentFolder))

# Check for errors
if errors > 0:
    sys.exit(1)
else:
    sys.exit(0)
