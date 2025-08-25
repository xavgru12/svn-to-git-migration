# SVN to Git Migration
This script is built on top of Git's git-svn. The most knowledgable feature is
that it converts externals to submodules inlcuding handling SVN subfolder checkouts.

# Setup

## Authors File
Provide an authors file in ./data/svn-authors.txt.

This file is used from the scripts by default.

It has this format: <svn_name> = <git_name> <git_email> 

## Branch Configuration
SVN provides no way of detecting branches. Each branch is treated as a directory with
 no differentiation between branches and directories/subdirectories.
In Git branches are not part of directories and can be especially identified.
In order to detect and map SVN branches to Git a configuration
file is established.

It is differentiated between trunk, branches and tags.
Directories without a branch, as well as subdirectories to be treated as branches can be configured, too.
A thorough example(which is used from the scripts by default) can be found at: ./data/branchConfiguration.json


# Execution

## Main Functionalities
For a full migration, the following steps need to be executed subsequentially.

The main Python script to be invoked is:

svnExternals.py

Checkout SVN externals of the repository
```
--checkout-svn
```

Migrate repositories including externals
```
--migrate
```

Upload repositories without externals
```
--upload-no-externals
```

Upload repositories subfolders, when an external is linked as subfolder.
```
--upload-no-externals-subfolders
```

Create a Git repository with Git submodules converted from externals
```
--checkout-git
```

## Important Options for the Script  
url to SVN repostory
```
--remote-url
```

select a specific branch
```
--branch-path
```

local path where git-svn repositories will be generated
```
--migration-output-path
```

reset git-svn repositories and fetch from backup path
```
--reset-migration-output-path
```

for each git-svn repository, fetch latest SVN state and publish to backup path
```
--fetch-and-publish-all
```

