import shutil
import os
import stat

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
    transform_branches()
    transform_tags()

def transform_branches():
    pass

def transform_tags():
    pass

if __name__ == "__main__":
    git_bridge_path = r"C:\localSharedPool\ag-curmit"
    working_directory = copy_repo_to_working_directory(git_bridge_path)
    print(f"working directory: {working_directory}")
    transform_git_bridge_to_native_git(working_directory)