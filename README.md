# Real Python Learning Paths Scraper

A Python-based web scraper that extracts learning path information from [Real Python](https://realpython.com/) and generates a comprehensive Excel workbook with progress tracking capabilities. This project was created as a learning exercise to practice Python web scraping, data extraction, and Excel file manipulation.

## 💡 Why This Project Exists

As a paid subscriber to [Real Python](https://realpython.com/), I wanted to take my Python learning journey seriously. However, I found myself asking some important questions:

- **How long will it actually take?** If I commit to learning Python day by day, how many hours of content do I need to cover?
- **How should I plan my daily time?** I set a goal to complete the learning paths within 6 months, but I needed to know how much time to dedicate each day.
- **How can I track my progress?** I wanted a way to see my progress visually and stay motivated throughout the journey.

This tracker was born from that need. It helps me:
- **Plan strategically**: See the total scope of content and calculate daily time commitments
- **Track progress**: Visual indicators (progress bars, pie charts) keep me motivated
- **Stay organized**: All learning paths, courses, and lessons in one place with clear hierarchy
- **Make informed decisions**: Know exactly how much time I need to invest to meet my 6-month goal

If you're also a [Real Python](https://realpython.com/) subscriber looking to structure your learning journey, this tool might help you too!

## 📋 Table of Contents

- [Why This Project Exists](#-why-this-project-exists)
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Output Format](#output-format)
- [Ethical Scraping & Disclaimer](#ethical-scraping--disclaimer)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This tool scrapes [Real Python's](https://realpython.com/) learning paths to create a structured Excel workbook that helps you:
- **Organize** all learning paths, courses, sections, and lessons in one place
- **Track progress** with visual indicators (progress bars and pie charts)
- **Plan learning** by seeing the full scope of content and estimated durations
- **Navigate easily** with hyperlinked sheets and hierarchical organization

The scraper uses a two-phase approach: first downloading and caching HTML files locally, then processing them to extract structured data. This design minimizes requests to the [Real Python website](https://realpython.com/) and allows for fast re-processing.

## ✨ Features

### Data Extraction
- ✅ Extracts learning paths, courses, sections, and lessons
- ✅ Captures durations at all hierarchy levels (course, section, lesson)
- ✅ Validates duration sums (ensures lessons → sections → courses add up correctly)
- ✅ Handles various content types (courses, exercises, quizzes)

### Excel Output
- ✅ Hierarchical table of contents with proper numbering
- ✅ Hyperlinked navigation between sheets
- ✅ Auto-adjusted column widths and professional formatting
- ✅ Color-coded hierarchy (courses, sections, lessons)

### Progress Tracking
- ✅ **Lesson-level tracking**: Only lessons have manual "Yes/No" dropdowns
- ✅ **Automatic completion**: Sections and courses auto-complete when all children are done
- ✅ **Visual indicators**: Progress bars (data bars) for each learning path
- ✅ **Charts**: Individual pie charts per learning path + overall progress chart
- ✅ **Real-time updates**: Formulas automatically update progress as you mark lessons complete

### Performance & Design
- ✅ Local HTML caching for fast re-processing
- ✅ Respectful scraping with rate limiting
- ✅ Error handling and validation
- ✅ Clean, maintainable code structure

## 📦 Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)
- **Internet connection** (for initial HTML download)

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/real_python_scraper.git
   cd real_python_scraper
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Step 1: Download HTML Cache (One-time)

First, download all HTML pages to cache them locally. This saves time and avoids hitting the website repeatedly:

```bash
python scripts/download_all_html.py
```

**What this does:**
- Downloads the main learning paths page
- Downloads all individual learning path pages
- Downloads all course/exercise/quiz resource pages
- Saves everything in `html_cache/` directory

**Note**: This may take 30+ minutes depending on the number of resources, but you only need to run it once. The scraper will use cached files for all subsequent runs.

### Step 2: Run the Scraper

After caching HTML files, run the main scraper:

```bash
python scripts/scraper.py
```

**What this does:**
- Uses cached HTML files (much faster than re-downloading!)
- Extracts all learning paths, courses, sections, and lessons
- Extracts durations at all levels
- Validates that durations add up correctly
- Generates `learning_paths_analysis.xlsx` in the `output/` directory

### Refreshing the Cache

If [Real Python](https://realpython.com/) updates their content, refresh the cache:

```bash
# Delete the cache directory
rm -rf html_cache/

# Re-download everything
python scripts/download_all_html.py
```

## 📁 Project Structure

```
real_python_scraper/
├── scripts/                      # Python scripts
│   ├── scraper.py               # Main scraper (processes cached HTML)
│   ├── download_all_html.py      # HTML downloader and cache manager
│   ├── analyze_course_page.py   # Helper script for course page analysis
│   └── analyze_exercise_page.py # Helper script for exercise page analysis
├── html_cache/                   # Cached HTML files (gitignored)
│   ├── main_learning_paths.html
│   ├── learning_paths/           # Individual learning path pages
│   └── resources/                # Course/exercise/quiz pages
├── output/                       # Generated Excel files (gitignored)
│   └── learning_paths_analysis.xlsx
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🔧 How It Works

### Architecture

1. **Download Phase** (`download_all_html.py`):
   - Fetches HTML pages from [Real Python](https://realpython.com/)
   - Implements rate limiting to be respectful
   - Caches all HTML files locally
   - Tracks download progress

2. **Processing Phase** (`scraper.py`):
   - Reads cached HTML files
   - Parses HTML using BeautifulSoup
   - Extracts structured data (paths, courses, sections, lessons)
   - Validates duration calculations
   - Generates Excel workbook with formulas and formatting

### Data Flow

```
Real Python Website (https://realpython.com/)
    ↓ (download)
HTML Cache (local)
    ↓ (parse)
Structured Data
    ↓ (generate)
Excel Workbook
```

### Progress Tracking Logic

- **Lessons**: Manual "Yes/No" dropdowns (only editable level)
- **Sections**: Auto-calculated formula: `=IF(all_lessons="Yes", "Yes", "No")`
- **Courses**: Auto-calculated formula: `=IF(all_sections="Yes", "Yes", "No")`
- **Main Sheet**: Counts only completed lessons for accurate progress

## 📊 Output Format

The scraper generates `learning_paths_analysis.xlsx` with:

### Main Sheet: "Learning Paths"
- Table of contents with all learning paths
- Hyperlinks to individual learning path sheets
- Progress tracking columns:
  - Completed Resources (counts completed lessons)
  - Completed Minutes (sums completed lesson minutes)
  - Progress % (percentage of completion)
  - Progress Bar (visual data bars)
- Overall pie chart showing total progress (completed vs remaining hours)
- Grand total row with aggregate statistics

### Individual Learning Path Sheets
- Hierarchical structure:
  - **Courses** (top level, e.g., "1. Setting Up Python")
  - **Sections** (middle level, e.g., "1.1 Python Basics")
  - **Lessons** (bottom level, e.g., "1.1.1 Setting Up Python (Overview)")
- Columns:
  - Title (with proper indentation for hierarchy)
  - Duration (human-readable format)
  - Duration (Minutes) (numeric for calculations)
  - Completed (Yes/No dropdown for lessons, formulas for sections/courses)
  - Row Type (helper column: Course/Section/Lesson)
- Individual pie chart showing that path's progress
- Summary row with totals

### Using Progress Tracking

1. Open the Excel file
2. Navigate to any learning path sheet
3. Mark lessons as "Yes" when you complete them (only editable level)
4. Watch sections and courses auto-complete when all their children are done
5. Check the main "Learning Paths" sheet to see overall progress update automatically

## ⚖️ Ethical Scraping & Disclaimer

### About This Project

This project was created **as a hobby/learning project** to practice Python programming, web scraping, and data manipulation. The goal was to build a personal learning tracker, not to create a commercial product or over-scrape the [Real Python website](https://realpython.com/).

### Respecting robots.txt

**Important**: This scraper is designed to be respectful of [Real Python's](https://realpython.com/) servers:

- ✅ **Rate Limiting**: The download script includes delays between requests
- ✅ **Local Caching**: HTML is cached locally to minimize repeated requests
- ✅ **One-time Download**: Users download HTML once, then process locally
- ✅ **No Aggressive Scraping**: The code does not implement parallel/concurrent scraping that could overwhelm servers

**Before using this scraper**, please:
1. Check [Real Python's](https://realpython.com/) `robots.txt` file: https://realpython.com/robots.txt
2. Review their [Terms of Service](https://realpython.com/terms-of-use/)
3. Use responsibly and only for personal learning purposes
4. Consider reaching out to [Real Python](https://realpython.com/) if you plan to use this at scale

### Legal & Ethical Considerations

- This tool is for **personal use only**
- Do not use this to redistribute [Real Python's](https://realpython.com/) content
- Respect [Real Python's](https://realpython.com/) intellectual property and terms of service
- The authors of this project are not affiliated with [Real Python](https://realpython.com/)
- Use at your own discretion and responsibility

### Recommendations

If you're building a similar project:
- Always check and respect `robots.txt`
- Implement rate limiting
- Use caching to minimize requests
- Add user-agent headers
- Consider reaching out to website owners for permission
- Follow web scraping best practices and legal guidelines

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError" when running scripts

**Solution**: Make sure you've activated your virtual environment and installed dependencies:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: HTML cache is outdated

**Solution**: Delete the cache and re-download:
```bash
rm -rf html_cache/
python scripts/download_all_html.py
```

### Issue: Excel file shows "#REF!" errors

**Solution**: This usually means sheet names are too long or contain invalid characters. The scraper automatically truncates and sanitizes sheet names, but if you see this, try:
1. Regenerating the Excel file
2. Checking if any learning path names are extremely long

### Issue: Progress tracking not updating

**Solution**: 
- Make sure you're marking **lessons** (not sections or courses) as "Yes"
- Sections and courses are formula-based and update automatically
- Check that Excel formulas are enabled (File → Options → Formulas → Enable iterative calculation if needed)

### Issue: Download script is very slow

**Solution**: This is expected behavior. The script includes delays to be respectful. The first download takes 30+ minutes, but subsequent runs use cached files and are much faster.

## 🤝 Contributing

Contributions are welcome! This is a learning project, so feel free to:

1. **Report bugs**: Open an issue describing the problem
2. **Suggest features**: Share ideas for improvements
3. **Submit pull requests**: 
   - Fork the repository
   - Create a feature branch
   - Make your changes
   - Submit a pull request with a clear description

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comments for complex logic
- Test your changes before submitting
- Update documentation if needed

## 📄 License

This project is provided as-is for educational purposes. Please respect [Real Python's](https://realpython.com/) terms of service and intellectual property rights when using this tool.

---

**Note**: This project is not affiliated with, endorsed by, or connected to [Real Python](https://realpython.com/). Real Python is a trademark of their respective owners.
