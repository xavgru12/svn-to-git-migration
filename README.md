# SVN to Git Migration
This script is built on top of Git's git-svn. The most knowledgable feature is
that it converts externals to submodules.

# Setup
Provide an authors file in ./data/svn-authors.txt.

It has this format: <svn_name> = <git_name> <git_email> 

# Execution

## Main Functionalities
For a full migration, the following steps need to be executed subsequentially.


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

These are the steps which need to be executed subsequentially.

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

