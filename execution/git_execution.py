import execution.subprocess_execution


def add_remote_origin(repo_name, repo_path):
    url = f"git@bitbucket.org:curtisinst/{repo_name}.git"
    command = f"git remote add origin {url}"

    execution.subprocess_execution.check_output_execute(command, repo_path)


def check_remote_origin_exists(repo_path):
    checker_command = "git ls-remote origin"
    try:
        execution.subprocess_execution.check_output_execute(checker_command, repo_path)
    except:
        return False
    
    return True


def add_remote_upload(repo_name, repo_path):
    url = f"git@bitbucket.org:curtisinst/{repo_name}.git"
    command = f"git remote add upload {url}"

    execution.subprocess_execution.check_output_execute(command, repo_path)


def check_remote_upload_exists(repo_path):
    checker_command = "git ls-remote upload"
    try:
        execution.subprocess_execution.check_output_execute(checker_command, repo_path)
    except:
        return False

    return True


def remove_remote_origin(repo_path):
    command = "git remote remove origin"

    execution.subprocess_execution.check_output_execute(command, repo_path)


def fetch(repo_path):
    fetch_command = "git fetch"
    execution.subprocess_execution.check_output_execute(fetch_command, repo_path)


def push_local_git_tags(repo_path):
    command = "git push origin --tags --force"
    execution.subprocess_execution.check_output_execute(command, repo_path)

def add_missing_remote_to_file(name):
    file_path = "remotes.txt"

    with open(file_path, "a") as file:
        file.write(f"{name}\n")
