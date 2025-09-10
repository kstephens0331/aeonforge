#!/usr/bin/env python3
"""
Advanced Product Scraper
Incorporates current best practices from research
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from urllib.parse import urljoin
import json
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Product:
    """Product data structure"""
    name: str
    price: str
    url: str
    availability: str = "Unknown"
    description: str = ""
    image_url: str = ""
    category: str = ""

class ProductScraper:
    """Professional product scraper with advanced features"""
    
    def __init__(self, delay=2):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.products: List[Product] = []
        self.logger = logging.getLogger(__name__)
        
    def scrape_products(self, urls: List[str] = None) -> List[Product]:
        """Scrape products from given URLs"""
        if urls is None:
            urls = self._get_default_urls()
            
        for url in urls:
            try:
                self._scrape_single_product(url)
                time.sleep(self.delay)
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                
        return self.products
    
    def _get_default_urls(self) -> List[str]:
        """Get default URLs for demonstration"""
        return [
            "https://example-store.com/product1",
            "https://example-store.com/product2"
        ]
    
    def _scrape_single_product(self, url: str):
        """Scrape a single product"""
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product = Product(
            name=self._extract_text(soup, ['.product-title', 'h1', '.name']),
            price=self._extract_text(soup, ['.price', '.cost', '.amount']),
            url=url,
            availability=self._extract_text(soup, ['.stock', '.availability']),
            description=self._extract_text(soup, ['.description', '.details'])
        )
        
        self.products.append(product)
        self.logger.info(f"Scraped: {product.name}")
    
    def _extract_text(self, soup, selectors: List[str]) -> str:
        """Extract text using multiple selector options"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return "N/A"
    
    def save_results(self, products: List[Product] = None):
        """Save results to multiple formats"""
        if products is None:
            products = self.products
            
        if not products:
            self.logger.warning("No products to save")
            return
            
        # Save to JSON
        products_dict = [
            {
                'name': p.name,
                'price': p.price,
                'url': p.url,
                'availability': p.availability,
                'description': p.description
            } for p in products
        ]
        
        with open('products.json', 'w') as f:
            json.dump(products_dict, f, indent=2)
            
        # Save to CSV
        df = pd.DataFrame(products_dict)
        df.to_csv('products.csv', index=False)
        
        self.logger.info(f"Saved {len(products)} products to JSON and CSV")
