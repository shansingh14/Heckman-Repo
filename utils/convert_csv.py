import pandas as pd

def convert_to_csv(input_file, output_file):
    rows = []
    with open(input_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            label = parts[0]
            qid = parts[1].split(":")[1]
            features = {}
            features['C'] = int(label)
            features['qid'] = int(qid)
            for feature in parts[2:]:
                index, value = feature.split(":")
                features[f'X{index}'] = float(value)
            rows.append(features)
    
    # Convert list of dictionaries to DataFrame, filling missing features with 0
    df = pd.DataFrame(rows).fillna(0)
    df.to_csv(output_file, index=False)

# Run the function
convert_to_csv('ltrc_yahoo/set2.train.txt', 'set2_full.csv')
