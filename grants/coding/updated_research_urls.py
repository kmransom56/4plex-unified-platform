"""
Updated county-specific grant research URLs for 4-Plex Unified Platform
Aligned with target counties: Fulton, DeKalb, Clayton, Cobb, Atlanta
"""

# County-specific URL mapping for comprehensive grant research
COUNTY_SPECIFIC_URLS = {
    
    "fulton": [
        # Fulton County Government Resources
        "https://www.fultoncountyga.gov/services/community-development/housing/affordable-housing",
        "https://www.fultoncountyga.gov/services/community-development/cdbg",
        "https://www.fultoncountyga.gov/services/community-development/home-program",
        "https://www.fultoncountyga.gov/inside-fulton-county/fulton-county-news/articles/2024/housing-trust-fund",
        
        # Atlanta City Programs (within Fulton County)
        "https://www.atlantahousing.org/development/",
        "https://www.atlantahousing.org/property-owners/",
        "https://www.atlantaga.gov/government/mayor-s-office/executive-offices/housing",
        "https://www.atlantaga.gov/government/departments/planning/office-of-housing/affordable-housing-programs",
        "https://www.atlantaga.gov/home/showpublisheddocument/56021/637829142166970000",  # Housing Trust Fund
    ],
    
    "dekalb": [
        # DeKalb County Government Resources
        "https://www.dekalbcountyga.gov/community-development/community-development-block-grant-cdbg",
        "https://www.dekalbcountyga.gov/human-development/grants-and-administration",
        "https://www.dekalbcountyga.gov/community-development/home-program",
        "https://www.dekalbcountyga.gov/community-development/neighborhood-stabilization-program",
        
        # Brookhaven (DeKalb County)
        "https://www.brookhavenga.gov/1304/Economic-Development",
        "https://www.brookhavenga.gov/678/Housing",
        
        # Other DeKalb municipalities
        "https://www.dekaturga.com/departments/community-development/housing",
        "https://www.dunwooduga.gov/your-government/departments/community-development",
    ],
    
    "clayton": [
        # Clayton County Government Resources
        "https://www.claytoncountyga.gov/community-development",
        "https://www.claytoncountyga.gov/housing-authority",
        "https://www.claytoncountyga.gov/grants",
        "https://www.claytoncountyga.gov/departments/community-services/community-development",
        
        # Clayton municipalities
        "https://www.forestparkga.gov/departments/community-development",
        "https://www.jonesboroga.com/departments/community-development",
    ],
    
    "cobb": [
        # Cobb County Government Resources
        "https://www.cobbcounty.org/public-safety/community-development/housing",
        "https://www.cobbcounty.org/public-safety/community-development/cdbg",
        "https://www.cobbcounty.org/public-safety/community-development/home-program",
        "https://www.cobbcounty.org/central-services/community-services/grants-and-community-programs",
        
        # Cobb municipalities
        "https://mariettaga.gov/departments/community-development",
        "https://www.smyrnaga.gov/departments/community-development",
        "https://www.kennesawga.gov/departments/community-development",
    ],
    
    "georgia_state": [
        # Georgia State Programs (all counties)
        "https://dca.georgia.gov/financing-tools/infrastructure/community-development-block-grants-cdbg",
        "https://dca.georgia.gov/affordable-housing/housing-development/home-investment-partnership-program-home",
        "https://dca.georgia.gov/affordable-housing/rental-assistance/georgia-rental-assistance-program-grap",
        "https://gefa.georgia.gov/weatherization-assistance-program",
        "https://energyrebates.georgia.gov/",
        "https://www.georgiapower.com/residential/save-money-and-energy/products-programs/home-energy-efficiency-programs/home-energy-improvementprogram-multifamily.html",
        "https://www.georgiasaves.org/rebates",
    ],
    
    "federal": [
        # Federal Programs (all locations)
        "https://www.energy.gov/communitysolar/multifamily-affordable-housing-collaborative",
        "https://www.energy.gov/eere/solar/articles/multifamily-affordable-housing-collaborative-fact-sheet",
        "https://www.epa.gov/inflation-reduction-act/solar-all",
        "https://home.treasury.gov/news/featured-stories/the-inflation-reduction-act-benefits-for-builders-of-multifamily-housing",
        "https://www.hudexchange.info/programs/renewable-energy/",
        "https://www.energystar.gov/buildings/resources_topic/multifamily_housing",
        "https://www.irs.gov/credits-deductions/residential-clean-energy-credit",
        "https://www.novoco.com/resource-centers/renewable-energy-tax-credits",
    ],
    
    "solar_energy": [
        # Georgia Solar Incentives (all counties)
        "https://www.energysage.com/local-data/solar-rebates-incentives/ga/",
        "https://palmetto.com/policy/georgia-solar-incentives",
        "https://www.forbes.com/home-improvement/solar/georgia-solar-incentives/",
        "https://renewableenergyrebates.org/solar-incentives-and-rebates/georgia",
        "https://www.dsireusa.org/",
        "https://goodcapitalfund.org/georgia-bright",
    ],
    
    "nonprofits": [
        # Nonprofit and Foundation Grants
        "https://gridalternatives.org/what-we-do/multifamily",
        "https://www.michaelsorg.com/solar",
        "https://bquetfoundation.org/",
        "https://www.centerforsustainableenergy.org/",
        "https://homepropertygrants.com/2025/05/home-repair-grants-georgia.html",
        "https://nationalhousingtrust.org/sites/default/files/documents/Solar-for-All-Program-Tracker-9-6_0.pdf",
        "https://nationalhousingtrust.org/sites/default/files/documents/Solar-for-All-State-Funding-Tracker-4-30.pdf",
    ]
}

# Priority research order for 4-plex focused analysis
PRIORITY_ORDER = [
    "fulton",      # Highest property values, most opportunities
    "dekalb",      # Existing research base (Brookhaven)
    "cobb",        # Strong suburban multifamily market
    "clayton",     # Emerging market, lower barriers
    "georgia_state",  # State-wide programs
    "federal",     # Federal programs
    "solar_energy",   # Clean energy focus
    "nonprofits"   # Foundation grants
]

# Generate comprehensive URL list for updated research
def get_all_urls():
    """Return all URLs in priority order"""
    all_urls = []
    for category in PRIORITY_ORDER:
        all_urls.extend(COUNTY_SPECIFIC_URLS[category])
    return all_urls

def get_county_urls(county: str):
    """Get URLs for specific county"""
    county_lower = county.lower()
    if county_lower in COUNTY_SPECIFIC_URLS:
        return COUNTY_SPECIFIC_URLS[county_lower]
    return []

def get_priority_urls(top_n: int = 20):
    """Get top N priority URLs for initial research"""
    priority_urls = []
    for category in PRIORITY_ORDER[:4]:  # Focus on county-specific first
        priority_urls.extend(COUNTY_SPECIFIC_URLS[category][:3])  # Top 3 from each
        if len(priority_urls) >= top_n:
            break
    return priority_urls[:top_n]

# Updated URL list for research_agents.py
UPDATED_URLS_TO_RESEARCH = get_all_urls()

# County-specific initial messages
COUNTY_MESSAGES = {
    "fulton": """Research grant opportunities in Fulton County, Georgia for 4-plex and small multifamily property renovations and clean energy upgrades. Focus on:
- Atlanta Housing Authority programs
- Fulton County CDBG and HOME programs  
- City of Atlanta housing initiatives
- Property rehabilitation grants
- Energy efficiency incentives""",
    
    "dekalb": """Research grant opportunities in DeKalb County, Georgia for 4-plex and small multifamily property renovations and clean energy upgrades. Focus on:
- Brookhaven economic development programs
- DeKalb County community development grants
- Decatur housing initiatives
- Neighborhood stabilization programs
- Weatherization assistance""",
    
    "clayton": """Research grant opportunities in Clayton County, Georgia for 4-plex and small multifamily property renovations and clean energy upgrades. Focus on:
- Clayton County Housing Authority programs
- Community development block grants
- Emerging neighborhoods initiatives
- First-time investor programs
- Energy efficiency rebates""",
    
    "cobb": """Research grant opportunities in Cobb County, Georgia for 4-plex and small multifamily property renovations and clean energy upgrades. Focus on:
- Marietta housing development programs
- Cobb County CDBG initiatives
- Smyrna/Kennesaw community development
- Suburban multifamily incentives
- Solar installation programs"""
}

if __name__ == "__main__":
    print("Updated Grant Research URLs:")
    print(f"Total URLs: {len(UPDATED_URLS_TO_RESEARCH)}")
    print(f"Priority URLs: {len(get_priority_urls())}")
    print(f"Counties covered: {len([k for k in COUNTY_SPECIFIC_URLS.keys() if k not in ['georgia_state', 'federal', 'solar_energy', 'nonprofits']])}")