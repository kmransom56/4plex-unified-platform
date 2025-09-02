from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import json
import re
import os
import sys
import time
from typing import List, Dict, Any
from urllib.parse import urlparse

# Add the coding directory to the path so we can import the web_scraper_utils module
sys.path.append(os.path.join(os.path.dirname(__file__), 'coding'))

# Import the enhanced web scraper (will be used by the WebScraper agent)
try:
    from web_scraper_utils import scrape_grants, format_grant_results
except ImportError:
    print("Error: web_scraper_utils module not found. Make sure it exists in the 'coding' directory.")

# 1. Configure LLM (Replace with your actual configuration)
#llm_config = {
#   "config_list": [
#      {
#          "model": "gpt-4-turbo-preview",  # Or your preferred model
#          "api_key": "YOUR_OPENAI_API_KEY",  # Replace with your actual API key
#     }
#  ],
#  "seed": 42,
#}

#If using Ollama:
llm_config = {
    "config_list": [
        {
           "model": "deepseek-coder:6.7b",
           "base_url": "http://localhost:11434",
           "api_type": "ollama",
        }
    ],
    "seed": 42,
    "temperature": 0.7,  # Adding temperature for more focused responses
    "timeout": 120,     # Increasing timeout for complex responses
}


# 2. Define the Code Executor Agent with environment configuration
code_executor = UserProxyAgent(
    name="CodeExecutor",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,  # Increased to allow for multiple code executions
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # Don't use Docker to avoid environment issues
        "last_n_messages": 3,  # Only look at the last 3 messages for code execution
        "timeout": 60,  # 60 second timeout for code execution
    },
)


# 3. Define the Web Scraping Tool Agent (using enhanced web_scraper_utils)
web_scraper = AssistantAgent(
    name="WebScraper",
    llm_config=llm_config,
    system_message="""You are a helpful AI web scraping tool specialized in extracting grant information.
        You are given URLs and instructions on what information to extract.
        Your goal is to extract grant information using the enhanced web_scraper_utils module.
        
        IMPORTANT: All required packages are ALREADY INSTALLED in the virtual environment. DO NOT attempt to install any packages.
        
        You will use the following functions from the web_scraper_utils module:
        1. scrape_grants(urls): Takes a list of URLs and returns detailed grant information
        2. format_grant_results(results): Formats the results into a readable format
        
        The scrape_grants function handles:
        - Navigating to the URLs with retry logic
        - Extracting text content from web pages
        - Finding and downloading PDF files
        - Extracting text from PDFs
        - Parsing grant information including:
            - Grant program names
            - Descriptions
            - Eligibility criteria
            - Funding amounts
            - Application deadlines
            - Contact information
            
        When asked to scrape URLs, write Python code that:
        1. Imports the necessary functions from web_scraper_utils
        2. Calls scrape_grants with the list of URLs
        3. Formats the results using format_grant_results
        4. Returns the formatted results
        
        Process URLs in small batches of 3-5 at a time to avoid overwhelming the system.
        Focus on the most relevant URLs first - prioritize Georgia-specific and Brookhaven/DeKalb County resources.
        
        If you encounter any errors, provide detailed error information and troubleshooting steps.
        If you cannot extract information from a particular URL, you'll still get partial results for other URLs.
        """,
    human_input_mode="NEVER",
)


# 4. Define the Grant Research Agent (Orchestrator)
grant_researcher = AssistantAgent(
    name="GrantResearcher",
    llm_config=llm_config,
    system_message="""You are a helpful AI research assistant specializing in finding grant opportunities in Brookhaven, Georgia (DeKalb County).
        Your goal is to research the provided websites and identify grants available in Brookhaven, Georgia (DeKalb County) for renovating small multifamily properties and for adopting clean energy during renovations.
         Look into foundation grants that support community development, affordable housing, or environmental sustainability in the DeKalb County area.
         Research any local initiatives or partnerships that might offer grants or low-interest loans for property improvements
        
        You coordinate with the WebScraper agent to gather information from websites, including linked PDF files.  You will provide the WebScraper with a list of URLs to investigate.  You will then analyze the information returned by the WebScraper.
        
        You should carefully read the content extracted by the WebScraper and compile a well-organized summary of potential grant opportunities, clearly indicating the source website for each grant.  Your final output should be in a table format.
        
        You are responsible for:
        - Grant names
        - Brief descriptions of the grant programs
        - Eligibility criteria (specifically for location and property type)
        - Funding amounts or ranges
        - Application deadlines (if available)
        - Contact information or links for further details
        
        You will compile the findings into a table with columns: Source, Program/Incentive Name, Description, Eligibility Criteria, Funding, Deadlines, Contact Information.
        
        If the WebScraper returns "INFORMATION NOT FOUND", you acknowledge that and move on to the next URL.""",
    human_input_mode="NEVER",
)

# 5. Define the User Proxy Agent
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # Don't use Docker to avoid environment issues
        "last_n_messages": 3,  # Only look at the last 3 messages for code execution
        "timeout": 60,  # 60 second timeout for code execution
    },
    system_message="""You are the user proxy agent helping to research grant opportunities.
    IMPORTANT: All required packages are ALREADY INSTALLED in the virtual environment. DO NOT attempt to install any packages.
    When executing code, make sure to handle errors gracefully and provide helpful feedback.
    """,
)

# 6. Import updated county-specific URLs
from updated_research_urls import UPDATED_URLS_TO_RESEARCH, get_priority_urls, COUNTY_SPECIFIC_URLS

# Define the comprehensive list of URLs to research (all 5 target counties)
urls_to_research = UPDATED_URLS_TO_RESEARCH

# 7. Initial message to trigger the research - Updated for 5-county focus
initial_message = f"""Research the following websites for grant opportunities across Fulton, DeKalb, Clayton, Cobb Counties and Atlanta, Georgia for 4-plex and small multifamily property renovations and clean energy upgrades.

TARGET COUNTIES: Fulton, DeKalb, Clayton, Cobb, Atlanta
PROPERTY FOCUS: 4-plex, duplex, triplex, and small multifamily (2-4 units)
RENOVATION FOCUS: Property rehabilitation, clean energy installations, weatherization

IMPORTANT INSTRUCTIONS:
1. DO NOT attempt to install any packages - all required packages are already installed in the virtual environment.
2. Process URLs in small batches of 3-5 at a time to avoid overwhelming the system.
3. Prioritize county-specific resources first, then state and federal programs.

Use the enhanced web scraping functionality in the web_scraper_utils module to:
1. Extract grant information from the websites
2. Download and analyze any relevant PDF files
3. Parse out grant names, descriptions, eligibility criteria, funding amounts, deadlines, and contact information

Focus on grants that are applicable to:
- 4-plex and small multifamily properties (2-4 units)
- Property rehabilitation and renovation projects
- Clean energy installations (solar, HVAC, insulation)
- Properties located in Fulton, DeKalb, Clayton, Cobb Counties, or Atlanta

The final output should be a well-organized summary of potential grant opportunities, clearly indicating:
- Source website and agency
- County/jurisdiction coverage
- Property type eligibility
- Funding amounts and limits
- Application deadlines
- Contact information

PRIORITY RESEARCH ORDER:
1. Fulton County and Atlanta city programs
2. DeKalb County programs (including Brookhaven)
3. Cobb County and municipal programs
4. Clayton County programs
5. Georgia state-wide programs
6. Federal programs and incentives

Here are the priority URLs to research first:
{get_priority_urls(15)}

Complete URL list for comprehensive research:
{urls_to_research}
"""


# 8. Function to run a test of the web scraper directly
def test_web_scraper(test_url):
    """Run a test of the web scraper with a single URL"""
    print(f"\n--- Testing Web Scraper with URL: {test_url} ---")
    try:
        from coding.web_scraper_utils import scrape_grants, format_grant_results
        results = scrape_grants([test_url])
        formatted_output = format_grant_results(results)
        print(formatted_output)
        return True
    except Exception as e:
        print(f"Error testing web scraper: {str(e)}")
        return False

# Uncomment to test the web scraper directly with a single URL
# test_web_scraper("https://www.energy.gov/eere/solar/solar-financing-multifamily-affordable-housing")

# 9. Initiate the chat
print("\n--- Starting Grant Research ---")
user_proxy.initiate_chat(
    grant_researcher,
    message=initial_message,
)


# 10. Export Agent Configurations to JSON (for AutoGen Studio)
def export_agent_configs():
    """Export agent configurations to JSON for AutoGen Studio"""
    grant_researcher_config_for_export = grant_researcher.config
    user_proxy_config_for_export = user_proxy.config
    web_scraper_config_for_export = web_scraper.config
    code_executor_config_for_export = code_executor.config

    agent_configs_for_studio = {
        "grant_researcher": grant_researcher_config_for_export,
        "user_proxy": user_proxy_config_for_export,
        "web_scraper": web_scraper_config_for_export,
        "code_executor": code_executor_config_for_export,
    }

    json_output = json.dumps(agent_configs_for_studio, indent=4)

    print("\n--- JSON Configuration for AutoGen Studio ---")
    print(json_output)
    
    # Save to file
    with open("agent_configs.json", "w") as f:
        f.write(json_output)
    print(f"Agent configurations saved to agent_configs.json")

# Uncomment to export agent configurations
# export_agent_configs()