def split_data(input_file, output_1_percent_file, output_99_percent_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()
        total_lines = len(lines)
        split_index = total_lines // 100  # Calculate 1% of total lines

        with open(output_1_percent_file, 'w') as out1, open(output_99_percent_file, 'w') as out99:
            out1.writelines(lines[:split_index])  # Write the first 1% to the 1% file
            out99.writelines(lines[split_index:])  # Write the remaining 99% to the 99% file

# Usage example
input_file = 'ltrc_yahoo/set2.train.txt'
output_1_percent_file = 'set2_1_percent.txt'
output_99_percent_file = 'set2_99_percent.txt'
split_data(input_file, output_1_percent_file, output_99_percent_file)