# Grant Research System

This system helps research grant opportunities in Brookhaven, Georgia (DeKalb County) for renovating small multifamily properties and adopting clean energy during renovations.

## Features

- **Multi-Agent System**: Uses AutoGen to create a collaborative agent system for grant research
- **Enhanced Web Scraping**: Robust web scraping with Playwright and fallback mechanisms
- **PDF Processing**: Automatically extracts and analyzes text from PDF documents
- **Pattern Matching**: Identifies grant programs, eligibility criteria, funding amounts, and deadlines
- **Structured Output**: Organizes findings into a readable format

## Setup

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

## Usage

### Running the main research script

```bash
python research_agents.py
```

This will:
1. Initialize the agent system
2. Scrape the configured websites for grant information
3. Extract and analyze the content
4. Present the findings in a structured format

### Testing the web scraper directly

```bash
python coding/test_scraper.py
```

## Components

- `research_agents.py`: Main script that sets up and runs the agent system
- `coding/web_scraper_utils.py`: Enhanced web scraping utilities
- `coding/test_scraper.py`: Test script for the web scraper
- `requirements.txt`: Dependencies for the project

## Customization

To customize the research targets:
1. Edit the `urls_to_research` list in `research_agents.py`
2. Modify the initial message to focus on specific grant types or criteria

## Troubleshooting

- If web scraping fails, the system will automatically try fallback methods
- For timeout issues, try increasing the timeout value in `web_scraper_utils.py`
- If Playwright has issues, ensure browsers are installed with `playwright install`

## License

This project is for personal use only.
