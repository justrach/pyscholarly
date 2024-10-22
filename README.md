# PyScholarly

An async Python library for scraping Google Scholar profiles using Playwright.

## Installation

```bash
pip install pyscholarly
```

## Usage

```python
from pyscholarly import fetch_author_data
import asyncio

async def main():
    # Fetch data for a Google Scholar profile
    author_id = "SCHOLAR_ID"  # Replace with actual Google Scholar ID
    data = await fetch_author_data(author_id)
    
    print(f"Author: {data['name']}")
    print(f"Total citations: {data['citations']['all']}")
    print(f"Recent citations: {data['citations']['recent']}")
    print(f"h-index: {data['h_index']['all']}")
    
    # Print top 5 publications
    print("
Top 5 publications:")
    for pub in data['publications'][:5]:
        print(f"- {pub['title']} ({pub['year']}) - {pub['citations']} citations")

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Async/await support for efficient data fetching
- Clean, typed interface
- Comprehensive publication data including:
  - Citation counts (all-time and recent)
  - H-index and i10-index
  - Publication details (title, authors, venue, year)
- Modern Playwright-based scraping

## Requirements

- Python 3.8+
- Playwright

## License

This project is licensed under the MIT License - see the LICENSE file for details.
