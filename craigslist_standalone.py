#!/usr/bin/env python
"""
Standalone Craigslist scraper with updated selectors
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📄 {city} - Status: {response.status_code}")
        print(f"📄 Response length: {len(response.text)} characters")
        
        if response.status_code != 200:
            print(f"❌ {city} - HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save HTML for debugging
        debug_file = f"logs/debug_{city}.html"
        os.makedirs('logs', exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(response.text[:5000])
        print(f"💾 Saved HTML preview to {debug_file}")
        
        # Try different selectors for listings
        listings = []
        
        # Method 1: data-pid attribute
        listings = soup.find_all('li', {'data-pid': True})
        print(f"📍 {city} - Found {len(listings)} listings with data-pid")
        
        if not listings:
            # Method 2: result-row class
            listings = soup.find_all('li', class_='result-row')
            print(f"📍 {city} - Found {len(listings)} listings with result-row")
        
        if not listings:
            # Method 3: Search for any li with a link containing /reb/
            all_links = soup.find_all('a', href=re.compile(r'/reb/'))
            listings = [link.parent for link in all_links if link.parent.name == 'li']
            print(f"📍 {city} - Found {len(listings)} listings with /reb/ links")
        
        if not listings:
            # Method 4: Look for any div with class containing "result"
            listings = soup.find_all('div', class_=re.compile(r'result'))
            print(f"📍 {city} - Found {len(listings)} divs with result class")
        
        if not listings:
            print(f"⚠️ No listings found for {city}")
            # Check if we got blocked
            if "blocked" in response.text.lower():
                print(f"🚫 {city} - Blocked by Craigslist!")
            elif "captcha" in response.text.lower():
                print(f"🚫 {city} - CAPTCHA detected!")
            return []
        
        results = []
        for listing in listings[:35]:
            try:
                # Get URL
                link = None
                if hasattr(listing, 'find'):
                    link = listing.find('a', href=True)
                else:
                    # If it's just a link element
                    link = listing if listing.name == 'a' else None
                
                if not link:
                    continue
                
                detail_url = link.get('href')
                if detail_url.startswith('//'):
                    detail_url = 'https:' + detail_url
                elif not detail_url.startswith('http'):
                    detail_url = f"https://{city}.craigslist.org{detail_url}"
                
                # Get title
                title = link.text.strip() if link.text else None
                
                # Get price - look in various places
                price = None
                price_elem = listing.find('span', class_='price')
                if price_elem:
                    price = price_elem.text.strip()
                else:
                    # Try to find price in text
                    price_match = re.search(r'\$([\d,]+)', listing.text)
                    if price_match:
                        price = f"${price_match.group(1)}"
                
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
                
                # Try to get square footage from title or housing info
                square_feet = None
                if title:
                    sqft_match = re.search(r'(\d+)\s*(?:sq\s*ft|sqft)', title, re.IGNORECASE)
                    if sqft_match:
                        square_feet = sqft_match.group(1)
                
                results.append({
                    'title': title,
                    'price': price,
                    'address': location,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'square_feet': square_feet,
                    'listing_url': detail_url,
                    'description': None,
                    'posted_date': posted_date,
                    'city': city,
                    'scraped_at': datetime.now().isoformat()
                })
                
                print(f"📄 [{len(results)}] {title[:50] if title else 'No title'} - {price}")
                
            except Exception as e:
                print(f"Error processing listing: {e}")
                continue
        
        return results
        
    except Exception as e:
        print(f"❌ Error scraping {city}: {e}")
        import traceback
        traceback.print_exc()
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
    print("💡 Check 'logs/debug_*.html' for HTML debugging")

if __name__ == "__main__":
    main()
