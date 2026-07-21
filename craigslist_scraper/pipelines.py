"""
Data Pipeline: Data Validator -> Cleaning Pipeline -> Location Filter -> Duplicate Filter -> Export Pipeline
"""
from scrapy.exceptions import DropItem
from loguru import logger
import json
import csv
import re
from datetime import datetime
from pathlib import Path
import hashlib
import os


class DataValidator:
    """Data Validator - validates required fields"""

    REQUIRED_FIELDS = ['listing_url', 'title']

    def process_item(self, item, spider):
        for field in self.REQUIRED_FIELDS:
            if not item.get(field):
                raise DropItem(f"Missing required field: {field}")
        return item


class CleaningPipeline:
    """Cleaning Pipeline - cleans and normalizes data"""

    def process_item(self, item, spider):
        if item.get('title'):
            item['title'] = re.sub(r'\s+', ' ', str(item['title'])).strip()

        if item.get('description'):
            item['description'] = re.sub(r'\s+', ' ', str(item['description'])).strip()
            item['description'] = re.sub(r'<[^>]+>', '', str(item['description']))

        if item.get('price'):
            if isinstance(item['price'], str):
                item['price'] = re.sub(r'[$,]', '', str(item['price']))
                try:
                    item['price'] = int(float(item['price']))
                except ValueError:
                    item['price'] = None

        if item.get('address'):
            address = str(item['address'])
            address = re.sub(r'\([^)]*\)', '', address)
            address = re.sub(r'\s+', ' ', address).strip()
            item['address'] = address

        if item.get('square_feet'):
            square_feet = str(item['square_feet'])
            square_feet = re.sub(r'[^\d]', '', square_feet)
            item['square_feet'] = int(square_feet) if square_feet else None

        if not item.get('unique_id') and item.get('listing_url'):
            item['unique_id'] = hashlib.md5(
                str(item['listing_url']).encode()
            ).hexdigest()[:16]

        item['scraped_at'] = datetime.now().isoformat()

        return item


class LocationFilter:
    """
    Filters out listings that aren't genuinely tied to the target metro area,
    and flags likely non-real-estate results (land, mobile homes).

    Craigslist's newer /search/area endpoint has a looser geographic radius
    than the old per-city subdomain search, so it can return results from
    unrelated states (e.g. a Minneapolis listing under a "milwaukee" search).
    This pipeline checks the item's title/location text against a set of
    known local place names for each target city, rather than trusting the
    'city' field the spider assigned based on which URL it requested.
    """

    # Local place names used to confirm a listing is actually in-market.
    # Not exhaustive -- extend as needed if you see more false positives/negatives.
    METRO_KEYWORDS = {
        'milwaukee': [
            'milwaukee', 'wauwatosa', 'west allis', 'brookfield', 'waukesha',
            'franklin', 'germantown', 'menomonee falls', 'oak creek',
            'greenfield', 'cudahy', 'south milwaukee', 'wisconsin', ' wi',
            'wi ',
        ],
        'columbus': [
            'columbus', 'westerville', 'reynoldsburg', 'dublin', 'hilliard',
            'gahanna', 'grove city', 'whitehall', 'bexley', 'worthington',
            'blacklick', 'brice', 'ohio', ' oh', 'oh ',
        ],
    }

    # Title patterns suggesting the listing isn't the SFH/duplex/multi-family
    # property type the brief asks for, even though it passed the price filter.
    NON_TARGET_PATTERNS = [
        r'\bmobile home\b', r'\bmanufactured home\b', r'\bland for sale\b',
        r'\blot for sale\b', r'\bvacant lot\b', r'\bacres\b', r'\bwooded\b',
        r'\bcommercial lot\b', r'\b55\+\b', r'\bsnowbird',
    ]

    def process_item(self, item, spider):
        title = (item.get('title') or '').lower()
        location = (item.get('location') or '').lower()
        combined = f"{title} {location}"

        target_city = item.get('city', '').lower()
        keywords = self.METRO_KEYWORDS.get(target_city, [])

        in_metro = any(kw in combined for kw in keywords)
        item['in_target_metro'] = in_metro

        is_non_target_type = any(re.search(p, title) for p in self.NON_TARGET_PATTERNS)
        item['likely_non_target_property'] = is_non_target_type

        if not in_metro:
            raise DropItem(
                f"Dropped: '{item.get('title')}' does not match {target_city} metro area "
                f"(location field: {item.get('location')!r})"
            )

        # Non-target property types (land, mobile homes) are flagged, not dropped,
        # so they remain visible in the output for transparency/reporting rather
        # than silently disappearing.
        if is_non_target_type:
            logger.warning(f"⚠️ Flagged as likely non-target property type: {item.get('title')}")

        return item


class DuplicateFilter:
    """Remove duplicate records"""

    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        unique_id = item.get('unique_id')
        if not unique_id:
            unique_id = hashlib.md5(str(item.get('listing_url', '')).encode()).hexdigest()[:16]
            item['unique_id'] = unique_id

        if unique_id in self.seen_ids:
            raise DropItem(f"Duplicate item: {unique_id}")

        self.seen_ids.add(unique_id)
        return item


class ExportPipeline:
    """Export Pipeline - exports to CSV and JSON"""

    def __init__(self):
        self.items = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.data_dir = Path('../data')
        self.data_dir.mkdir(exist_ok=True)

    def process_item(self, item, spider):
        item_dict = dict(item)
        self.items.append(item_dict)
        return item

    def close_spider(self, spider):
        if not self.items:
            logger.warning("No items to export")
            return

        json_file = self.data_dir / f'listings_{self.timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Exported {len(self.items)} items to {json_file}")

        try:
            import pandas as pd
            csv_file = self.data_dir / f'listings_{self.timestamp}.csv'
            df = pd.DataFrame(self.items)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            logger.info(f"📊 Exported {len(self.items)} items to {csv_file}")
        except ImportError:
            logger.warning("Pandas not available, skipping CSV export")