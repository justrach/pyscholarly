import asyncio
import logging
from pyscholarly import fetch_scholar_data

async def main():
    # Setup logging to see what's happening
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Example Google Scholar IDs to test with
    # You can find these in the URL of any Google Scholar profile
    # e.g., https://scholar.google.com/citations?user=SCHOLAR_ID
    scholar_ids = [
        "u5VcrGgAAAAJ",  # Geoffrey Hinton
     
    ]

    for scholar_id in scholar_ids:
        try:
            print(f"\nFetching data for scholar ID: {scholar_id}")
            data = await fetch_scholar_data(
                scholar_id=scholar_id,
                logger=logger,
                headless=True  # Set to False if you want to see the browser
            )
            
            # Print basic info
            print(f"\nAuthor: {data['name']}")
            print(f"Total citations: {data['citedby']}")
            print(f"Recent citations: {data['citedby_recent']}")
            print(f"h-index: {data['hindex']}")
            
            # Print publications with YTD citations
            print("\nTop 5 Publications:")
            for pub in data['publications'][:5]:
                print(f"\nTitle: {pub['bib']['title']} ({pub['year']})")
                print(f"Total citations: {pub['num_citations']}")
                print(f"YTD citations: {pub['ytd_citations']}")

        except Exception as e:
            print(f"Error fetching data for {scholar_id}: {e}")

if __name__ == "__main__":
    asyncio.run(main())