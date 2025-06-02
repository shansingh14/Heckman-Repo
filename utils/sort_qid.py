def sort_training_data(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    lines.sort(key=lambda x: int(x.split('qid:')[1].split()[0]))
    
    with open(output_file, 'w') as f:
        f.writelines(lines)

# Usage
sort_training_data('train_99_percent.txt', 'sorted_train_99_percent.txt')