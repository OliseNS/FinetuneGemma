import csv
import json
import random
from typing import List, Dict

def convert_to_gemma_format(csv_file: str, output_file: str):
    """
    Convert CSV data to Gemma 2B compatible format using Alpaca instruction template.
    
    Args:
        csv_file: Path to input CSV file
        output_file: Path to output JSONL file
    """
    
    # Read the CSV dataset
    data = []
    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prompt = row.get('prompt', '').strip()
            completion = row.get('completion', '').strip()
            age_group = row.get('age_group', '').strip()
            audience_type = row.get('audience_type', '').strip()
            tags = row.get('tags', '').strip()
            
            if prompt and completion:
                # Create instruction-input-output format for Gemma 2B
                # For healthcare data, we'll use the prompt as instruction
                # and add context about the audience and age group as input
                
                # Build contextual input
                context_parts = []
                if age_group:
                    context_parts.append(f"Age group: {age_group}")
                if audience_type:
                    context_parts.append(f"Audience: {audience_type}")
                if tags:
                    context_parts.append(f"Topic areas: {tags}")
                
                context_input = ". ".join(context_parts) if context_parts else ""
                
                # Format for Alpaca template
                data_point = {
                    "instruction": prompt,
                    "input": context_input,
                    "output": completion                }
                
                data.append(data_point)
    
    print(f"Loaded {len(data)} data points from CSV")
    
    # Shuffle all data
    random.seed(42)
    random.shuffle(data)
    
    print(f"Total data points: {len(data)} examples")
    
    # Write all data to single training file
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Training data saved to: {output_file}")
    
    # Show sample formatted data
    print("\n=== Sample Training Example ===")
    sample = data[0]
    print(f"Instruction: {sample['instruction'][:100]}...")
    print(f"Input: {sample['input']}")
    print(f"Output: {sample['output'][:100]}...")

def create_gemma_prompt_preview(data_point: Dict[str, str]) -> str:
    """
    Preview how the data will look in the Alpaca template format
    """
    alpaca_template = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""
    
    return alpaca_template.format(
        instruction=data_point["instruction"],
        input=data_point["input"],
        output=data_point["output"]
    )

if __name__ == "__main__":
    # Convert the dataset
    convert_to_gemma_format(
        csv_file="data/dataset.csv",
        output_file="train.jsonl"
    )
    
    # Load a sample to show the formatted prompt
    with open("train.jsonl", 'r', encoding='utf-8') as f:
        first_line = f.readline()
        sample_data = json.loads(first_line)
    
    print("\n=== Full Alpaca Template Preview ===")
    print(create_gemma_prompt_preview(sample_data))
