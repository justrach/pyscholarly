from pyscholarly import fetch_multiple_scholars
import asyncio
import logging
from rich.console import Console
from rich.table import Table
import sys
from typing import Dict, List

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
        
        console.print(f"Authors: {pub['bib']['authors']}", style="dim")
        console.print(f"Venue: {pub['bib']['venue']}", style="dim")
        console.print()
    
    console.print(pub_table)

async def main():
    # Setup
    logger = setup_logging()
    
    # List of scholar IDs to fetch
    scholar_ids = [
        "u5VcrGgAAAAJ",  # Example scholar 1
        "yMGBji4AAAAJ",  # Example scholar 2
        "xt4UjA4AAAAJ"   # Example scholar 3
    ]
    
    try:
        # Fetch data for multiple scholars
        logger.info("Starting scholar data fetch for multiple authors")
        results = await fetch_multiple_scholars(
            scholar_ids=scholar_ids,
            logger=logger,
            proxies=PROXIES,
            headless=True,
            proxy_rotation='random',
                max_workers=3,
    redis_url="redis://localhost:6379"
        )
        
        # Print results for each scholar
        console = Console()
        
        for i, data in enumerate(results, 1):
            if data:
                console.rule(f"[bold blue]Google Scholar Profile #{i}")
                print_author_stats(data)
                console.print()  # Add spacing
                print_publications(data['publications'])
                console.print()  # Add spacing between scholars
            else:
                console.print(f"[red]Failed to fetch data for scholar ID: {scholar_ids[i-1]}")
        
        logger.info("Analysis complete")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())