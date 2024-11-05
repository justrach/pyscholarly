from pyscholarly import fetch_scholar_data
import asyncio
import logging
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import sys
from typing import Dict
PROXIES = [
    "http://ryemmxgm:8cf3hhzyva4h@198.23.239.134:6540",
    "http://ryemmxgm:8cf3hhzyva4h@207.244.217.165:6712",
    "http://ryemmxgm:8cf3hhzyva4h@107.172.163.27:6543",
    "http://ryemmxgm:8cf3hhzyva4h@64.137.42.112:5157",
    "http://ryemmxgm:8cf3hhzyva4h@173.211.0.148:6641",
    "http://ryemmxgm:8cf3hhzyva4h@161.123.152.115:6360",
    "http://ryemmxgm:8cf3hhzyva4h@167.160.180.203:6754",
    "http://ryemmxgm:8cf3hhzyva4h@154.36.110.199:6853",
    "http://ryemmxgm:8cf3hhzyva4h@173.0.9.70:5653",
    "http://ryemmxgm:8cf3hhzyva4h@173.0.9.209:5792"
]
def setup_logging() -> logging.Logger:
    """Configure logging for the application"""
    logger = logging.getLogger('scholar_scraper')
    logger.setLevel(logging.INFO)
    
    # Console handler with custom formatting
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def print_author_stats(data: Dict) -> None:
    """Print author statistics using Rich tables"""
    console = Console()
    
    # Author Statistics Table
    stats_table = Table(title=f"Author Statistics: {data['name']}")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("All Time", style="green")
    stats_table.add_column("Recent", style="yellow")
    
    stats_table.add_row("Citations", str(data['citedby']), str(data['citedby_recent']))
    stats_table.add_row("h-index", str(data['hindex']), str(data['hindex_recent']))
    stats_table.add_row("i10-index", str(data['i10index']), str(data['i10index_recent']))
    
    console.print(stats_table)

def print_publications(publications: list) -> None:
    """Print publications using Rich tables"""
    console = Console()
    
    # Publications Table
    pub_table = Table(title="Top 5 Publications")
    pub_table.add_column("#", style="cyan", width=3)
    pub_table.add_column("Title", style="blue")
    pub_table.add_column("Year", style="green", width=6)
    pub_table.add_column("Citations", style="yellow", width=10)
    pub_table.add_column("YTD Citations", style="red", width=12)
    
    for i, pub in enumerate(publications[:5], 1):
        pub_table.add_row(
            str(i),
            pub['bib']['title'],
            pub['year'],
            str(pub['num_citations']),
            str(pub.get('ytd_citations', 0))
        )
        
        # Print authors and venue details after each row
        console.print(f"Authors: {pub['bib']['authors']}", style="dim")
        console.print(f"Venue: {pub['bib']['venue']}", style="dim")
        console.print()
    
    console.print(pub_table)

async def fetch_scholar_profile(author_id: str, logger: logging.Logger) -> Dict:
    """Fetch and return scholar profile data"""
    try:
        logger.info(f"Fetching data for scholar ID: {author_id}")
        return await fetch_scholar_data(
            author_id, 
            logger=logger,
            headless=True,
            proxies=PROXIES,
            proxy_rotation='random'
        )
    except Exception as e:
        logger.error(f"Error fetching scholar data: {e}")
        raise

async def main():
    # Setup
    logger = setup_logging()
    author_id = "5TZ7f5wAAAAJ"
    
    try:
        # Fetch data
        logger.info("Starting scholar data fetch")
        data = await fetch_scholar_profile(author_id, logger)
        
        # Print results
        console = Console()
        console.rule("[bold blue]Google Scholar Profile Analysis")
        
        print_author_stats(data)
        console.print()  # Add spacing
        
        print_publications(data['publications'])
        
        logger.info("Analysis complete")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())