import subprocess
import sys

output_subprocess = subprocess.check_output(
    ["git", "svn", "fetch", "--quiet", "--quiet"],
    creationflags=subprocess.REALTIME_PRIORITY_CLASS,
).decode(sys.stdout.encoding)
