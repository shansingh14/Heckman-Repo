import math
import sys


# Define the path to the input and output files
input_file_path = sys.argv[1]
output_file_path_1_percent = 'one_percent_' + input_file_path
output_file_path_99_percent = 'ninety_nine_percent_' + input_file_path
# input_file_path = "set2.train.txt"
# output_file_path = "set2.train1.txt"

# Read the input file and modify the first character of each line
with open(input_file_path, "r") as input_file:
    lines = input_file.readlines()

count_train_1 = math.ceil(len(lines) * .01)
count_train_99 = len(lines) - count_train_1

lines_1_percent = []
for i in range(count_train_1):
    lines_1_percent.append(lines[i])

lines_99_percent = []
for i in range(count_train_1, count_train_99, 1):
    lines_99_percent.append(lines[i])

with open(output_file_path_1_percent, "w") as output_file:
    output_file.writelines(lines_1_percent)

with open(output_file_path_99_percent, "w") as output_file:
    output_file.writelines(lines_99_percent)
