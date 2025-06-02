def binarize_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            parts = line.split()
            trueR = float(parts[0])
            # Binarize trueR based on the given condition
            if trueR in [1, 2]:
                trueR = 0
            elif trueR in [3, 4]:
                trueR = 1
            # Write the modified line to the output file
            parts[0] = str(int(trueR))
            outfile.write(' '.join(parts) + '\n')
# Usage example
input_file = 'set2.sampled.txt'
output_file = 'set2.train_sampled.binary.txt'
binarize_file(input_file, output_file)