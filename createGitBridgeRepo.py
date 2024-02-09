import os
import sys
import subprocess
import shutil
import errno
import os
from datetime import datetime

def filecreation():
    dir_name = "gitBridgeRepository" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    mydir = os.path.join(
        os.getcwd(), 
        dir_name)
    try:
        os.makedirs(mydir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise  # This was not a "directory exist" error..
    return mydir

def create(directory):

    config_file = sys.argv[1]
    if not os.path.isfile(config_file):
        raise Exception("config file does not exist")
    
    init_process = f"git svn init http://ag-reposerver/repo".split()

    output = subprocess.check_output(init_process, cwd=f"{directory}").decode(sys.stdout.encoding)

    shutil.copy(config_file, os.path.join(directory, ".git"))



    fetch_process = f"git svn fetch -r 514212:HEAD".split()
    output = subprocess.check_output(fetch_process, cwd=f"{directory}", creationflags=subprocess.REALTIME_PRIORITY_CLASS).decode(sys.stdout.encoding)

    print_branches_process = f"git branch -a".split()

    branch_output = subprocess.check_output(print_branches_process, cwd=f"{directory}").decode(sys.stdout.encoding)

    print(f"git branch -a:\n{branch_output}")

directory = filecreation()
create(directory)

