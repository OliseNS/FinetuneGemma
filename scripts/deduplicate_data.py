"""
Medical Training Data Deduplication - High Quality Preservation
This version is designed specifically for medical training data and preserves important medical distinctions.
"""

import json
import os
from typing import List, Dict, Set, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict
import hashlib
import argparse
from datetime import datetime
import re


def load_jsonl(file_path: str) -> List[Dict]:
    """Load data from a JSONL file."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON on line {line_num}: {e}")
                        continue
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    
    return data


def save_jsonl(data: List[Dict], file_path: str) -> None:
    """Save data to a JSONL file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def save_removal_report(removed_items: List[Dict], report_path: str) -> None:
    """Save a detailed report of removed items."""
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Training Data Removal Report\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Group by removal reason
        by_reason = defaultdict(list)
        for item in removed_items:
            by_reason[item['removal_reason']].append(item)
        
        f.write(f"## Summary\n")
        f.write(f"Total items removed: {len(removed_items)}\n\n")
        
        for reason, items in by_reason.items():
            f.write(f"- {reason}: {len(items)} items\n")
        f.write("\n")
        
        # Detailed breakdown by category
        for reason, items in by_reason.items():
            f.write(f"## {reason.title()} ({len(items)} items)\n\n")
            
            for i, item in enumerate(items, 1):
                f.write(f"### Item {i}\n")
                f.write(f"**Original Index:** {item['original_index']}\n\n")
                
                if 'similar_to' in item:
                    f.write(f"**Similar to Index:** {item['similar_to']}\n")
                    f.write(f"**Similarity Score:** {item['similarity_score']:.3f}\n")
                    f.write(f"**Instruction Similarity:** {item['instruction_similarity']:.3f}\n\n")
                
                f.write(f"**Instruction:** {item['data']['instruction']}\n\n")
                
                if item['data'].get('input', '').strip():
                    f.write(f"**Input:** {item['data']['input']}\n\n")
                
                f.write(f"**Output:** {item['data']['output']}\n\n")
                
                if 'similar_to_data' in item:
                    f.write("**Kept Instead (Similar Item):**\n")
                    f.write(f"- Instruction: {item['similar_to_data']['instruction']}\n")
                    if item['similar_to_data'].get('input', '').strip():
                        f.write(f"- Input: {item['similar_to_data']['input']}\n")
                    f.write(f"- Output: {item['similar_to_data']['output'][:150]}{'...' if len(item['similar_to_data']['output']) > 150 else ''}\n\n")
                    
                    if 'quality_score' in item and 'kept_quality_score' in item:
                        f.write(f"**Quality Comparison:**\n")
                        f.write(f"- Removed item quality score: {item['quality_score']:.1f}\n")
                        f.write(f"- Kept item quality score: {item['kept_quality_score']:.1f}\n\n")
                
                f.write("---\n\n")
    
    print(f"Detailed removal report saved to: {report_path}")


def get_content_hash(item: Dict) -> str:
    """Generate a hash for the content of an item."""
    content = ""
    if 'instruction' in item:
        content += item['instruction'].strip().lower()
    if 'input' in item:
        content += item['input'].strip().lower()
    if 'output' in item:
        content += item['output'].strip().lower()
    
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def get_similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity score between two texts using SequenceMatcher."""
    return SequenceMatcher(None, text1.lower().strip(), text2.lower().strip()).ratio()


def extract_medical_terms(text: str) -> Set[str]:
    """Extract medical terms and treatment types from text."""
    medical_terms = set()
    
    patterns = [
        r'\b(hemodialysis|peritoneal dialysis|crrt|apd|capd|hd|pd)\b',
        r'\b(kidney|renal|dialysis|transplant|nephrology)\b',
        r'\b(peritonitis|pneumonia|infection|fever|cramps|vomiting)\b',
        r'\b(catheter|access|fistula|graft)\b',
        r'\b(fluid|electrolyte|sodium|potassium|calcium)\b',
        r'\b(pediatric|adult|elderly|young_adult|middle_aged|older_adult)\b',
        r'\b(layperson|expert|nurse|doctor|physician)\b'
    ]
    
    text_lower = text.lower()
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        medical_terms.update(matches)
    
    return medical_terms


def are_medically_distinct(item1: Dict, item2: Dict) -> bool:
    """Determine if two items are medically distinct and should not be considered duplicates."""
    text1 = f"{item1.get('instruction', '')} {item1.get('input', '')} {item1.get('output', '')}"
    text2 = f"{item2.get('instruction', '')} {item2.get('input', '')} {item2.get('output', '')}"
    
    terms1 = extract_medical_terms(text1)
    terms2 = extract_medical_terms(text2)
    
    # Different treatment modalities are medically distinct
    treatment_modalities = {'hemodialysis', 'peritoneal dialysis', 'crrt', 'apd', 'capd', 'hd', 'pd'}
    treatment1 = terms1.intersection(treatment_modalities)
    treatment2 = terms2.intersection(treatment_modalities)
    
    if treatment1 and treatment2 and treatment1 != treatment2:
        return True
    
    # Different medical conditions are distinct
    conditions = {'peritonitis', 'pneumonia', 'infection', 'fever', 'cramps', 'vomiting'}
    condition1 = terms1.intersection(conditions)
    condition2 = terms2.intersection(conditions)
    
    if condition1 and condition2 and condition1 != condition2:
        return True
    
    # Different age groups or audiences might need different approaches
    age_groups = {'pediatric', 'adult', 'elderly', 'young_adult', 'middle_aged', 'older_adult'}
    age1 = terms1.intersection(age_groups)
    age2 = terms2.intersection(age_groups)
    
    audiences = {'layperson', 'expert', 'nurse', 'doctor', 'physician'}
    audience1 = terms1.intersection(audiences)
    audience2 = terms2.intersection(audiences)
    
    # If different age groups AND different audiences, consider distinct
    if age1 and age2 and age1 != age2 and audience1 and audience2 and audience1 != audience2:
        return True
    
    return False


def is_low_quality(item: Dict) -> Tuple[bool, str]:
    """Check if an item is low quality and should be removed."""
    instruction = item.get('instruction', '').strip()
    input_text = item.get('input', '').strip()
    output = item.get('output', '').strip()
    
    # Check for minimum content requirements
    if len(instruction) < 10:
        return True, "instruction_too_short"
    
    if len(output) < 15:
        return True, "output_too_short"
    
    # Check for clearly inappropriate content
    inappropriate_patterns = [
        r'\bhack\b.*\bemail\b',
        r'\bhitler\b',
        r'\bnazi\b',
        r'\bkill\b.*\bpeople\b',
        r'\bhow to.*\bmurder\b'
    ]
    
    full_text = f"{instruction} {input_text} {output}".lower()
    for pattern in inappropriate_patterns:
        if re.search(pattern, full_text):
            return True, "inappropriate_content"
    
    # Check for overly generic refusal responses (but be conservative)
    refusal_phrases = ["sorry, i can't assist with that", "i cannot assist", "i'm not able to"]
    output_lower = output.lower()
    
    # Only flag as low quality if it's ONLY a refusal with no medical context
    if any(phrase in output_lower for phrase in refusal_phrases):
        if len(output) < 50 and not extract_medical_terms(full_text):
            return True, "generic_refusal"
    
    # Check for test/dummy content
    if instruction.lower().startswith(("test", "example", "sample", "dummy")):
        return True, "test_content"
    
    return False, ""


def calculate_quality_score(item: Dict) -> float:
    """Calculate a quality score for an item, focusing on medical relevance and completeness."""
    output = item.get('output', '')
    instruction = item.get('instruction', '')
    input_text = item.get('input', '')
    
    score = 0.0
    
    # Base score from length (but not the primary factor)
    score += min(len(output) * 0.1, 50)  # Max 50 points for length
    
    # Medical term density (important for medical dataset)
    full_text = f"{instruction} {input_text} {output}"
    medical_terms = extract_medical_terms(full_text)
    score += len(medical_terms) * 10  # 10 points per medical term
    
    # Sentence structure (indicates coherent response)
    sentences = output.count('.') + output.count('!') + output.count('?')
    score += sentences * 5
    
    # Specificity indicators
    specific_words = len([w for w in output.split() if len(w) > 6])
    score += specific_words * 0.5
    
    # Completeness (no truncation)
    if not output.endswith('...'):
        score += 20
    
    # Penalize very short responses
    if len(output) < 50:
        score *= 0.5
    
    return score


def find_high_quality_duplicates(data: List[Dict], similarity_threshold: float = 0.80) -> Tuple[Set[int], List[Dict]]:
    """Find only true duplicates and very low quality items. Conservative approach."""
    indices_to_remove = set()
    removal_details = []
    
    print("Checking for low-quality items...")
    low_quality_count = 0
    for i, item in enumerate(data):
        is_low_qual, reason = is_low_quality(item)
        if is_low_qual:
            indices_to_remove.add(i)
            low_quality_count += 1
            
            removal_details.append({
                'original_index': i,
                'removal_reason': f'low_quality_{reason}',
                'data': item,
                'quality_issue': reason
            })
            
            if low_quality_count <= 10:  # Show first 10 examples
                print(f"  Removing item {i}: {reason} - '{item['instruction'][:60]}...'")
    
    print(f"Found {low_quality_count} low-quality items")
    
    print("Checking for exact duplicates...")
    exact_duplicates = defaultdict(list)
    
    # Find exact duplicates using content hashes
    for i, item in enumerate(data):
        if i in indices_to_remove:
            continue
        content_hash = get_content_hash(item)
        exact_duplicates[content_hash].append(i)
    
    # Mark duplicate indices for removal (keep the first occurrence)
    for content_hash, indices in exact_duplicates.items():
        if len(indices) > 1:
            print(f"Found {len(indices)} exact duplicates: {indices}")
            # Remove all but the first occurrence
            for idx in indices[1:]:
                indices_to_remove.add(idx)
                removal_details.append({
                    'original_index': idx,
                    'removal_reason': 'exact_duplicate',
                    'data': data[idx],
                    'duplicate_of': indices[0],
                    'duplicate_of_data': data[indices[0]]
                })
    
    print(f"Checking for very similar items (similarity threshold: {similarity_threshold})...")
    
    # Only catch extremely similar items that are not medically distinct
    similar_found = 0
    processed_pairs = set()
    
    for i in range(len(data)):
        if i in indices_to_remove:
            continue
            
        for j in range(i + 1, len(data)):
            if j in indices_to_remove:
                continue
                
            # Skip if we've already processed this pair
            pair = tuple(sorted([i, j]))
            if pair in processed_pairs:
                continue
            processed_pairs.add(pair)
            
            # Check if medically distinct first
            if are_medically_distinct(data[i], data[j]):
                continue
              # Calculate similarities
            full_text_i = f"{data[i].get('instruction', '')} {data[i].get('input', '')} {data[i].get('output', '')}"
            full_text_j = f"{data[j].get('instruction', '')} {data[j].get('input', '')} {data[j].get('output', '')}"
            
            overall_similarity = get_similarity_score(full_text_i, full_text_j)
            instruction_similarity = get_similarity_score(
                data[i].get('instruction', ''), 
                data[j].get('instruction', '')
            )
            
            # Very high threshold for removal
            if overall_similarity >= similarity_threshold and instruction_similarity >= 0.70:
                similar_found += 1
                
                if similar_found <= 5:  # Show first 5 similar pairs
                    print(f"Found very similar items (overall: {overall_similarity:.3f}, instruction: {instruction_similarity:.3f}):")
                    print(f"  Item {i}: {data[i]['instruction'][:60]}...")
                    print(f"  Item {j}: {data[j]['instruction'][:60]}...")
                
                # Calculate quality scores to decide which to keep
                score_i = calculate_quality_score(data[i])
                score_j = calculate_quality_score(data[j])
                
                # Remove the lower quality item
                if score_i >= score_j:
                    indices_to_remove.add(j)
                    removal_details.append({
                        'original_index': j,
                        'removal_reason': 'very_similar_item',
                        'data': data[j],
                        'similar_to': i,
                        'similar_to_data': data[i],
                        'similarity_score': overall_similarity,
                        'instruction_similarity': instruction_similarity,
                        'quality_score': score_j,
                        'kept_quality_score': score_i
                    })
                    if similar_found <= 5:
                        print(f"  Keeping item {i} (quality: {score_i:.1f} vs {score_j:.1f})")
                else:
                    indices_to_remove.add(i)
                    removal_details.append({
                        'original_index': i,
                        'removal_reason': 'very_similar_item',
                        'data': data[i],
                        'similar_to': j,
                        'similar_to_data': data[j],
                        'similarity_score': overall_similarity,
                        'instruction_similarity': instruction_similarity,
                        'quality_score': score_i,
                        'kept_quality_score': score_j
                    })
                    if similar_found <= 5:
                        print(f"  Keeping item {j} (quality: {score_j:.1f} vs {score_i:.1f})")
                
                if similar_found <= 5:
                    print()
    
    if similar_found > 5:
        print(f"... and {similar_found - 5} more very similar pairs found")
    
    return indices_to_remove, removal_details


def analyze_dataset(data: List[Dict]) -> None:
    """Analyze the dataset and print statistics."""
    print(f"Total items: {len(data)}")
    
    # Count items by type
    instruction_only = sum(1 for item in data if item.get('input', '').strip() == '')
    with_input = len(data) - instruction_only
    
    print(f"Items with instruction only: {instruction_only}")
    print(f"Items with instruction + input: {with_input}")
    
    # Average lengths
    avg_instruction_len = sum(len(item.get('instruction', '')) for item in data) / len(data)
    avg_input_len = sum(len(item.get('input', '')) for item in data) / len(data)
    avg_output_len = sum(len(item.get('output', '')) for item in data) / len(data)
    
    print(f"Average instruction length: {avg_instruction_len:.1f} characters")
    print(f"Average input length: {avg_input_len:.1f} characters")
    print(f"Average output length: {avg_output_len:.1f} characters")
    
    # Medical content analysis
    medical_items = 0
    total_medical_terms = 0
    for item in data:
        full_text = f"{item.get('instruction', '')} {item.get('input', '')} {item.get('output', '')}"
        terms = extract_medical_terms(full_text)
        if terms:
            medical_items += 1
            total_medical_terms += len(terms)
    
    print(f"Items with medical content: {medical_items} ({medical_items/len(data)*100:.1f}%)")
    if medical_items > 0:
        print(f"Average medical terms per medical item: {total_medical_terms/medical_items:.1f}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Medical training data deduplication - high quality preservation')
    parser.add_argument('--input', default='../data/train.jsonl', help='Input JSONL file path')
    parser.add_argument('--output', default='../data/train_unique.jsonl', help='Output JSONL file path')     
    parser.add_argument('--report', default='../reports/removal_report.md', help='Detailed removal report path')
    parser.add_argument('--similarity-threshold', type=float, default=0.50, 
                       help='Similarity threshold for detecting near-duplicates (0.0 to 1.0, default: 0.50)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed without actually removing')
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, args.input)
    output_path = os.path.join(script_dir, args.output)
    report_path = os.path.join(script_dir, args.report)
    
    print("=== Medical Training Data Deduplication - High Quality Mode ===")
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")
    print(f"Report file: {report_path}")
    print(f"Similarity threshold: {args.similarity_threshold} (very conservative)")
    print()
    
    # Load data
    print("Loading data...")
    data = load_jsonl(input_path)
    
    if not data:
        print("No data loaded. Exiting.")
        return
    
    print("=== Original Dataset Analysis ===")
    analyze_dataset(data)
    
    # Find duplicates and very low quality items
    print("=== Conservative Quality Control & Duplicate Detection ===")
    indices_to_remove, removal_details = find_high_quality_duplicates(data, args.similarity_threshold)
    
    # Report findings
    total_removed = len(indices_to_remove)
    
    print(f"=== Summary ===")
    print(f"Total items to remove: {total_removed}")
    print(f"Remaining items: {len(data) - total_removed}")
    print(f"Retention rate: {((len(data) - total_removed) / len(data) * 100):.1f}%")
    print()
    
    if args.dry_run:
        print("DRY RUN: No files were modified.")
        if removal_details:
            save_removal_report(removal_details, report_path)
        return
    
    if indices_to_remove:
        # Create cleaned dataset
        print("Creating cleaned dataset...")
        cleaned_data = [item for i, item in enumerate(data) if i not in indices_to_remove]
        
        # Save cleaned data
        save_jsonl(cleaned_data, output_path)
        print(f"Cleaned dataset saved to: {output_path}")
        
        # Save detailed removal report
        save_removal_report(removal_details, report_path)
        
        print("=== Cleaned Dataset Analysis ===")
        analyze_dataset(cleaned_data)
    else:
        print("No duplicates or low-quality items found. No cleaning needed.")
        # Still create the output file as a copy
        save_jsonl(data, output_path)
        print(f"Original dataset copied to: {output_path}")


if __name__ == "__main__":
    main()
