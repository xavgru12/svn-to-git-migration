import os

path = "C:\\localSharedPool"
repostory_names = os.listdir(path)

for repository_name in repostory_names:
    repository_name = repository_name.replace("ag-", "AG - ")
    output = f"{repository_name}-no-externals"
    print(output)
