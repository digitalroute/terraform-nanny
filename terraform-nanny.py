#!/usr/bin/python3

# This script will check all terraform plans and workspaces defined in terraform-nanny.json

# Imports
import sys
import json
import shlex
from subprocess import Popen, PIPE, STDOUT
from termcolor import colored


# Variables
jobFile = 'terraform-nanny.json'
errors = 0
alertCmd = None
okCmd = None
refreshCmd = None


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


def run_terraform(workspace=None, directory='.', refreshCmd=None):
    global errors

    cmd = "terraform plan -detailed-exitcode -lock=false -no-color"

    folder = directory.split('/')[-1]

    if workspace:
        # Switch workspace
        switch = run_command('terraform workspace select ' + workspace, directory)
        if switch[1] != 0:
            errors += 1
            return(colored('Something went wrong!\n' + switch[0], 'red'))

        cmd += ' -input=false -module-depth=-1 -var-file=terraform.tfvars \
        -var-file=env/' + workspace + '.tfvars'

    if refreshCmd:
        cmd += refreshCmd

    result = run_command(cmd, directory)

    if result[1] == 0:
        return(colored('No diff found!', 'green'))
    elif result[1] == 2:
        if alertCmd:
            alertCmdFormatted = alertCmd.format(project=project,
                                                folder=folder,
                                                workspace=workspace)
            run_command(alertCmdFormatted, '.')
        return(colored('Diff found!\n' + result[0], 'yellow'))
    else:
        errors += 1
        return(colored('Something went wrong!\n' + result[0], 'red'))


# Read workspaces.json
with open(jobFile) as json_data:
    job = json.load(json_data)

    print('\n' + colored('Running Terraform Nanny with:',
                         'magenta', attrs=['bold']))

    if 'name' in job:
        project = job['name']
    else:
        print(colored('Exit: Name is missing in terraform-nanny.json', 'red'))
        sys.exit(1)

    # Should we send alert messages
    if 'alert' in job:
        alertCmd = job['alert']
        print('  Alert  \t' + colored('True', 'green'))
    else:
        print('  Alert  \t' + colored('False', 'red'))

    # Should we send OK messages
    if 'ok' in job:
        okCmd = job['ok']
        print('  Ok  \t' + colored('True', 'green'))
    else:
        print('  Ok  \t' + colored('False', 'red'))

    # Should we run plan without refresh
    if 'refresh' in job:
        if job['refresh'] is True:
            refreshCmd = ' -refresh=true'
            print('  Refresh\t' + colored('True', 'green'))
        else:
            refreshCmd = None
            print('  Refresh\t' + colored('False', 'red'))

    print('\n')

    # For all folders, run plan on all defined workspaces
    for task in job['tasks']:
        # Keep track of current number of errors, to see if we add to them
        errorsBeforeTask = errors

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
                                             directory=currentFolder,
                                             refreshCmd=refreshCmd))
        else:
            msg += 'no workspaces found'
            print(msg)
            print('  ' + run_terraform(workspace=None,
                                       directory=currentFolder))

        # Check for errors, else send okCmd
        if okCmd:
            if errors == errorsBeforeTask:
                okCmdFormatted = okCmd.format(project=project, folder=currentFolder)
                run_command(okCmdFormatted, '.')

# Check for errors
if errors > 0:
    sys.exit(1)
else:
    sys.exit(0)
