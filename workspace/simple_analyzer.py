import os
import re
from collections import Counter

def analyze_text_file(file_path):
    """Analyze a text file and return word statistics."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Count words
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = len(words)
        unique_words = len(set(words))
        
        # Get most common words
        word_freq = Counter(words).most_common(10)
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Calculate word length distribution
        word_lengths = [len(word) for word in words]
        length_dist = Counter(word_lengths)
        
        return {
            'file_name': os.path.basename(file_path),
            'word_count': word_count,
            'unique_words': unique_words,
            'most_common': word_freq,
            'avg_word_length': avg_word_length,
            'length_distribution': length_dist
        }
    except Exception as e:
        return {
            'file_name': os.path.basename(file_path),
            'error': str(e)
        }

def find_text_files(directory):
    """Find all text files in the given directory."""
    text_files = []
    for file in os.listdir(directory):
        if file.endswith('.txt') or file.endswith('.md'):
            text_files.append(os.path.join(directory, file))
    return text_files

def generate_report(results):
    """Generate a text report from the analysis results."""
    report = "=== Text File Analysis Report ===\n\n"
    
    for result in results:
        report += f"File: {result['file_name']}\n"
        if 'error' in result:
            report += f"  Error: {result['error']}\n"
        else:
            report += f"  Word count: {result['word_count']}\n"
            report += f"  Unique words: {result['unique_words']}\n"
            report += f"  Average word length: {result['avg_word_length']:.2f} characters\n"
            report += "  Most common words:\n"
            for word, count in result['most_common']:
                report += f"    - '{word}': {count} occurrences\n"
            
            # Add word length distribution as ASCII chart
            if 'length_distribution' in result:
                report += "  Word length distribution:\n"
                max_count = max(result['length_distribution'].values()) if result['length_distribution'] else 0
                if max_count > 0:
                    for length in sorted(result['length_distribution'].keys()):
                        count = result['length_distribution'][length]
                        bar_length = int((count / max_count) * 40)
                        bar = '#' * bar_length
                        report += f"    {length:2d} chars: {bar} ({count})\n"
        report += "\n"
    
    # Add comparison section if multiple files
    if len(results) > 1:
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            report += "=== File Comparison ===\n\n"
            report += "Word counts:\n"
            for r in valid_results:
                report += f"  {r['file_name']}: {r['word_count']} total, {r['unique_words']} unique\n"
            
            # Find common words across all files
            common_words = set()
            for i, r in enumerate(valid_results):
                words = set(word for word, _ in r['most_common'])
                if i == 0:
                    common_words = words
                else:
                    common_words &= words
            
            if common_words:
                report += "\nCommon popular words across all files:\n"
                for word in common_words:
                    report += f"  - {word}\n"
            
    return report

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create output directory
    output_dir = os.path.join(current_dir, "analysis_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Find text files
    text_files = find_text_files(current_dir)
    
    if not text_files:
        print("No text files found in the workspace directory.")
        return
    
    # Analyze each file
    results = []
    for file_path in text_files:
        print(f"Analyzing {os.path.basename(file_path)}...")
        result = analyze_text_file(file_path)
        results.append(result)
    
    # Generate and print report
    report = generate_report(results)
    print("\n" + report)
    
    # Save report to file
    report_path = os.path.join(output_dir, "text_analysis_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report saved to {report_path}")
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()