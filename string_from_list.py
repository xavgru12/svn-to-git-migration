import sys
import ast

# Get the list from the command-line arguments
arg = sys.argv[1]

# Convert the string representation of the list back into a Python list
my_list = ast.literal_eval(arg)

# Print the list as a string
print(" ".join(my_list))
