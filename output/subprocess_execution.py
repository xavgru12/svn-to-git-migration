import subprocess

def continuous_execute(command, external_source_path, std):
    std_types = ["stderr", "stdout"]
    if std not in std_types:
        raise ValueError(f"std is not recognized. Valid values are: {std_types}")
    
    if not isinstance(command, list):
        command = command.split()

    stderr_pipe = None
    stdout_pipe = None

    if std == "stdout":
        stdout_pipe = subprocess.PIPE
    elif std == "stderr":
        stderr_pipe = subprocess.PIPE

    popen = subprocess.Popen(
        command,
        stderr=stderr_pipe,
        stdout=stdout_pipe,
        cwd=external_source_path,
        creationflags=subprocess.REALTIME_PRIORITY_CLASS,
        universal_newlines=True,
    )

    if std == "stdout":
        popen_std = popen.stdout
    elif std == "stderr":
        popen_std = popen.stderr

    for line in iter(popen_std.readline, ""):
        if line.strip() and line is not None:
            yield line
    popen_std.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(
            return_code,
            f"{command} at {external_source_path} failed.",
        )