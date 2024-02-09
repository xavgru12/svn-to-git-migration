import data.configuration as configuration


def createGitIgnoreFile(data_dictionary):
    with open(f"{configuration.local_path}/.gitignore", "w") as f:
        f.write("DebugConfig\nDebug\nobj\n*uvguix*\n*uvopt*\n.vs\n*.vcxproj*\n*uvproj\n")
        f.write(f"SharedComponentsSources/\n")
        f.write(f"BuildVersion.h\n")
        f.write(f"Version.properties\n")
        f.write(f"Projects/packages/\n")
        for _, data in data_dictionary.items():
            f.write(f"{data.base_folder}/{data.name}/\n")
