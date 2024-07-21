import shutil
import os
import stat
import re
import pdb

import subprocess_execution

def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

def copy_repo_to_working_directory(repo_path):
    name = os.path.basename(repo_path)
    destination = r"C:\bitbucketWorkspace\gitNoExternals"
    destination_repo_path = os.path.join(destination, name)
    os.makedirs(destination, exist_ok=True)

    if os.path.isdir(destination_repo_path):
        shutil.rmtree( destination_repo_path, onerror = on_rm_error )
    shutil.copytree(repo_path, destination_repo_path)

    destination_path = os.path.join(destination, name)
    return destination_path

def transform_git_bridge_to_native_git(repo_path):
    git_bridge_folder = os.path.join(repo_path, ".git", "svn")
    if not os.path.exists(git_bridge_folder):
        raise FileNotFoundError(f'directory is not a git bridge repository: "{git_bridge_folder}"')

    add_remote_origin(repo_path)
    transform_branches(repo_path)
    transform_tags(repo_path)

def add_remote_origin(repo_path):
    base_name = os.path.basename(repo_path)
    repo_name = f"{base_name}-no-externals"
    url = f"git@bitbucket.org:curtisinst/{repo_name}.git"
    command = f"git remote add origin {url}"

    subprocess_execution.check_output_execute(command, repo_path)

def remove_remote_origin(repo_path):
    command = "git remote remove origin"

    subprocess_execution.check_output_execute(command, repo_path)

def transform_branches(repo_path):
    
    command_list = ["git", "for-each-ref", "--format=%(refname:short)"]
    for line in subprocess_execution.continuous_execute(command_list, repo_path, "stdout"):
        if "@" not in line:
            line = line.replace("\n", "")
            print(line)
            branch_pattern = "origin.*branches/"
            transform_line_as_branch(line, branch_pattern, repo_path)

            trunk_pattern = "origin.*trunk"
            transform_line_as_branch(line, trunk_pattern, repo_path)

            if "ag-curmit" in repo_path:
                tag_pattern = "origin.*distr/"
                transform_line_as_branch(line, tag_pattern, repo_path)
            print()
    #git push origin all found branches

def transform_line_as_branch(line, pattern, repo_path):
    found_pattern = find(pattern, line)
    if found_pattern is not None:
        remote_part = line.replace(found_pattern, "")
        if "trunk" in found_pattern:
            remote_part= "main"
        command = f"git push origin refs/remotes/{line}:refs/heads/{remote_part}"
        print(command)
        subprocess_execution.check_output_execute(command, repo_path)


def find(pattern, line):
    match = re.match(pattern, line)
    if match:
        return match.group()


def transform_tags(repo_path):
    #distr in ag-curmit must be treated as branch, do not make git tags for it
    if "ag-curmit" in repo_path:
        return
    command_list = ["git", "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/remotes/origin/distr/*"]
    for line in subprocess_execution.continuous_execute(command_list, repo_path, "stdout"):
        splitted_line = line.split()
        branch_name = splitted_line[0]
        commit_hash = splitted_line[1]
        print(branch_name)
        print(commit_hash)

    #write output of execution to a log file since this will be a very long file


# git for-each-ref --format="%(refname:short) %(objectname)" refs/remotes/origin/tags \
# | while read BRANCH REF
#   do
#         TAG_NAME=${BRANCH#*/}
#         BODY="$(git log -1 --format=format:%B $REF)"

#         echo "ref=$REF parent=$(git rev-parse $REF^) tagname=$TAG_NAME body=$BODY" >&2

#         git tag -a -m "$BODY" $TAG_NAME $REF^  &&\
#         git branch -r -d $BRANCH
#   done

if __name__ == "__main__":
    git_bridge_path = r"C:\localSharedPool\ag-curmit"
    working_directory = copy_repo_to_working_directory(git_bridge_path)
    print(f"working directory: {working_directory}")
    transform_git_bridge_to_native_git(working_directory)
