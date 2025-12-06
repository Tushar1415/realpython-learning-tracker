"""Script to analyze the structure of an exercise page to understand duration extraction"""
from pathlib import Path
import requests
from bs4 import BeautifulSoup

def fetch_and_analyze(url):
    """Fetch the page and analyze its structure"""
    print("=" * 60)
    print(f"Fetching: {url}")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save HTML for inspection
        # Get project root (parent of scripts directory)
        PROJECT_ROOT = Path(__file__).parent.parent
        html_file = PROJECT_ROOT / 'analysis' / 'exercise_page_analysis.html'
        html_file.parent.mkdir(exist_ok=True)
        html_file.write_text(soup.prettify(), encoding='utf-8')
        print(f"✓ Saved HTML to: {html_file}")
        
        # Analyze duration elements
        print("\n" + "=" * 60)
        print("ANALYZING DURATION ELEMENTS")
        print("=" * 60)
        
        # Look for the main duration (top-level)
        print("\n1. TOP-LEVEL DURATION:")
        main_duration = soup.find('p', class_=lambda x: x and 'text-muted' in x and 'mt-1' in x)
        if main_duration:
            print(f"   Found: {main_duration.get_text(strip=True)}")
            print(f"   HTML: {str(main_duration)[:200]}")
        else:
            print("   Not found")
        
        # Look for all duration-related elements
        print("\n2. ALL ELEMENTS WITH 'text-muted mt-1' CLASS:")
        all_durations = soup.find_all('p', class_=lambda x: x and 'text-muted' in x and 'mt-1' in x)
        print(f"   Found {len(all_durations)} elements")
        for i, elem in enumerate(all_durations, 1):
            text = elem.get_text(strip=True)
            print(f"   {i}. {text}")
            # Check if it contains duration info
            if any(word in text.lower() for word in ['lesson', 'min', 'hour', 'h', 'm']):
                print(f"      ✓ Contains duration info")
        
        # Look for section durations
        print("\n3. LOOKING FOR SECTIONS WITH DURATIONS:")
        # Common patterns for sections
        sections = soup.find_all(['section', 'div'], class_=lambda x: x and ('section' in str(x).lower() or 'chapter' in str(x).lower() or 'part' in str(x).lower()))
        print(f"   Found {len(sections)} potential sections")
        
        # Look for h2/h3 headings that might indicate sections
        print("\n4. LOOKING FOR SECTION HEADINGS:")
        headings = soup.find_all(['h2', 'h3', 'h4'])
        section_headings = []
        for heading in headings:
            text = heading.get_text(strip=True)
            # Look for headings that might be section titles
            if text and len(text) < 100:  # Reasonable section title length
                section_headings.append((heading.name, text))
        
        print(f"   Found {len(section_headings)} headings")
        for tag, text in section_headings[:10]:  # Show first 10
            print(f"   <{tag}> {text}")
        
        # Look for duration patterns in the page structure
        print("\n5. SEARCHING FOR DURATION PATTERNS IN PAGE STRUCTURE:")
        # Look for elements that might contain "X Lessons Y min" pattern
        import re
        all_text = soup.get_text()
        duration_patterns = re.findall(r'(\d+\s*Lessons?\s*\d+[hm]|\d+\s*Lessons?\s*\d+\s*(?:hour|hr|h)\s*\d+\s*(?:min|m))', all_text, re.IGNORECASE)
        if duration_patterns:
            print(f"   Found {len(duration_patterns)} duration patterns:")
            for pattern in duration_patterns[:10]:
                print(f"   - {pattern}")
        
        # Look for specific structure - sections with their own durations
        print("\n6. ANALYZING PAGE STRUCTURE FOR SECTIONS:")
        # Try to find the main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and 'content' in str(x).lower())
        if main_content:
            print(f"   Found main content area")
            # Look for nested structures that might be sections
            potential_sections = main_content.find_all(['div', 'section'], recursive=True)
            sections_with_duration = []
            for section in potential_sections:
                # Check if this section has a heading and duration
                heading = section.find(['h2', 'h3', 'h4'])
                duration_elem = section.find('p', class_=lambda x: x and 'text-muted' in x and 'mt-1' in x)
                if heading and duration_elem:
                    heading_text = heading.get_text(strip=True)
                    duration_text = duration_elem.get_text(strip=True)
                    if any(word in duration_text.lower() for word in ['lesson', 'min', 'hour', 'h', 'm']):
                        sections_with_duration.append({
                            'heading': heading_text,
                            'duration': duration_text,
                            'html_snippet': str(section)[:300]
                        })
            
            if sections_with_duration:
                print(f"   Found {len(sections_with_duration)} sections with durations:")
                for i, sec in enumerate(sections_with_duration, 1):
                    print(f"\n   Section {i}:")
                    print(f"      Heading: {sec['heading']}")
                    print(f"      Duration: {sec['duration']}")
            else:
                print("   No sections with durations found")
        
        # Look for the specific structure shown in the web search results
        print("\n7. LOOKING FOR STRUCTURE FROM WEB CONTENT:")
        print("   Based on web content, there should be sections like:")
        print("   - Review String Basics (7 Lessons 14m)")
        print("   - Revisit String Methods (8 Lessons 15m)")
        print("   - Work With User Input (6 Lessons 16m)")
        print("   - Keep Going With Strings (8 Lessons 14m)")
        print("   - Give Yourself a Challenge (4 Lessons 10m)")
        
        # Search for these specific patterns
        print("\n   Searching for section patterns in HTML...")
        # Look for h2 or h3 followed by duration info
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text(strip=True)
            # Check if next sibling or parent contains duration
            next_elem = heading.find_next_sibling()
            parent = heading.parent
            
            # Check in next sibling
            if next_elem:
                duration_in_sibling = next_elem.find('p', class_=lambda x: x and 'text-muted' in x and 'mt-1' in x)
                if duration_in_sibling:
                    duration_text = duration_in_sibling.get_text(strip=True)
                    if any(word in duration_text.lower() for word in ['lesson', 'min', 'hour']):
                        print(f"   ✓ Found: {heading_text} -> {duration_text}")
            
            # Check in parent
            if parent:
                duration_in_parent = parent.find('p', class_=lambda x: x and 'text-muted' in x and 'mt-1' in x)
                if duration_in_parent:
                    duration_text = duration_in_parent.get_text(strip=True)
                    if any(word in duration_text.lower() for word in ['lesson', 'min', 'hour']):
                        print(f"   ✓ Found in parent: {heading_text} -> {duration_text}")
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"\n✓ HTML saved to: {html_file}")
        print("  Review the HTML file to understand the exact structure")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = "https://realpython.com/courses/python-exercises-string-methods/"
    fetch_and_analyze(url)

