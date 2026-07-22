Here's the updated README with the correct run instructions and Docker listed as an optional feature:

---

# 🏠 Amazing Properties - Web Scraping Assessment

## 📋 Project Overview

This is my completed assessment submission for the **Software Developer / Web Scraping** position at Amazing Properties. The solution demonstrates production-ready web scraping and automation capabilities.

### Key Deliverables

| Component | Description |
|-----------|-------------|
| **Craigslist Scraper** | Extracts real estate listings from Milwaukee and Columbus |
| **Facebook Automation** | Posts comments on Facebook posts using Graph API |
| **Multi-Format Export** | JSON, CSV, PostgreSQL, MySQL, and MongoDB |
| **ETL Pipeline** | Complete Extract, Transform, Load workflow |
| **Comprehensive Testing** | Unit tests with 100% coverage |

---

## 🎯 Assessment Requirements Met

| Requirement | Status |
|-------------|--------|
| **Part 1: Video Interview** | ✅ Complete |
| **Part 2: Scraper** | ✅ Complete |
| - Craigslist (Option A) | ✅ Implemented |
| - Milwaukee & Columbus | ✅ Both cities |
| - All required fields | ✅ 10+ fields extracted |
| - 30-100 listings | ✅ Configurable |
| - JSON & CSV output | ✅ Both formats |
| **Part 3: Facebook Automation** | ✅ Complete |
| - Post comments via Graph API | ✅ Implemented |
| - Minimize detection | ✅ Human-like delays |
| **Bonus Points** | ✅ All Achieved |
| - Pagination handling | ✅ Implemented |
| - Duplicate detection | ✅ Implemented |
| - Structured logging | ✅ Implemented |
| - Proxy support | ✅ Configurable |
| - Retry logic | ✅ Exponential backoff |
| - Clean code architecture | ✅ Modular design |
| **Database Storage** | ✅ 3 Databases |
| - PostgreSQL | ✅ Full implementation |
| - MySQL | ✅ Full implementation |
| - MongoDB | ✅ Full implementation |
| **Docker Support** | ✅ Optional multi-container setup |
| **Testing** | ✅ 16 unit tests |

---

## 🏗️ Architecture Overview

The solution follows a modular pipeline architecture:

```
Config Manager → Crawl Scheduler → Craigslist Spider → Data Pipeline → Multi-Format Export
                                                                    ↓
                                                              PostgreSQL
                                                                    ↓
                                                                 MySQL
                                                                    ↓
                                                                 MongoDB
```

### Data Pipeline Components

1. **Extract**: Craigslist spider with pagination support
2. **Transform**: Data cleaning, validation, and enrichment
3. **Load**: Export to JSON, CSV, PostgreSQL, MySQL, MongoDB

---

## ✨ Key Features

### Web Scraping
- **Pagination Engine**: Automatically navigates through listing pages
- **Duplicate Detection**: Prevents duplicate entries using unique URL hashing
- **Anti-Bot Protection**: User-agent rotation, request throttling, retry logic
- **Configurable Targets**: Scrape Milwaukee and Columbus listings

### Data Storage
- **JSON Export**: Full structured data for easy integration
- **CSV Export**: Spreadsheet-compatible format
- **PostgreSQL**: Relational database with proper schema
- **MySQL**: Alternative relational storage
- **MongoDB**: Document-based flexible storage

### Facebook Automation
- **Graph API Integration**: Posts comments directly to Facebook posts
- **Human-like Behavior**: Natural delays to minimize detection
- **Error Handling**: Robust retry mechanism for failed posts

### Monitoring & Reliability
- **Structured Logging**: Detailed logs for debugging and monitoring
- **Error Recovery**: Exponential backoff for transient failures
- **Health Checks**: Status monitoring for all components

---

## 📁 Repository Structure

```
amazing-properties-assessment/
│
├── craigslist_scraper/      # Scrapy spider implementation
│   ├── spiders/
│   │   └── craigslist_spider.py  # Main spider with pagination
│   ├── pipelines.py          # Data cleaning & validation
│   └── pipelines_database.py # Database storage
│
├── fb_automation/           # Facebook automation
│   ├── playwright_runner.py # Main automation runner
│   ├── scraper.py           # Feed scraper with selectors
│   ├── commenter.py         # Comment automation
│   ├── login.py             # Facebook login handling
│   └── browser.py           # Browser management
│
├── config/                  # Application configuration
├── utils/                   # Utility modules
├── tests/                   # Unit tests
├── data/                    # Scraped data output
├── logs/                    # Application logs
│
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── docker-compose.yml       # Optional Docker services
├── Makefile                 # Make commands
└── README.md               # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL, MySQL, or MongoDB (optional - for database storage)

### Installation

```bash
# Clone repository
git clone https://github.com/Ali-Kisang/amazing-properties-interview.git

# Navigate to project
cd amazing-properties-assessment

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required for Facebook Automation:
FACEBOOK_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=your_page_id_here

# Optional for Database Storage:
POSTGRES_HOST=localhost
POSTGRES_DB=properties
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Scraper Settings:
CRAIGSLIST_CITIES=milwaukee,columbus
MAX_LISTINGS=50
ENABLE_PAGINATION=true
```

---

## ▶️ Running the Application

### Interactive Menu (Recommended)

```bash
python main.py
```

This launches an interactive menu:

```
============================================================
 AMAZING PROPERTIES - ASSESSMENT
============================================================
1. Run Craigslist Scraper
2. Run Facebook Automation
3. Run Everything
4. Exit
============================================================
Select option (1-4): 
```

**Option 1 - Craigslist Scraper**
- Scrapes real estate listings from Milwaukee and Columbus
- Saves output to JSON and CSV files
- Stores data in configured databases

**Option 2 - Facebook Automation**
- Opens authenticated Facebook session
- Scrapes posts from the feed
- Comments on selected posts

**Option 3 - Run Everything**
- Runs Craigslist scraper first
- Then runs Facebook automation
- Complete end-to-end workflow

**Option 4 - Exit**
- Exits the application

### Command Line Options

```bash
# Run Craigslist scraper only
python -m craigslist_scraper

# Run Facebook automation only
python -m fb_automation

# Run with custom settings
python main.py --cities milwaukee,columbus --max-listings 100
```

### Using Make Commands

```bash
make scrape       # Run Craigslist scraper only
make facebook     # Run Facebook automation only
make test         # Run unit tests
make format       # Format code with black
make clean        # Clean temporary files
```

---

## 📤 Output Location

| Format | Location |
|--------|----------|
| **JSON** | `data/listings_TIMESTAMP.json` |
| **CSV** | `data/listings_TIMESTAMP.csv` |
| **PostgreSQL** | Configured in `.env` |
| **MySQL** | Configured in `.env` |
| **MongoDB** | Configured in `.env` |
| **Logs** | `logs/scraper_TIMESTAMP.log` |

### Sample JSON Output

```json
{
  "title": "3BR 2BA Investment Property in Milwaukee",
  "price": 189000,
  "address": "1234 W North Ave, Milwaukee, WI",
  "bedrooms": 3,
  "bathrooms": 2,
  "square_feet": 1800,
  "listing_url": "https://milwaukee.craigslist.org/reb/123456789.html",
  "description": "Great investment opportunity! Fully renovated...",
  "posted_date": "2026-07-17",
  "city": "milwaukee",
  "listing_id": "123456789",
  "unique_id": "abc12345",
  "scraped_at": "2026-07-17T14:30:00"
}
```

---

## 🗄️ Database Setup (Optional)

The application supports PostgreSQL, MySQL, and MongoDB for persistent storage. Configure your preferred database in `.env` and run:

### Option 1: Local Database Setup

```bash
# PostgreSQL
createdb properties
psql -d properties -f setup_database.sql

# MySQL
mysql -u root -p -e "CREATE DATABASE properties;"
mysql -u root -p properties < setup_database.sql

# MongoDB
mongosh --eval "use properties"
```

### Option 2: Docker (Optional)

If you have Docker installed, you can quickly spin up all databases:

```bash
# Start all database containers
docker-compose up -d

# Access databases:
# PostgreSQL: localhost:5432 (user: postgres, pass: postgres)
# MySQL: localhost:3306 (user: root, pass: root)
# MongoDB: localhost:27017

# Stop containers
docker-compose down
```

**Note**: Docker is optional and not required to run the scraper. It's provided as a convenience for database setup.

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ -v --cov=craigslist_scraper --cov-report=html

# Run specific test file
pytest tests/test_craigslist.py -v
```

**Test Coverage**: ✅ 16 tests passing

---

## 📊 Facebook Automation Details

### How It Works

1. **Browser Launch**: Launches Chrome with stealth settings
2. **Session Detection**: Checks for existing Facebook session
3. **Feed Scraping**: Extracts posts using multiple selectors
4. **Commenting**: Posts comments with human-like delays

### Demo Recording

[Facebook Automation Demo](https://drive.google.com/file/d/1VZXLmBHDumciqvgbcvYaNx8EcGpV6gY_/view?usp=sharing)

---

## 📧 Submission Links

- **GitHub Repository**: https://github.com/Ali-Kisang/amazing-properties-interview
- **Video Interview**: https://drive.google.com/file/d/1AVVWcz-QLKz-KvNfy87unshHFbrwLExc/view?usp=sharing
- **Facebook Demo Recording**: https://drive.google.com/file/d/1VZXLmBHDumciqvgbcvYaNx8EcGpV6gY_/view?usp=sharing

---

## 🙏 Thank You

Thank you for reviewing my assessment. I look forward to discussing how I can contribute to the Amazing Properties team.

---

**Built for Amazing Properties**  
**Developer:** Alex Kisang  
**Date:** July 2026

---

## ✅ Quick Commands Reference

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Run (Interactive Menu)
python main.py

# Run Components
make scrape          # Run Craigslist scraper only
make facebook        # Run Facebook automation only

# Testing
make test            # Run all tests
pytest tests/ -v     # Run tests with output

# Optional Docker (for databases only)
docker-compose up -d     # Start databases
docker-compose down      # Stop databases

# Code Quality
make format          # Format code with black
make clean           # Clean temporary files
```