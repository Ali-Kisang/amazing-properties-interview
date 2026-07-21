#!/usr/bin/env python
"""
Standalone Craigslist scraper that works without Scrapy project
Run: python craigslist_standalone.py
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import os

def scrape_craigslist(city, min_price=50000, max_price=250000):
    """Scrape Craigslist for real estate listings"""
    print(f"🔍 Scraping {city}...")
    
    url = f"https://{city}.craigslist.org/search/rea?query=single+family+home|duplex|multi-family|investment&min_price={min_price}&max_price={max_price}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📄 {city} - Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ {city} - HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find listings
        listings = soup.find_all('li', {'data-pid': True})
        if not listings:
            listings = soup.find_all('li', class_='result-row')
        
        print(f"📍 {city} - Found {len(listings)} listings")
        
        results = []
        for listing in listings[:30]:
            try:
                # Get URL
                link = listing.find('a', href=True)
                if not link:
                    continue
                
                detail_url = link.get('href')
                if detail_url.startswith('//'):
                    detail_url = 'https:' + detail_url
                elif not detail_url.startswith('http'):
                    detail_url = f"https://{city}.craigslist.org{detail_url}"
                
                # Get title
                title = link.text.strip() if link.text else None
                
                # Get price
                price_elem = listing.find('span', class_='price')
                price = price_elem.text.strip() if price_elem else None
                
                # Get location
                location_elem = listing.find('span', class_='px')
                location = location_elem.text.strip() if location_elem else None
                
                # Get posted date
                date_elem = listing.find('time')
                posted_date = date_elem.get('datetime') if date_elem else None
                
                # Get housing info
                housing_elem = listing.find('span', class_='housing')
                housing = housing_elem.text.strip() if housing_elem else None
                
                bedrooms = None
                bathrooms = None
                if housing:
                    br_match = re.search(r'(\d+)\s*br', housing, re.IGNORECASE)
                    ba_match = re.search(r'(\d+)\s*ba', housing, re.IGNORECASE)
                    if br_match:
                        bedrooms = int(br_match.group(1))
                    if ba_match:
                        bathrooms = int(ba_match.group(1))
                
                results.append({
                    'title': title,
                    'price': price,
                    'address': location,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'square_feet': None,
                    'listing_url': detail_url,
                    'description': None,
                    'posted_date': posted_date,
                    'city': city,
                    'scraped_at': datetime.now().isoformat()
                })
                
                print(f"📄 Found: {title[:50] if title else 'No title'} - {price}")
                
            except Exception as e:
                print(f"Error processing listing: {e}")
                continue
        
        return results
        
    except Exception as e:
        print(f"❌ Error scraping {city}: {e}")
        return []

def main():
    """Main function"""
    print("=" * 60)
    print("🏠 CRAIGSLIST STANDALONE SCRAPER")
    print("=" * 60)
    print("📍 Scraping Milwaukee and Columbus")
    print("💰 Price Range: $50,000 - $250,000")
    print("=" * 60)
    
    cities = ['milwaukee', 'columbus']
    all_listings = []
    
    for city in cities:
        listings = scrape_craigslist(city)
        all_listings.extend(listings)
        time.sleep(2)  # Be polite
    
    print("\n" + "=" * 60)
    print(f"📊 TOTAL LISTINGS: {len(all_listings)}")
    print("=" * 60)
    
    # Create data directory if needed
    os.makedirs('data', exist_ok=True)
    
    # Save to JSON
    output_file = 'data/listings.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_listings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(all_listings)} listings to {output_file}")
    
    # Also save to CSV
    if all_listings:
        try:
            import pandas as pd
            df = pd.DataFrame(all_listings)
            csv_file = 'data/listings.csv'
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"✅ Saved to {csv_file}")
        except ImportError:
            print("⚠️ Pandas not installed, skipping CSV export")
    
    print("\n📁 Output files saved in 'data/' directory")

if __name__ == "__main__":
    main()
