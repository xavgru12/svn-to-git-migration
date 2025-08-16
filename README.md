# SVN to Git Migration
This script is built on top of Git's git-svn. The most knowledgable feature is
that it converts externals to submodules.

# Setup
Provide an authors file in ./data/svn-authors.txt.

It has this format: <svn_name> = <git_name> <git_email> 

# Execution

## Following main functionalities  exist:

Checkout SVN externals of the repository.
--checkout-svn


Migrate repositories including externals
--migrate

Upload repositories without externals
--upload-no-externals

Upload repositories subfolders, when an external is linked as subfolder.
--upload-no-externals-subfolders

Create a git repository with git submodules converted from externals

These are the steps which need to be executed subsequentially.

## Options for the script  
url to SVN repostory
--remote-url

select a specific branch
--branch-path

