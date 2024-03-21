import data.configuration as configuration


def create_git_ignore_file(data_dictionary):
    with open(f"{configuration.get_local_git_path()}/.gitignore", "w") as f:
        f.write(
            "DebugConfig\nDebug\nobj\n*uvguix*\n*uvopt*\n.vs\n*.vcxproj*\n*uvproj\n"
        )
        f.write("SharedComponentsSources/\n")
        f.write("BuildVersion.h\n")
        f.write("Version.properties\n")
        f.write("Projects/packages/\n")
        for _, data in data_dictionary.items():
            f.write(f"{data.base_folder}/{data.name}/\n")
