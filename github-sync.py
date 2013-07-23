#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NOTE: Modified script to use Github's v3 API. Also, the watched folder is 
no longer checked out

Kenneth Reitz's GitHub Syncer

This script uses the GitHub API to get a list of all forked, mirrored, public, and 
private repos in your GitHub account. If the repo already exists locally, it will 
update it via git-pull. Otherwise, it will properly clone the repo.

It will organize your repos into the following directory structure:

+ repos
  ├── forks    (public fork repos)
  ├── mirrors  (public mirror repos)
  ├── private  (private repos)
  ├── public   (public repos)
  ├── watched  (public watched repos)
  └── sync.py  (this script)

Requirements: 
$ pip install pygithub3

Inspired by Gisty (http://github.com/swdyh/gisty). 
"""

import os
from commands import getoutput as cmd

from pygithub3.github import Github


# GitHub configurations
GITHUB_USER = cmd('git config github.user')
GITHUB_TOKEN = cmd('git config github.token')

# API Object
print '======================================================'
print 'GitHub Username: %s' % GITHUB_USER
print 'GitHub Token: %s' % GITHUB_TOKEN
print '======================================================\n'

github = Github(username=GITHUB_USER, token=GITHUB_TOKEN)


# repo slots
repos = {}

# repos['watched'] = [r for r in github.repos.watchers.list_repos().all()]
repos['private'] = []
repos['mirrors'] = []
repos['public'] = []
repos['forks'] = []

# Collect GitHub repos via API
for repo in github.repos.list().all():

    if repo.private:
        repos['private'].append(repo)
    elif repo.fork:
        repos['forks'].append(repo)
    elif 'mirror' in repo.description.lower():
        # mirrors owned by self if mirror in description...
        repos['mirrors'].append(repo)
    else:
        repos['public'].append(repo)

    # print repo.private, repo.fork, repo

for org, reps in repos.iteritems():
    for repo in reps:
        
        # create org directory (safely)
        try:
            os.makedirs(org)
        except OSError:
            pass
        
        # enter org dir
        os.chdir(org)
        
        # I own the repo
        private = True if org in ('private', 'fork', 'mirror') else False

        # just `git pull` if it's already there
        if os.path.exists(repo.name):
            os.chdir(repo.name)
            print('Updating repo: %s' % (repo.name))
            os.system('git pull')
            os.chdir('..')
        else:
            if private:
                print('Cloning private repo: %s' % (repo.name))
                print 'git clone https://github.com/%s/%s.git' % (repo.owner.login, repo.name)
                os.system('git clone https://github.com/%s/%s.git' % (repo.owner.login, repo.name))
            else:
                print('Cloning repo: %s' % (repo.name))
                print 'git clone https://github.com/%s/%s.git' % (repo.owner.login, repo.name)
                os.system('git clone https://github.com/%s/%s.git' % (repo.owner.login, repo.name))
        
        # return to base
        os.chdir('..')
        print
