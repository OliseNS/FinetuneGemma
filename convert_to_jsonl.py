import csv
import json
import random

# Read the CSV dataset
data = []
with open('dataset.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        prompt = row.get('prompt', '').strip()
        completion = row.get('completion', '').strip()
        if prompt and completion:
            data.append((prompt, completion))

# Shuffle and split into training (90%) and validation (10%)
random.seed(42)
random.shuffle(data)
split_idx = int(len(data) * 0.1)
validation = data[:split_idx]
training = data[split_idx:]

# Helper to write JSONL
def write_jsonl(records, filename):
    with open(filename, 'w', encoding='utf-8') as outfile:
        for prompt, completion in records:
            # ensure a space after prompt for GPT finetuning
            obj = {"prompt": prompt + " ", "completion": completion}
            json_line = json.dumps(obj, ensure_ascii=False)
            outfile.write(json_line + '\n')

# Generate files
write_jsonl(training, 'train.jsonl')
write_jsonl(validation, 'validation.jsonl')
