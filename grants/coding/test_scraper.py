"""
Test script for the enhanced web scraper.
This script tests the web_scraper_utils module with a single URL.
"""

import sys
import os
import time

# Add the parent directory to the path so we can import the web_scraper_utils module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the enhanced web scraper
from coding.web_scraper_utils import scrape_grants, format_grant_results

def test_web_scraper(test_url):
    """Run a test of the web scraper with a single URL"""
    print(f"\n--- Testing Web Scraper with URL: {test_url} ---")
    start_time = time.time()
    
    try:
        # Scrape the URL
        results = scrape_grants([test_url])
        
        # Format the results
        formatted_output = format_grant_results(results)
        
        # Print the results
        print(formatted_output)
        
        # Print execution time
        end_time = time.time()
        print(f"Execution time: {end_time - start_time:.2f} seconds")
        
        return True
    except Exception as e:
        print(f"Error testing web scraper: {str(e)}")
        return False

if __name__ == "__main__":
    # Test with a more reliable sample URL
    test_url = "https://www.dsireusa.org/"
    
    # Alternative URLs to try if the first one fails
    alternative_urls = [
        "https://www.brookhavenga.gov/1304/Economic-Development",
        "https://www.dekalbcountyga.gov/community-development/community-development-block-grant-cdbg",
        "https://www.georgiapower.com/residential/save-money-and-energy/products-programs/home-energy-efficiency-programs/home-energy-improvementprogram-multifamily.html"
    ]
    
    print("Starting web scraper test...")
    success = test_web_scraper(test_url)
    
    if success:
        print("Web scraper test completed successfully!")
    else:
        print("Web scraper test failed!")
