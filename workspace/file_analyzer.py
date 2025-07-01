import os
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

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
            'length_distribution': length_dist,
            'words': words
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
        report += "\n"
    
    return report

def create_visualizations(results, output_dir):
    """Create visualizations for the analysis results."""
    for result in results:
        if 'error' in result:
            continue
            
        file_name = result['file_name']
        base_name = os.path.splitext(file_name)[0]
        
        # Create figure for word frequency
        plt.figure(figsize=(10, 6))
        words, counts = zip(*result['most_common'])
        plt.bar(words, counts)
        plt.title(f'Most Common Words in {file_name}')
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{base_name}_word_freq.png'))
        plt.close()
        
        # Create figure for word length distribution
        if 'length_distribution' in result:
            plt.figure(figsize=(10, 6))
            lengths = sorted(result['length_distribution'].keys())
            counts = [result['length_distribution'][length] for length in lengths]
            plt.bar(lengths, counts)
            plt.title(f'Word Length Distribution in {file_name}')
            plt.xlabel('Word Length')
            plt.ylabel('Count')
            plt.xticks(lengths)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'{base_name}_length_dist.png'))
            plt.close()
            
    # Create comparison chart if there are multiple files
    if len(results) > 1:
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            plt.figure(figsize=(10, 6))
            file_names = [r['file_name'] for r in valid_results]
            word_counts = [r['word_count'] for r in valid_results]
            unique_counts = [r['unique_words'] for r in valid_results]
            
            x = np.arange(len(file_names))
            width = 0.35
            
            plt.bar(x - width/2, word_counts, width, label='Total Words')
            plt.bar(x + width/2, unique_counts, width, label='Unique Words')
            
            plt.xlabel('Files')
            plt.ylabel('Word Count')
            plt.title('Word Count Comparison')
            plt.xticks(x, file_names, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'word_count_comparison.png'))
            plt.close()

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create output directory for visualizations
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
    
    # Create visualizations
    try:
        print("Generating visualizations...")
        create_visualizations(results, output_dir)
        print(f"Visualizations saved to {output_dir}")
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        
    print("\nAnalysis complete! The following files were created:")
    print(f"- Text report: {report_path}")
    print(f"- Visualizations: {output_dir}/*.png")

if __name__ == "__main__":
    main()