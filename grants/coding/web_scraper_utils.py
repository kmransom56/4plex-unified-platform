"""
Web scraping utilities for grant research.
This module provides enhanced functionality for scraping grant information from websites,
including handling dynamic content and PDF extraction.
"""

import os
import re
import time
import tempfile
import requests
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
import pdfminer.high_level
from playwright.sync_api import sync_playwright, Page, Browser

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('web_scraper_utils')

class EnhancedWebScraper:
    """Enhanced web scraper with specialized functions for grant information extraction."""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize the web scraper.
        
        Args:
            headless: Whether to run the browser in headless mode
            timeout: Page navigation timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.page = None
        self.temp_dir = tempfile.mkdtemp(prefix="grant_research_")
        
    def __enter__(self):
        """Context manager entry point."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()
        
    def start(self):
        """Start the browser session."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.page.set_default_navigation_timeout(self.timeout)
        
        # Set up download handling
        self.page.on("download", self._handle_download)
        
        return self
        
    def close(self):
        """Close the browser session."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
    def _handle_download(self, download):
        """Handle file downloads."""
        download_path = os.path.join(self.temp_dir, download.suggested_filename)
        download.save_as(download_path)
        print(f"Downloaded file: {download_path}")
        return download_path
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL with retry logic and fallback to requests.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        max_retries = 3
        retry_delay = 2
        
        # Try with Playwright first
        for attempt in range(max_retries):
            try:
                logger.info(f"Playwright navigation attempt {attempt + 1} to {url}")
                response = self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                if response and response.ok:
                    # Wait a bit more for any dynamic content
                    self.page.wait_for_timeout(2000)
                    logger.info(f"Successfully navigated to {url} with Playwright")
                    return True
                    
                if attempt < max_retries - 1:
                    logger.warning(f"Navigation attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
            except Exception as e:
                logger.error(f"Error navigating to {url} with Playwright: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        # If Playwright navigation failed, try with requests as fallback
        logger.warning(f"Failed to navigate to {url} with Playwright after {max_retries} attempts. Trying with requests...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # If requests succeeded, set the content in the page
                logger.info(f"Successfully fetched {url} with requests")
                self.page.set_content(response.text)
                return True
            else:
                logger.error(f"Failed to fetch {url} with requests. Status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error fetching {url} with requests: {str(e)}")
            return False
    
    def extract_page_content(self) -> str:
        """
        Extract the visible text content from the current page.
        
        Returns:
            str: The visible text content
        """
        # Get the page content
        content = self.page.content()
        
        # Parse with BeautifulSoup for better text extraction
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        return text
    
    def find_pdf_links(self) -> List[Dict[str, str]]:
        """
        Find PDF links on the current page.
        
        Returns:
            List[Dict[str, str]]: List of dictionaries with 'url' and 'text' keys
        """
        # Get all links on the page
        links = self.page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.map(link => {
                    return {
                        url: link.href,
                        text: link.textContent.trim()
                    };
                });
            }
        """)
        
        # Filter for PDF links
        pdf_links = [
            link for link in links 
            if link['url'] and (
                link['url'].lower().endswith('.pdf') or 
                'pdf' in link['url'].lower() or
                'application/pdf' in link.get('type', '').lower()
            )
        ]
        
        # Add base URL to relative links
        current_url = self.page.url
        for link in pdf_links:
            if not link['url'].startswith(('http://', 'https://')):
                link['url'] = urljoin(current_url, link['url'])
                
        return pdf_links
    
    def download_pdf(self, url: str) -> Optional[str]:
        """
        Download a PDF file.
        
        Args:
            url: URL of the PDF to download
            
        Returns:
            Optional[str]: Path to the downloaded file or None if download failed
        """
        try:
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Ensure filename is valid and has .pdf extension
            if not filename or not filename.strip():
                filename = f"document_{int(time.time())}.pdf"
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
                
            # Create file path
            file_path = os.path.join(self.temp_dir, filename)
            
            # Download the file
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"Downloaded PDF: {file_path}")
            return file_path
        except Exception as e:
            print(f"Error downloading PDF from {url}: {str(e)}")
            return None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            with open(pdf_path, 'rb') as f:
                text = pdfminer.high_level.extract_text(f)
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return ""
    
    def extract_grant_information(self, page_content: str) -> Dict[str, Any]:
        """
        Extract grant information from page content using pattern matching.
        
        Args:
            page_content: The page content to extract information from
            
        Returns:
            Dict[str, Any]: Extracted grant information
        """
        # Initialize result dictionary
        grant_info = {
            'programs': [],
            'general_info': {}
        }
        
        # Look for grant program names
        program_patterns = [
            r'(?i)(?:grant|program|initiative|fund)s?\s+(?:called|named|titled)?\s+"([^"]+)"',
            r'(?i)(?:grant|program|initiative|fund)s?:?\s+([A-Z][A-Za-z0-9\s\-]+(?:\([^)]+\))?)',
            r'(?i)The\s+([A-Z][A-Za-z0-9\s\-]+(?:\([^)]+\))?)\s+(?:grant|program|initiative|fund)s?'
        ]
        
        for pattern in program_patterns:
            matches = re.finditer(pattern, page_content)
            for match in matches:
                program_name = match.group(1).strip()
                if program_name and len(program_name) > 3 and len(program_name) < 100:
                    # Look for description near the program name
                    context = page_content[max(0, match.start() - 200):min(len(page_content), match.end() + 500)]
                    
                    # Extract potential description
                    desc_match = re.search(r'(?i)(?:description|overview|summary|about)s?:?\s+([^.]+(?:\.[^.]+){0,3})', context)
                    description = desc_match.group(1).strip() if desc_match else ""
                    
                    # Extract potential eligibility
                    elig_match = re.search(r'(?i)(?:eligibility|eligible|qualify|qualifications?):?\s+([^.]+(?:\.[^.]+){0,3})', context)
                    eligibility = elig_match.group(1).strip() if elig_match else ""
                    
                    # Extract potential funding amounts
                    funding_match = re.search(r'(?i)(?:funding|amount|award|grant size):?\s+([^.]+(?:\.[^.]+){0,2})', context)
                    funding = funding_match.group(1).strip() if funding_match else ""
                    
                    # Extract potential deadlines
                    deadline_match = re.search(r'(?i)(?:deadline|due date|application period|applications due):?\s+([^.]+)', context)
                    deadline = deadline_match.group(1).strip() if deadline_match else ""
                    
                    # Extract potential contact info
                    contact_match = re.search(r'(?i)(?:contact|for more information|questions):?\s+([^.]+(?:\.[^.]+){0,2})', context)
                    contact = contact_match.group(1).strip() if contact_match else ""
                    
                    # Add to programs list if not already present
                    if not any(p.get('name') == program_name for p in grant_info['programs']):
                        grant_info['programs'].append({
                            'name': program_name,
                            'description': description,
                            'eligibility': eligibility,
                            'funding': funding,
                            'deadline': deadline,
                            'contact': contact
                        })
        
        # Look for general eligibility information
        eligibility_match = re.search(r'(?i)(?:eligibility|who can apply|requirements):?\s+([^.]+(?:\.[^.]+){0,5})', page_content)
        if eligibility_match:
            grant_info['general_info']['eligibility'] = eligibility_match.group(1).strip()
            
        # Look for application process
        application_match = re.search(r'(?i)(?:how to apply|application process):?\s+([^.]+(?:\.[^.]+){0,5})', page_content)
        if application_match:
            grant_info['general_info']['application_process'] = application_match.group(1).strip()
            
        # Look for contact information
        contact_match = re.search(r'(?i)(?:contact|for more information):?\s+([^.]+(?:\.[^.]+){0,3})', page_content)
        if contact_match:
            grant_info['general_info']['contact'] = contact_match.group(1).strip()
            
        return grant_info
    
    def scrape_grant_information(self, url: str) -> Dict[str, Any]:
        """
        Scrape grant information from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dict[str, Any]: Scraped grant information
        """
        result = {
            'url': url,
            'success': False,
            'page_content': '',
            'pdf_content': [],
            'extracted_info': {
                'programs': [],
                'general_info': {}
            }
        }
        
        # Navigate to the URL
        if not self.navigate(url):
            return result
            
        # Extract page content
        page_content = self.extract_page_content()
        result['page_content'] = page_content
        result['success'] = True
        
        # Extract grant information from page content
        result['extracted_info'] = self.extract_grant_information(page_content)
        
        # Find and download PDF links
        pdf_links = self.find_pdf_links()
        for pdf_link in pdf_links[:5]:  # Limit to first 5 PDFs
            pdf_url = pdf_link['url']
            pdf_path = self.download_pdf(pdf_url)
            
            if pdf_path:
                pdf_text = self.extract_text_from_pdf(pdf_path)
                if pdf_text:
                    pdf_info = {
                        'url': pdf_url,
                        'text': pdf_text[:10000],  # Limit text size
                        'extracted_info': self.extract_grant_information(pdf_text)
                    }
                    result['pdf_content'].append(pdf_info)
                    
                    # Merge PDF extracted info with main extracted info
                    for program in pdf_info['extracted_info']['programs']:
                        if not any(p.get('name') == program['name'] for p in result['extracted_info']['programs']):
                            result['extracted_info']['programs'].append(program)
        
        return result

def scrape_grants(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Scrape grant information from a list of URLs.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List[Dict[str, Any]]: List of scraped grant information
    """
    results = []
    
    # First try with the enhanced web scraper
    try:
        logger.info(f"Starting web scraping with EnhancedWebScraper for {len(urls)} URLs")
        with EnhancedWebScraper(headless=True) as scraper:
            for url in urls:
                try:
                    logger.info(f"Scraping {url}...")
                    result = scraper.scrape_grant_information(url)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    results.append({
                        'url': url,
                        'success': False,
                        'error': str(e)
                    })
    except Exception as e:
        logger.error(f"Error initializing EnhancedWebScraper: {str(e)}")
        
        # Fallback to simple requests-based scraping if Playwright fails completely
        logger.info("Falling back to simple requests-based scraping")
        for url in urls:
            try:
                logger.info(f"Scraping {url} with requests fallback...")
                result = fallback_scrape_url(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {url} with fallback method: {str(e)}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
    
    return results


def fallback_scrape_url(url: str) -> Dict[str, Any]:
    """
    Fallback method to scrape a URL using requests and BeautifulSoup.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dict[str, Any]: Scraped information
    """
    result = {
        'url': url,
        'success': False,
        'page_content': '',
        'pdf_content': [],
        'extracted_info': {
            'programs': [],
            'general_info': {}
        }
    }
    
    try:
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {url}. Status code: {response.status_code}")
            result['error'] = f"HTTP error: {response.status_code}"
            return result
            
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        result['page_content'] = text
        result['success'] = True
        
        # Extract grant information
        extractor = EnhancedInfoExtractor()
        result['extracted_info'] = extractor.extract_grant_information(text)
        
        # Find PDF links
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf') or 'pdf' in href.lower():
                # Make relative URLs absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)
                    
                pdf_links.append({
                    'url': href,
                    'text': link.get_text(strip=True)
                })
                
        # Download and process PDFs (limit to first 3)
        temp_dir = tempfile.mkdtemp(prefix="grant_research_fallback_")
        for pdf_link in pdf_links[:3]:
            try:
                pdf_url = pdf_link['url']
                logger.info(f"Downloading PDF: {pdf_url}")
                
                # Extract filename from URL
                parsed_url = urlparse(pdf_url)
                filename = os.path.basename(parsed_url.path)
                
                # Ensure filename is valid and has .pdf extension
                if not filename or not filename.strip():
                    filename = f"document_{int(time.time())}.pdf"
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
                    
                # Create file path
                file_path = os.path.join(temp_dir, filename)
                
                # Download the file
                pdf_response = requests.get(pdf_url, headers=headers, timeout=30)
                pdf_response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in pdf_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                # Extract text from PDF
                with open(file_path, 'rb') as f:
                    pdf_text = pdfminer.high_level.extract_text(f)
                    
                if pdf_text:
                    pdf_info = {
                        'url': pdf_url,
                        'text': pdf_text[:10000],  # Limit text size
                        'extracted_info': extractor.extract_grant_information(pdf_text)
                    }
                    result['pdf_content'].append(pdf_info)
                    
                    # Merge PDF extracted info with main extracted info
                    for program in pdf_info['extracted_info']['programs']:
                        if not any(p.get('name') == program['name'] for p in result['extracted_info']['programs']):
                            result['extracted_info']['programs'].append(program)
            except Exception as e:
                logger.error(f"Error processing PDF {pdf_link['url']}: {str(e)}")
                
        return result
    except Exception as e:
        logger.error(f"Error in fallback_scrape_url for {url}: {str(e)}")
        result['error'] = str(e)
        return result


class EnhancedInfoExtractor:
    """Helper class to extract grant information from text."""
    
    def extract_grant_information(self, text: str) -> Dict[str, Any]:
        """Extract grant information from text using pattern matching."""
        # Initialize result dictionary
        grant_info = {
            'programs': [],
            'general_info': {}
        }
        
        # Look for grant program names
        program_patterns = [
            r'(?i)(?:grant|program|initiative|fund)s?\s+(?:called|named|titled)?\s+"([^"]+)"',
            r'(?i)(?:grant|program|initiative|fund)s?:?\s+([A-Z][A-Za-z0-9\s\-]+(?:\([^)]+\))?)',
            r'(?i)The\s+([A-Z][A-Za-z0-9\s\-]+(?:\([^)]+\))?)\s+(?:grant|program|initiative|fund)s?'
        ]
        
        for pattern in program_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                program_name = match.group(1).strip()
                if program_name and len(program_name) > 3 and len(program_name) < 100:
                    # Look for description near the program name
                    context = text[max(0, match.start() - 200):min(len(text), match.end() + 500)]
                    
                    # Extract potential description
                    desc_match = re.search(r'(?i)(?:description|overview|summary|about)s?:?\s+([^.]+(?:\.[^.]+){0,3})', context)
                    description = desc_match.group(1).strip() if desc_match else ""
                    
                    # Extract potential eligibility
                    elig_match = re.search(r'(?i)(?:eligibility|eligible|qualify|qualifications?):?\s+([^.]+(?:\.[^.]+){0,3})', context)
                    eligibility = elig_match.group(1).strip() if elig_match else ""
                    
                    # Extract potential funding amounts
                    funding_match = re.search(r'(?i)(?:funding|amount|award|grant size):?\s+([^.]+(?:\.[^.]+){0,2})', context)
                    funding = funding_match.group(1).strip() if funding_match else ""
                    
                    # Extract potential deadlines
                    deadline_match = re.search(r'(?i)(?:deadline|due date|application period|applications due):?\s+([^.]+)', context)
                    deadline = deadline_match.group(1).strip() if deadline_match else ""
                    
                    # Extract potential contact info
                    contact_match = re.search(r'(?i)(?:contact|for more information|questions):?\s+([^.]+(?:\.[^.]+){0,2})', context)
                    contact = contact_match.group(1).strip() if contact_match else ""
                    
                    # Add to programs list if not already present
                    if not any(p.get('name') == program_name for p in grant_info['programs']):
                        grant_info['programs'].append({
                            'name': program_name,
                            'description': description,
                            'eligibility': eligibility,
                            'funding': funding,
                            'deadline': deadline,
                            'contact': contact
                        })
        
        # Look for general eligibility information
        eligibility_match = re.search(r'(?i)(?:eligibility|who can apply|requirements):?\s+([^.]+(?:\.[^.]+){0,5})', text)
        if eligibility_match:
            grant_info['general_info']['eligibility'] = eligibility_match.group(1).strip()
            
        # Look for application process
        application_match = re.search(r'(?i)(?:how to apply|application process):?\s+([^.]+(?:\.[^.]+){0,5})', text)
        if application_match:
            grant_info['general_info']['application_process'] = application_match.group(1).strip()
            
        # Look for contact information
        contact_match = re.search(r'(?i)(?:contact|for more information):?\s+([^.]+(?:\.[^.]+){0,3})', text)
        if contact_match:
            grant_info['general_info']['contact'] = contact_match.group(1).strip()
            
        return grant_info

def format_grant_results(results: List[Dict[str, Any]]) -> str:
    """
    Format grant scraping results into a readable format.
    
    Args:
        results: List of scraped grant information
        
    Returns:
        str: Formatted results
    """
    output = []
    
    for result in results:
        url = result['url']
        domain = urlparse(url).netloc
        
        output.append(f"## Source: {domain}")
        output.append(f"URL: {url}")
        
        if not result['success']:
            output.append("**Error:** Failed to scrape this website.")
            if 'error' in result:
                output.append(f"Error details: {result['error']}")
            output.append("")
            continue
            
        # Add programs information
        programs = result['extracted_info']['programs']
        if programs:
            output.append("\n### Grant Programs Found:")
            
            for program in programs:
                output.append(f"\n#### {program['name']}")
                
                if program.get('description'):
                    output.append(f"**Description:** {program['description']}")
                    
                if program.get('eligibility'):
                    output.append(f"**Eligibility:** {program['eligibility']}")
                    
                if program.get('funding'):
                    output.append(f"**Funding:** {program['funding']}")
                    
                if program.get('deadline'):
                    output.append(f"**Deadline:** {program['deadline']}")
                    
                if program.get('contact'):
                    output.append(f"**Contact:** {program['contact']}")
        else:
            output.append("\nNo specific grant programs identified.")
            
        # Add general information
        general_info = result['extracted_info']['general_info']
        if general_info:
            output.append("\n### General Information:")
            
            for key, value in general_info.items():
                output.append(f"**{key.replace('_', ' ').title()}:** {value}")
                
        # Add PDF information
        pdf_content = result.get('pdf_content', [])
        if pdf_content:
            output.append(f"\n### PDFs Found ({len(pdf_content)}):")
            for i, pdf in enumerate(pdf_content, 1):
                output.append(f"\n#### PDF {i}: {urlparse(pdf['url']).path.split('/')[-1]}")
                
                pdf_programs = pdf['extracted_info']['programs']
                if pdf_programs:
                    output.append("**Programs mentioned in PDF:**")
                    for program in pdf_programs:
                        output.append(f"- {program['name']}")
                        
        output.append("\n" + "-" * 80 + "\n")
        
    return "\n".join(output)

if __name__ == "__main__":
    # Example usage
    test_urls = [
        "https://www.energy.gov/eere/solar/solar-financing-multifamily-affordable-housing",
    ]
    
    results = scrape_grants(test_urls)
    formatted_output = format_grant_results(results)
    print(formatted_output)
