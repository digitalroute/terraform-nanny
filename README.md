# Terraform Nanny

[![Build Status](https://travis-ci.org/digitalroute/terraform-nanny.svg?branch=master)](https://travis-ci.org/digitalroute/terraform-nanny)

This project aims to alert developers about Terraform plans that are out of sync. When having multiple projects with mutltiple workspaces it is hard to keep track of which workspaces where actually applied with which changes. It could even be so that developers forget to apply their changes in all workspaces.

Enter Nanny! Enabled in your build-cyckle Terraform Nanny will read ```terraform-nanny.json``` which describes your projects folder-structure and which workspaces to build in each folder. In [the attached example](https://github.com/digitalroute/terraform-nanny/blob/master/example/terraform-nanny.json) there are three separate terraform enabled folders. One has [enabled workspaces](https://github.com/digitalroute/terraform-nanny/blob/master/example/terraform-nanny.json#L10) and thus built once for each entry in ```workspaces```, the other two are built once.

Terraform Nanny will only fail your build if terraform for some reason breaks, Nanny's only job is to alert developers about plans not applied.

## Install

Using TravisCI, download the latest terraform-nanny.py in your install step and run.
Terraform Nanny should run fine with your other build-steps.

```yml
sudo: false
python:
  - 3.6
install:
  - curl -fSL "https://raw.githubusercontent.com/digitalroute/terraform-nanny/master/terraform-nanny.py" -o terraform-nanny.py
script: python terraform-nanny.py
```

## Docker image

Use the pushed docker image in your buildstep to check your currnet source folder. You need to pass your credentials to the container.

```docker run -e AWS_ACCESS_KEY_ID={YOUR_KEY} -e AWS_SECRET_ACCESS_KEY={YOUR_SECRET} -v `pwd`:/src digitalroute/terraform-nanny```
