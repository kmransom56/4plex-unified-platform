"""
Direct grant research script using the enhanced web scraper.
This script bypasses the AutoGen agents and directly uses the web_scraper_utils module.
"""

import os
import sys
import time
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('direct_research')

# Add the parent directory to the path so we can import the web_scraper_utils module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the enhanced web scraper
try:
    from coding.web_scraper_utils import scrape_grants, format_grant_results
    logger.info("Successfully imported web_scraper_utils module")
except ImportError as e:
    logger.error(f"Error importing web_scraper_utils module: {str(e)}")
    sys.exit(1)

def research_grants(urls: List[str], batch_size: int = 3) -> str:
    """
    Research grant opportunities from a list of URLs.
    
    Args:
        urls: List of URLs to research
        batch_size: Number of URLs to process in each batch
        
    Returns:
        str: Formatted results
    """
    all_results = []
    
    # Process URLs in batches
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} of {(len(urls) + batch_size - 1) // batch_size}: {batch}")
        
        try:
            # Scrape grants from the batch of URLs
            batch_results = scrape_grants(batch)
            all_results.extend(batch_results)
            
            # Log success
            logger.info(f"Successfully processed batch {i//batch_size + 1}")
            
            # Sleep between batches to avoid overwhelming the system
            if i + batch_size < len(urls):
                logger.info("Sleeping for 5 seconds before processing the next batch...")
                time.sleep(5)
        except Exception as e:
            logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
    
    # Format the results
    formatted_results = format_grant_results(all_results)
    
    # Save the results to a file
    with open("grant_research_results.md", "w") as f:
        f.write(formatted_results)
    
    logger.info("Research completed and results saved to grant_research_results.md")
    
    return formatted_results

if __name__ == "__main__":
    # Priority URLs to research first (local and Georgia-specific)
    priority_urls = [
        "https://www.brookhavenga.gov/1304/Economic-Development",
        "https://www.dekalbcountyga.gov/community-development/community-development-block-grant-cdbg",
        "https://www.dekalbcountyga.gov/human-development/grants-and-administration",
        "https://www.georgiapower.com/residential/save-money-and-energy/products-programs/home-energy-efficiency-programs/home-energy-improvementprogram-multifamily.html",
        "https://gefa.georgia.gov/weatherization-assistance-program",
    ]
    
    # Additional Georgia-specific resources
    georgia_urls = [
        "https://goodcapitalfund.org/georgia-bright",
        "https://energyrebates.georgia.gov/",
        "https://dca.georgia.gov/financing-tools/infrastructure/community-development-block-grants-cdbg",
        "https://dca.georgia.gov/affordable-housing/housing-development/home-investment-partnership-program-home",
        "https://dfcs.georgia.gov/services/low-income-home-energy-assistance-program-liheap/weatherization",
        "https://www.energysage.com/local-data/solar-rebates-incentives/ga/",
        "https://palmetto.com/policy/georgia-solar-incentives",
    ]
    
    # Federal resources specifically for multifamily housing
    federal_urls = [
        "https://www.energy.gov/communitysolar/multifamily-affordable-housing-collaborative",
        "https://www.energy.gov/eere/solar/articles/multifamily-affordable-housing-collaborative-fact-sheet",
        "https://www.epa.gov/inflation-reduction-act/solar-all",
        "https://home.treasury.gov/news/featured-stories/the-inflation-reduction-act-benefits-for-builders-of-multifamily-housing",
    ]
    
    print("Starting grant research...")
    print(f"Processing {len(priority_urls)} priority URLs first...")
    
    try:
        # Research priority URLs first
        results = research_grants(priority_urls, batch_size=2)
        
        # Print a summary of the results
        print("\nResearch completed for priority URLs!")
        print("Results saved to grant_research_results.md")
        
        # Ask if the user wants to continue with more URLs
        continue_research = input("\nDo you want to continue research with additional Georgia-specific resources? (y/n): ")
        
        if continue_research.lower() == 'y':
            print(f"\nProcessing {len(georgia_urls)} additional Georgia-specific URLs...")
            results = research_grants(georgia_urls, batch_size=2)
            print("\nResearch completed for Georgia-specific URLs!")
            print("Results saved to grant_research_results.md")
            
            continue_research = input("\nDo you want to continue research with federal resources? (y/n): ")
            
            if continue_research.lower() == 'y':
                print(f"\nProcessing {len(federal_urls)} federal resource URLs...")
                results = research_grants(federal_urls, batch_size=2)
                print("\nResearch completed for federal resource URLs!")
                print("Results saved to grant_research_results.md")
        
        print("\nGrant research completed!")
        
    except Exception as e:
        print(f"Error during research: {str(e)}")
        logger.error(f"Error during research: {str(e)}")
