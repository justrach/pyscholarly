from playwright.async_api import async_playwright
from datetime import datetime
import re
import asyncio
from typing import Dict, List, Optional, Union
import json
import logging
from logging import Logger
import random
from bs4 import BeautifulSoup
import aiohttp
from pathlib import Path
import os
class ProxyRotator:
    def __init__(self, proxies: Optional[Union[str, List[str]]] = None):
        # Convert proxy strings to proper format if needed
        if isinstance(proxies, str):
            proxies = [proxies]
        
        self.proxies = []
        if proxies:
            for proxy in proxies:
                # Handle proxy strings with authentication
                if '@' in proxy:
                    self.proxies.append(proxy)
                else:
                    # If no auth in URL, assume it's a simple proxy
                    self.proxies.append(f"http://{proxy}")
        
        self._current_index = 0

    def get_next(self) -> Optional[str]:
        if not self.proxies:
            return None
        proxy = self.proxies[self._current_index]
        self._current_index = (self._current_index + 1) % len(self.proxies)
        return proxy

    def get_random(self) -> Optional[str]:
        return random.choice(self.proxies) if self.proxies else None

class Scholar:
    def __init__(
        self, 
        logger: Optional[Logger] = None, 
        proxies: Optional[Union[str, List[str]]] = None,
        headless: bool = False,
        proxy_rotation: str = 'sequential'
    ):
        self._playwright = None
        self._browser = None
        self.logger = logger or logging.getLogger(__name__)
        self.proxy_rotator = ProxyRotator(proxies)
        self.headless = headless
        self.proxy_rotation = proxy_rotation

    async def _create_browser_context(self, proxy: Optional[str] = None):
        """Create a new browser context with optional proxy"""
        browser_args = {}
        
        if proxy:
            self.logger.debug(f"Using proxy: {proxy}")
            # Parse proxy string to extract authentication if present
            if '@' in proxy:
                # Format: protocol://username:password@host:port
                auth_part = proxy.split('@')[0].split('://')[1]
                server_part = proxy.split('@')[1]
                username, password = auth_part.split(':')
                
                browser_args["proxy"] = {
                    "server": f"http://{server_part}",
                    "username": username,
                    "password": password
                }
            else:
                browser_args["proxy"] = {"server": proxy}
        
        return await self._browser.new_context(**browser_args)
    async def __aenter__(self):
        self.logger.info("Initializing Scholar session")
        self._playwright = await async_playwright().start()
        # Moved headless parameter here
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Closing Scholar session")
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    def _get_proxy(self) -> Optional[str]:
        """Get next proxy based on rotation strategy"""
        if self.proxy_rotation == 'random':
            return self.proxy_rotator.get_random()
        return self.proxy_rotator.get_next()

    async def _get_page_content(self, url: str) -> str:
        self.logger.debug(f"Fetching content from {url}")
        proxy = self._get_proxy()
        context = await self._create_browser_context(proxy)
        page = await context.new_page()
        
        try:
            await page.goto(url)
            await page.wait_for_selector("#gsc_rsb_cit")
            content = await page.content()
            return content
        except Exception as e:
            self.logger.error(f"Error fetching page content: {e}")
            raise
        finally:
            await page.close()
            await context.close()

    async def _get_ytd_citations(self, citation_link: str) -> int:
        """Get year-to-date citations for a specific paper"""
        if not citation_link:
            return 0
            
        self.logger.debug(f"Getting YTD citations from link: {citation_link}")
        
        try:
            # Create debug directory if it doesn't exist
            debug_dir = Path('debug_pages')
            debug_dir.mkdir(exist_ok=True)
            
            # Use Playwright page to navigate
            page = await self._browser.new_page()
            await page.goto(citation_link)
            
            # Modify URL for current year
            current_year = datetime.now().year
            ytd_url = f"{page.url}&as_ylo={current_year}"
            
            # Navigate to the YTD URL
            await page.goto(ytd_url)
            
            # Save the page content for debugging
            html = await page.content()
            ytd_filename = debug_dir / f"ytd_page_{hash(citation_link)}.html"
            with open(ytd_filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Use Playwright's selector to find the results count
            results_div = await page.query_selector('#gs_ab_md .gs_ab_mdw')
            if results_div:
                results_text = await results_div.text_content()
                self.logger.debug(f"Found results text: {results_text}")
                
                # Try both "About X results" and "X results" formats
                match = re.search(r'(?:About )?(\d+(?:,\d+)?)\s+results?', results_text)
                if match:
                    count = int(match.group(1).replace(',', ''))
                    self.logger.info(f"Found {count} YTD citations")
                    return count
                    
            self.logger.warning(f"Could not find citation count in page. Full HTML saved to {ytd_filename}")
            return 0
            
        finally:
            await page.close()
    async def get_author_data(self, scholar_id: str) -> Dict:
        self.logger.info(f"Fetching author data for scholar ID: {scholar_id}")
        url = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&pagesize=100&view_op=list_works"
        content = await self._get_page_content(url)

        proxy = self._get_proxy()
        context = await self._create_browser_context(proxy)
        page = await context.new_page()
        await page.set_content(content)

        try:
            author_info = await page.evaluate('''() => {
                const name = document.querySelector("#gsc_prf_in")?.innerText || "";
                
                const stats = {};
                const rows = document.querySelectorAll("#gsc_rsb_st tbody tr");
                rows.forEach(row => {
                    const label = row.querySelector(".gsc_rsb_sc1 .gsc_rsb_f")?.innerText;
                    const values = Array.from(row.querySelectorAll(".gsc_rsb_std"));
                    if (label && values.length >= 2) {
                        stats[label] = {
                            all: parseInt(values[0].innerText) || 0,
                            recent: parseInt(values[1].innerText) || 0
                        };
                    }
                });
                
                return { name, stats };
            }''')

            publications = []
            last_count = 0
            
            while True:
                pub_data = await page.evaluate('''() => {
                    const pubs = Array.from(document.querySelectorAll('#gsc_a_b .gsc_a_tr'));
                    return pubs.map(pub => ({
                        title: pub.querySelector('.gsc_a_at')?.innerText || '',
                        citations: pub.querySelector('.gsc_a_ac')?.innerText || '0',
                        citation_link: pub.querySelector('.gsc_a_ac')?.href || null,
                        year: pub.querySelector('.gsc_a_y .gsc_a_h')?.innerText || '',
                        authors: pub.querySelectorAll('.gs_gray')[0]?.innerText || '',
                        venue: pub.querySelectorAll('.gs_gray')[1]?.innerText || ''
                    }));
                }''')

                current_count = len(pub_data)
                if current_count == last_count:
                    break

                for pub in pub_data[last_count:]:
                    try:
                        citation_count = int(pub['citations']) if pub['citations'] and pub['citations'] != '' else 0
                    except ValueError:
                        citation_count = 0

                    ytd_citations = await self._get_ytd_citations(pub['citation_link']) if pub['citation_link'] else 0

                    publications.append({
                        'title': pub['title'],
                        'authors': pub['authors'],
                        'venue': pub['venue'],
                        'num_citations': citation_count,
                        'ytd_citations': ytd_citations,
                        'year': pub['year']
                    })

                last_count = current_count
                
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                try:
                    await page.wait_for_function(
                        'document.querySelectorAll("#gsc_a_b .gsc_a_tr").length > arguments[0]',
                        arg=current_count,
                        timeout=3000
                    )
                except:
                    break

            return {
                'name': author_info['name'],
                'citations': author_info['stats'].get('Citations', {'all': 0, 'recent': 0}),
                'h_index': author_info['stats'].get('h-index', {'all': 0, 'recent': 0}),
                'i10_index': author_info['stats'].get('i10-index', {'all': 0, 'recent': 0}),
                'publications': publications
            }

        finally:
            await page.close()
            await context.close()

    @staticmethod
    def format_response(author_data: Dict) -> Dict:
        """Format the scraped data to match the structure expected by the existing application"""
        publications = []
        for pub in author_data['publications']:
            publications.append({
                'bib': {
                    'title': pub['title'],
                    'authors': pub['authors'],
                    'venue': pub['venue']
                },
                'num_citations': pub['num_citations'],
                'ytd_citations': pub['ytd_citations'],
                'year': pub.get('year', '')
            })

        return {
            'name': author_data['name'],
            'citedby': author_data['citations']['all'],
            'citedby_recent': author_data['citations']['recent'],
            'hindex': author_data['h_index']['all'],
            'hindex_recent': author_data['h_index']['recent'],
            'i10index': author_data['i10_index']['all'],
            'i10index_recent': author_data['i10_index']['recent'],
            'publications': publications
        }

async def fetch_scholar_data(
    scholar_id: str, 
    logger: Optional[Logger] = None,
    proxies: Optional[Union[str, List[str]]] = None,
    headless: bool = False,
    proxy_rotation: str = 'sequential'
) -> Dict:
    async with Scholar(
        logger=logger, 
        proxies=proxies, 
        headless=headless,
        proxy_rotation=proxy_rotation
    ) as scraper:
        author_data = await scraper.get_author_data(scholar_id)
        return Scholar.format_response(author_data)