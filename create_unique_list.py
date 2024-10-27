list_of_names = [
    "ag-ats",
    "ag-curtis-can-open-cli-wrapper",
    "ag-core",
    "ag-nor-image-creator",
    "ag-curmit",
    "ag-canopen-library",
]

repository_names = []

# breakpoint()
[repository_names.append(item) for item in list_of_names if item not in list_of_names]
print(repository_names)
