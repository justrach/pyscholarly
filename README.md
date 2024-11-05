# PyScholarly

An async Python library for scraping Google Scholar profiles using Playwright, with support for proxy rotation and detailed citation tracking.

> **⚠️ Disclaimer**: This project is for academic and research purposes only. Please be mindful of Google Scholar's terms of service and rate limiting. Use responsibly and at your own risk.

## Installation

```bash
pip install pyscholarly
```


## Features

- Async/await support for efficient data fetching
- Proxy support with rotation strategies:
  - Sequential rotation
  - Random rotation
  - Support for authenticated proxies (username/password)
- Comprehensive citation metrics:
  - All-time citations
  - Recent citations (last 5 years)
  - Year-to-date citations per publication
  - H-index and i10-index (all-time and recent)
- Publication details:
  - Title, authors, venue, year
  - Citation counts (all-time and YTD)
- Debug logging and HTML page saving for troubleshooting
- Headless mode support
- Modern Playwright-based scraping

## Usage

### Basic Usage

```python
from pyscholarly import fetch_scholar_data
import asyncio

async def main():
    # Fetch data for a Google Scholar profile
    author_id = "SCHOLAR_ID"  # Replace with actual Google Scholar ID
    data = await fetch_scholar_data(author_id)
    
    print(f"Author: {data['name']}")
    print(f"Total citations: {data['citedby']}")
    print(f"Recent citations: {data['citedby_recent']}")
    print(f"h-index: {data['hindex']}")
    
    # Print publications with YTD citations
    print("\nPublications:")
    for pub in data['publications']:
        print(f"- {pub['bib']['title']} ({pub['year']}):")
        print(f"  - Total citations: {pub['num_citations']}")
        print(f"  - YTD citations: {pub['ytd_citations']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage with Proxies

```python
import logging
from pyscholarly import fetch_scholar_data

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    # Single proxy
    proxy = "username:password@host:port"
    
    # Or multiple proxies
    proxies = [
        "username1:password1@host1:port1",
        "username2:password2@host2:port2"
    ]
    
    data = await fetch_scholar_data(
        scholar_id="SCHOLAR_ID",
        proxies=proxies,
        proxy_rotation="random",  # or "sequential"
        headless=True,
        logger=logger
    )
```

## Return Data Structure

```python
{
    'name': str,
    'citedby': int,              # All-time citations
    'citedby_recent': int,       # Citations in last 5 years
    'hindex': int,               # All-time h-index
    'hindex_recent': int,        # Recent h-index
    'i10index': int,             # All-time i10-index
    'i10index_recent': int,      # Recent i10-index
    'publications': [
        {
            'bib': {
                'title': str,
                'authors': str,
                'venue': str
            },
            'num_citations': int,    # Total citations
            'ytd_citations': int,    # Year-to-date citations
            'year': str
        },
        # ...
    ]
}
```

## Configuration Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `scholar_id` | str | Google Scholar profile ID |
| `proxies` | Optional[Union[str, List[str]]] | Single proxy or list of proxies |
| `proxy_rotation` | str | Proxy rotation strategy ('sequential' or 'random') |
| `headless` | bool | Run browser in headless mode |
| `logger` | Optional[Logger] | Custom logger instance |

## Requirements

- Python 3.8+
- Playwright

## Debug Mode

The library saves HTML pages for debugging purposes in a `debug_pages` directory when running with a logger at DEBUG level.

## License

This project is licensed under the MIT License - see the LICENSE file for details.