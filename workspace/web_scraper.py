import os
import re
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlparse, urljoin

class WebScraper:
    def __init__(self, output_dir=None):
        """Initialize the web scraper with an optional output directory."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Set up output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.output_dir = os.path.join(script_dir, "scraper_output")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
    def fetch_page(self, url):
        """Fetch a web page and return its content."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_text(self, html_content):
        """Extract readable text from HTML content."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator=' ')
        
        # Clean up text: remove extra whitespace and normalize
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, html_content, base_url):
        """Extract all links from HTML content."""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # Filter out non-HTTP links, anchors, etc.
            if full_url.startswith(('http://', 'https://')) and '#' not in full_url:
                links.append(full_url)
        
        return links
    
    def extract_metadata(self, html_content):
        """Extract metadata from HTML content."""
        if not html_content:
            return {}
        
        soup = BeautifulSoup(html_content, 'html.parser')
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.text.strip()
        
        # Extract meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and 'content' in desc_tag.attrs:
            metadata['description'] = desc_tag['content'].strip()
        
        # Extract meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and 'content' in keywords_tag.attrs:
            metadata['keywords'] = keywords_tag['content'].strip()
        
        # Extract h1 headings
        h1_tags = soup.find_all('h1')
        if h1_tags:
            metadata['h1_headings'] = [h1.text.strip() for h1 in h1_tags]
        
        return metadata
    
    def analyze_text(self, text):
        """Analyze text content and return statistics."""
        if not text:
            return {}
        
        # Count words
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        unique_words = len(set(words))
        
        # Get most common words (excluding common stop words)
        stop_words = {'the', 'and', 'a', 'to', 'of', 'in', 'is', 'it', 'that', 'for', 
                     'on', 'with', 'as', 'by', 'at', 'from', 'be', 'this', 'an', 'are'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        word_freq = Counter(filtered_words).most_common(20)
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Calculate sentence count (rough approximation)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = sum(1 for s in sentences if s.strip())
        
        return {
            'word_count': word_count,
            'unique_words': unique_words,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'most_common': word_freq
        }
    
    def scrape_url(self, url, depth=0, max_depth=0):
        """Scrape a URL and optionally follow links up to max_depth."""
        print(f"Scraping: {url}")
        
        # Fetch and parse the page
        html_content = self.fetch_page(url)
        if not html_content:
            return None
        
        # Extract text and metadata
        text = self.extract_text(html_content)
        metadata = self.extract_metadata(html_content)
        
        # Analyze the text
        text_analysis = self.analyze_text(text)
        
        # Extract links for potential further scraping
        links = self.extract_links(html_content, url) if depth < max_depth else []
        
        # Create result object
        result = {
            'url': url,
            'metadata': metadata,
            'text_analysis': text_analysis,
            'links': links,
            'text': text[:1000] + '...' if len(text) > 1000 else text  # Truncate text for report
        }
        
        return result
    
    def generate_report(self, results):
        """Generate a text report from scraping results."""
        if not results:
            return "No results to report."
        
        report = "=== Web Scraping Report ===\n\n"
        
        for i, result in enumerate(results, 1):
            report += f"Page {i}: {result['url']}\n"
            
            # Add metadata
            if 'metadata' in result:
                report += "  Metadata:\n"
                for key, value in result['metadata'].items():
                    if isinstance(value, list):
                        report += f"    {key}: {', '.join(value)}\n"
                    else:
                        report += f"    {key}: {value}\n"
            
            # Add text analysis
            if 'text_analysis' in result:
                analysis = result['text_analysis']
                report += "  Content Analysis:\n"
                report += f"    Word count: {analysis['word_count']}\n"
                report += f"    Unique words: {analysis['unique_words']}\n"
                report += f"    Sentence count: {analysis['sentence_count']}\n"
                report += f"    Average word length: {analysis['avg_word_length']:.2f} characters\n"
                
                report += "    Most common words:\n"
                for word, count in analysis['most_common'][:10]:  # Show top 10
                    report += f"      - '{word}': {count} occurrences\n"
            
            # Add a sample of the text
            if 'text' in result:
                sample = result['text'][:500] + '...' if len(result['text']) > 500 else result['text']
                report += "  Text Sample:\n"
                report += f"    {sample}\n"
            
            report += "\n" + "-"*50 + "\n\n"
        
        return report
    
    def save_results(self, results, base_filename="scraping_results"):
        """Save scraping results to files."""
        if not results:
            return None
        
        # Save the report
        report = self.generate_report(results)
        report_path = os.path.join(self.output_dir, f"{base_filename}_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save full text for each page
        for i, result in enumerate(results, 1):
            if 'text' in result:
                domain = urlparse(result['url']).netloc.replace('.', '_')
                text_path = os.path.join(self.output_dir, f"{base_filename}_{domain}_{i}.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
        
        return report_path

def main():
    parser = argparse.ArgumentParser(description='Web scraper and analyzer')
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('--depth', type=int, default=0, help='Depth of links to follow (default: 0)')
    parser.add_argument('--output', help='Output directory for results')
    
    args = parser.parse_args()
    
    scraper = WebScraper(output_dir=args.output)
    
    # Scrape the initial URL
    results = [scraper.scrape_url(args.url)]
    
    # Follow links if depth > 0
    if args.depth > 0:
        links_to_scrape = results[0]['links'][:5]  # Limit to first 5 links
        for link in links_to_scrape:
            result = scraper.scrape_url(link, depth=1, max_depth=args.depth)
            if result:
                results.append(result)
    
    # Save and display results
    report_path = scraper.save_results(results)
    print(f"\nScraping complete! Report saved to: {report_path}")
    
    # Print a summary
    print("\nSummary:")
    print(f"- Pages scraped: {len(results)}")
    total_words = sum(r['text_analysis']['word_count'] for r in results if 'text_analysis' in r)
    print(f"- Total words analyzed: {total_words}")
    print(f"- Output directory: {scraper.output_dir}")

if __name__ == "__main__":
    main()