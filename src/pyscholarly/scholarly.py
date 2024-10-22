from playwright.async_api import async_playwright
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

class Scholar:
    """A class to interact with Google Scholar profiles."""
    
    def __init__(self):
        self._playwright = None
        self._browser = None
        
    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def get_author_data(self, author_id: str) -> Dict:
        """
        Fetch author data from Google Scholar.
        
        Args:
            author_id (str): The Google Scholar author ID
            
        Returns:
            Dict: Author data including citations, publications, and metrics
        """
        url = f"https://scholar.google.com/citations?user={author_id}&hl=en"
        page = await self._browser.new_page()
        
        try:
            await page.goto(url)
            await page.wait_for_selector("#gsc_rsb_cit")
            
            # Get author name
            name = await page.evaluate('() => document.querySelector("#gsc_prf_in")?.innerText || ""')
            
            # Get citation statistics
            stats = {}
            rows = await page.query_selector_all("#gsc_rsb_st tbody tr")
            
            for row in rows:
                cells = await row.query_selector_all("td")
                if len(cells) == 3:  # Metric name, all-time value, recent value
                    metric_cell = await cells[0].query_selector(".gsc_rsb_f")
                    if metric_cell:
                        metric_name = (await metric_cell.text_content()).strip()
                        all_time = await cells[1].text_content()
                        recent = await cells[2].text_content()
                        
                        stats[metric_name] = {
                            'all': int(all_time),
                            'recent': int(recent)
                        }

            # Get publications
            pubs = await page.query_selector_all('#gsc_a_b .gsc_a_tr')
            publications = []
            
            for pub in pubs:
                title_elem = await pub.query_selector('.gsc_a_at')
                cite_elem = await pub.query_selector('.gsc_a_ac')
                year_elem = await pub.query_selector('.gsc_a_y .gsc_a_h')
                
                authors_venue = await pub.query_selector_all('.gs_gray')
                
                title = await title_elem.text_content() if title_elem else ''
                citations = await cite_elem.text_content() if cite_elem else '0'
                year = await year_elem.text_content() if year_elem else ''
                
                authors = await authors_venue[0].text_content() if len(authors_venue) > 0 else ''
                venue = await authors_venue[1].text_content() if len(authors_venue) > 1 else ''

                publications.append({
                    'title': title,
                    'authors': authors,
                    'venue': venue,
                    'citations': int(citations) if citations.isdigit() else 0,
                    'year': year
                })

            return {
                'author_id': author_id,
                'name': name,
                'citations': stats.get('Citations', {'all': 0, 'recent': 0}),
                'h_index': stats.get('h-index', {'all': 0, 'recent': 0}),
                'i10_index': stats.get('i10-index', {'all': 0, 'recent': 0}),
                'publications': publications
            }

        finally:
            await page.close()

async def fetch_author_data(author_id: str) -> Dict:
    """
    Convenience function to fetch author data from Google Scholar.
    
    Args:
        author_id (str): The Google Scholar author ID
        
    Returns:
        Dict: Author data including citations, publications, and metrics
    
    Example:
        >>> import asyncio
        >>> data = asyncio.run(fetch_author_data("author_id"))
        >>> print(f"Total citations: {data['citations']['all']}")
    """
    async with Scholar() as scholar:
        return await scholar.get_author_data(author_id)
