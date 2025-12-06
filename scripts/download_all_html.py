"""One-time script to download all HTML pages from Real Python learning paths"""
from pathlib import Path
import re
import time
import json
import requests
from bs4 import BeautifulSoup

# Base URL
BASE_URL = "https://realpython.com/learning-paths/"
# Get project root (parent of scripts directory)
PROJECT_ROOT = Path(__file__).parent.parent
HTML_DIR = PROJECT_ROOT / "html_cache"
TRACKER_FILE = HTML_DIR / "download_tracker.json"

def load_tracker():
    """Load the download tracker"""
    if TRACKER_FILE.exists():
        try:
            return json.loads(TRACKER_FILE.read_text())
        except:
            return {"downloaded": set(), "failed": set()}
    return {"downloaded": set(), "failed": set()}

def save_tracker(tracker):
    """Save the download tracker"""
    # Convert sets to lists for JSON serialization
    tracker_json = {
        "downloaded": list(tracker["downloaded"]),
        "failed": list(tracker["failed"])
    }
    TRACKER_FILE.write_text(json.dumps(tracker_json, indent=2))

def fetch_page(url, max_retries=3, base_delay=2):
    """Fetch a page with retry logic and exponential backoff for 429 errors"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            # Handle 429 Too Many Requests
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', base_delay * (2 ** attempt)))
                wait_time = max(retry_after, base_delay * (2 ** attempt))
                print(f"      ⚠️ Rate limited (429). Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.exceptions.Timeout:
            print(f"      ⚠️ Timeout. Retrying {attempt + 1}/{max_retries}...")
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
            continue
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                print(f"      ⚠️ Error: {e}. Retrying in {wait_time} seconds ({attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                print(f"      ⚠️ Failed after {max_retries} attempts: {e}")
                return None
    
    return None

def save_html(url, html_content, filepath):
    """Save HTML content to file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(html_content, encoding='utf-8')
    print(f"  ✓ Saved: {filepath}")

def sanitize_filename(name):
    """Create a safe filename from a string"""
    # Remove or replace invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '-', name)
    name = re.sub(r'\s+', '_', name)
    name = name[:100]  # Limit length
    return name

def extract_learning_paths(soup):
    """Extract learning path titles and URLs from the main page"""
    if not soup:
        return []

    paths = []
    for card in soup.find_all("learning-path-card"):
        title_tag = card.find("h2")
        link_tag = card.find("a", class_="stretched-link")
        title = title_tag.get_text(strip=True) if title_tag else None
        href = link_tag.get("href") if link_tag else None
        if title and href:
            if href.startswith('/'):
                href = f"https://realpython.com{href}"
            paths.append({"title": title, "url": href})
    return paths

def extract_resources_from_path(soup):
    """Extract all resource URLs from a learning path page"""
    if not soup:
        return []

    all_containers = soup.find_all('div', class_=lambda x: x and 'container' in x and 'border' in x and 'rounded' in x and 'shadow-sm' in x)
    
    resources = []
    seen_resources = set()  # Avoid duplicates
    
    for container in all_containers:
        link_elem = container.find('a', class_='stretched-link', href=True)
        if not link_elem:
            continue
        
        href = link_elem.get('href', '')
        if '/courses/' in href or '/quizzes/' in href or '/tutorials/' in href:
            if href.startswith('/'):
                href = f"https://realpython.com{href}"
            # Only add if we haven't seen it
            if href not in seen_resources:
                seen_resources.add(href)
                resources.append(href)
    
    return resources

def get_file_path_for_url(url):
    """Get the file path for a URL"""
    url_clean = url.rstrip('/')
    
    # Main learning paths page
    if url_clean == BASE_URL.rstrip('/') or url_clean.endswith('/learning-paths'):
        return HTML_DIR / "main_learning_paths.html"
    
    # Learning path pages
    if '/learning-paths/' in url and url.count('/learning-paths/') == 1:
        url_path = url_clean.replace('https://realpython.com/learning-paths/', '').rstrip('/')
        path_filename = url_path.replace('/', '_')
        return HTML_DIR / "learning_paths" / f"{path_filename}.html"
    
    # Resource pages
    if '/courses/' in url or '/quizzes/' in url or '/tutorials/' in url:
        url_path = url_clean.replace('https://realpython.com/', '').rstrip('/')
        url_path = url_path.replace('/', '_')
        if len(url_path) > 200:
            url_path = url_path[:200]
        return HTML_DIR / "resources" / f"{url_path}.html"
    
    return None

def download_all():
    """Download all HTML pages with tracking"""
    print("=" * 60)
    print("DOWNLOADING ALL HTML PAGES")
    print("=" * 60)
    
    # Create HTML cache directory
    HTML_DIR.mkdir(exist_ok=True)
    
    # Load tracker
    tracker = load_tracker()
    tracker["downloaded"] = set(tracker.get("downloaded", []))
    tracker["failed"] = set(tracker.get("failed", []))
    
    print(f"   📊 Tracker: {len(tracker['downloaded'])} already downloaded, {len(tracker['failed'])} previously failed")
    
    # Step 1: Download main learning paths page
    print("\n1. Downloading main learning paths page...")
    main_file = get_file_path_for_url(BASE_URL)
    
    soup = None
    if BASE_URL in tracker["downloaded"] and main_file and main_file.exists() and main_file.stat().st_size > 0:
        print(f"   ✓ Already cached: {main_file}")
        try:
            soup = BeautifulSoup(main_file.read_text(encoding='utf-8'), 'html.parser')
        except Exception as e:
            print(f"   ⚠️ Error reading cached file, re-downloading: {e}")
            soup = None
    
    if not soup:
        soup = fetch_page(BASE_URL)
        if soup:
            save_html(BASE_URL, str(soup), main_file)
            tracker["downloaded"].add(BASE_URL)
            save_tracker(tracker)
            print(f"   ✓ Main page saved")
            time.sleep(2)  # Delay after main page
        else:
            print("   ⚠️ Failed to fetch main page")
            tracker["failed"].add(BASE_URL)
            save_tracker(tracker)
            return
    
    # Step 2: Extract all learning paths
    print("\n2. Extracting learning paths...")
    learning_paths = extract_learning_paths(soup)
    print(f"   ✓ Found {len(learning_paths)} learning paths")
    
    # Step 3: Download each learning path page
    print("\n3. Downloading learning path pages...")
    all_resources = []
    
    for idx, path in enumerate(learning_paths, 1):
        print(f"\n   [{idx}/{len(learning_paths)}] {path['title']}")
        
        path_file = get_file_path_for_url(path['url'])
        
        # Check if already downloaded
        if path['url'] in tracker["downloaded"] and path_file and path_file.exists() and path_file.stat().st_size > 0:
            print(f"      ✓ Already cached, loading from file...")
            try:
                path_soup = BeautifulSoup(path_file.read_text(encoding='utf-8'), 'html.parser')
            except Exception as e:
                print(f"      ⚠️ Error reading cached file, re-downloading: {e}")
                path_soup = None
        else:
            path_soup = None
        
        if not path_soup:
            # Download learning path page
            path_soup = fetch_page(path['url'])
            if path_soup:
                save_html(path['url'], str(path_soup), path_file)
                tracker["downloaded"].add(path['url'])
                save_tracker(tracker)
            else:
                print(f"      ⚠️ Failed to fetch learning path page")
                tracker["failed"].add(path['url'])
                save_tracker(tracker)
                continue
        
        # Extract resources from this learning path
        resources = extract_resources_from_path(path_soup)
        print(f"      Found {len(resources)} resources")
        all_resources.extend(resources)
        
        # Be polite - longer delay between learning paths
        time.sleep(2)
    
    # Step 4: Download all resource pages (courses, exercises, quizzes)
    print(f"\n4. Downloading resource pages ({len(all_resources)} total)...")
    
    # Remove duplicates
    unique_resources = list(set(all_resources))
    print(f"   ✓ {len(unique_resources)} unique resources to download")
    
    # Filter out already downloaded
    to_download = [url for url in unique_resources if url not in tracker["downloaded"]]
    already_cached = len(unique_resources) - len(to_download)
    
    if already_cached > 0:
        print(f"   ✓ {already_cached} resources already cached, skipping...")
    
    successful_resources = already_cached
    failed_resources = len([url for url in unique_resources if url in tracker["failed"]])
    
    for idx, resource_url in enumerate(to_download, 1):
        if idx % 10 == 0:
            print(f"   Progress: {idx}/{len(to_download)} ({idx*100//len(to_download)}%) - Success: {successful_resources}, Failed: {failed_resources}")
        else:
            print(f"   [{idx}/{len(to_download)}] {resource_url[:60]}...")
        
        resource_file = get_file_path_for_url(resource_url)
        
        # Double-check file doesn't exist (in case tracker is out of sync)
        if resource_file and resource_file.exists() and resource_file.stat().st_size > 0:
            print(f"      ✓ Already exists, skipping...")
            tracker["downloaded"].add(resource_url)
            successful_resources += 1
            save_tracker(tracker)
            continue
        
        resource_soup = fetch_page(resource_url)
        if resource_soup:
            save_html(resource_url, str(resource_soup), resource_file)
            tracker["downloaded"].add(resource_url)
            save_tracker(tracker)
            successful_resources += 1
        else:
            print(f"      ⚠️ Failed to fetch resource page")
            tracker["failed"].add(resource_url)
            save_tracker(tracker)
            failed_resources += 1
        
        # Be polite - longer delay between requests (2-3 seconds)
        time.sleep(2.5)
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    print(f"✓ Main page: 1 file")
    print(f"✓ Learning paths: {len(learning_paths)} files")
    print(f"✓ Resources: {successful_resources} files downloaded ({failed_resources} failed)")
    print(f"✓ Total: {1 + len(learning_paths) + successful_resources} HTML files saved")
    print(f"\nAll files saved in: {HTML_DIR.absolute()}")
    print("\nYou can now run the main scraper and it will use these cached files!")

if __name__ == "__main__":
    download_all()

