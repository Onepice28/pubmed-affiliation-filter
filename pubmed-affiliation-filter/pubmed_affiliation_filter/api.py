# api.py
import os
import time
import requests
from typing import List, Dict, Any, Optional
from Bio import Entrez
import logging
from .filters import is_company_affiliated
import re

class PubMedAPI:
    """Class to handle PubMed API interactions with rate limiting."""
    
    def __init__(self, email: Optional[str] = None, requests_per_second: float = 3.0):
        """
        Initialize PubMed API handler.
        
        Args:
            email: Email address for NCBI E-utilities. If not provided, will try to get from NCBI_EMAIL env var.
            requests_per_second: Maximum number of requests per second (default: 3.0 as per NCBI guidelines)
        """
        self.email = email or os.environ.get("NCBI_EMAIL")
        if not self.email:
            raise ValueError("Email address is required. Set via constructor or NCBI_EMAIL environment variable.")
            
        self.min_request_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        
        # Configure Entrez
        Entrez.email = self.email
        Entrez.tool = "PubMedAffiliationFilter"
        
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed the rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def search_pubmed(self, query: str, retmax: int = 10) -> List[str]:
        """Search PubMed for papers matching the query."""
        self._wait_for_rate_limit()
        
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["esearchresult"]["idlist"]

    def fetch_details(self, paper_ids: List[str]) -> str:
        """Fetch details for a list of PubMed IDs."""
        self._wait_for_rate_limit()
        
        ids = ",".join(paper_ids)
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "xml"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text

    def fetch_and_filter_papers(self, query: str, min_companies: int = 1, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch papers from PubMed and filter by company affiliations.
        
        Args:
            query: PubMed search query
            min_companies: Minimum number of company affiliations required
            max_results: Maximum number of results to fetch
            
        Returns:
            List of papers with required company affiliations
        """
        logging.info(f"Searching PubMed for: {query}")
        
        # Search PubMed
        self._wait_for_rate_limit()
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        if not record["IdList"]:
            logging.warning("No results found")
            return []
        
        # Fetch paper details
        self._wait_for_rate_limit()
        handle = Entrez.efetch(db="pubmed", id=record["IdList"], rettype="medline", retmode="xml")
        papers = Entrez.read(handle)["PubmedArticle"]
        handle.close()
        
        filtered_papers = []
        for paper in papers:
            article = paper["MedlineCitation"]["Article"]
            
            # Extract paper details
            paper_data = {
                "pmid": paper["MedlineCitation"]["PMID"],
                "title": article["ArticleTitle"],
                "publication_date": self._extract_publication_date(article),
                "authors": self._extract_authors(article),
                "affiliations": self._extract_affiliations(article),
                "corresponding_email": self._extract_corresponding_email(article)
            }
            
            # Check company affiliations
            company_count = sum(1 for aff in paper_data["affiliations"] if is_company_affiliated(aff))
            if company_count >= min_companies:
                filtered_papers.append(paper_data)
        
        logging.info(f"Found {len(filtered_papers)} papers with company affiliations")
        return filtered_papers

    def _extract_publication_date(self, article: Dict[str, Any]) -> str:
        """Extract publication date in YYYY-MM-DD format."""
        try:
            pub_date = article.get("ArticleDate", [{}])[0]
            if pub_date:
                return f"{pub_date.get('Year', '')}-{pub_date.get('Month', '')}-{pub_date.get('Day', '')}"
            return article["Journal"]["JournalIssue"]["PubDate"].get("Year", "")
        except (KeyError, IndexError):
            return ""

    def _extract_authors(self, article: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract author information."""
        authors = []
        try:
            for author in article["AuthorList"]:
                author_data = {
                    "last_name": author.get("LastName", ""),
                    "first_name": author.get("ForeName", ""),
                    "affiliation": author.get("AffiliationInfo", [{}])[0].get("Affiliation", "")
                }
                authors.append(author_data)
        except KeyError:
            pass
        return authors

    def _extract_affiliations(self, article: Dict[str, Any]) -> List[str]:
        """Extract unique affiliations."""
        affiliations = set()
        try:
            for author in article["AuthorList"]:
                for aff in author.get("AffiliationInfo", []):
                    if "Affiliation" in aff:
                        affiliations.add(aff["Affiliation"])
        except KeyError:
            pass
        return list(affiliations)

    def _extract_corresponding_email(self, article: Dict[str, Any]) -> Optional[str]:
        """Extract corresponding author email if available."""
        try:
            for author in article["AuthorList"]:
                if "AffiliationInfo" in author:
                    for aff in author["AffiliationInfo"]:
                        affiliation = aff.get("Affiliation", "")
                        if "email" in affiliation.lower() or "@" in affiliation:
                            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', affiliation)
                            if email_match:
                                return email_match.group(0)
        except KeyError:
            pass
        return None
