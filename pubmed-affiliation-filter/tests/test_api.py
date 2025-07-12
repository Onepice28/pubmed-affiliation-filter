import pytest
from unittest.mock import patch, MagicMock
from pubmed_affiliation_filter.api import PubMedAPI
from pubmed_affiliation_filter.filters import is_company_affiliated

def test_pubmed_api_requires_email():
    """Test that PubMedAPI requires an email address."""
    with pytest.raises(ValueError, match="Email address is required"):
        PubMedAPI()

def test_pubmed_api_accepts_email_from_env(monkeypatch):
    """Test that PubMedAPI accepts email from environment variable."""
    monkeypatch.setenv("NCBI_EMAIL", "test@example.com")
    api = PubMedAPI()
    assert api.email == "test@example.com"

def test_pubmed_api_constructor_email():
    """Test that PubMedAPI accepts email in constructor."""
    api = PubMedAPI(email="test@example.com")
    assert api.email == "test@example.com"

def test_rate_limiting():
    """Test that rate limiting works."""
    api = PubMedAPI(email="test@example.com", requests_per_second=2.0)
    
    # First request should not wait
    with patch("time.sleep") as mock_sleep:
        api._wait_for_rate_limit()
        mock_sleep.assert_not_called()
    
    # Second request should wait if too soon
    with patch("time.sleep") as mock_sleep:
        api._wait_for_rate_limit()
        mock_sleep.assert_called_once()

@pytest.mark.parametrize("affiliation,expected", [
    ("Pfizer Inc., New York, USA", True),
    ("Moderna Therapeutics", True),
    ("BioNTech GmbH", True),
    ("Harvard University", False),
    ("Stanford Medical School", False),
    ("National Institutes of Health", False),
    ("Genentech Inc", True),
    ("AstraZeneca Pharmaceuticals", True),
    ("Memorial Sloan Kettering Cancer Center", False),
    ("Johnson & Johnson Pharmaceutical R&D", True),
])
def test_company_affiliation_detection(affiliation, expected):
    """Test company affiliation detection with various examples."""
    assert is_company_affiliated(affiliation) == expected

@patch("pubmed_affiliation_filter.api.Entrez")
def test_fetch_and_filter_papers(mock_entrez):
    """Test fetching and filtering papers."""
    # Mock Entrez search response
    mock_search_handle = MagicMock()
    mock_search_handle.read.return_value = {"IdList": ["12345", "67890"]}
    mock_entrez.esearch.return_value = mock_search_handle
    
    # Mock Entrez fetch response
    mock_fetch_handle = MagicMock()
    mock_fetch_handle.read.return_value = {
        "PubmedArticle": [
            {
                "MedlineCitation": {
                    "PMID": "12345",
                    "Article": {
                        "ArticleTitle": "Test Paper 1",
                        "AuthorList": [
                            {
                                "LastName": "Smith",
                                "ForeName": "John",
                                "AffiliationInfo": [{"Affiliation": "Pfizer Inc."}]
                            }
                        ],
                        "Journal": {
                            "JournalIssue": {
                                "PubDate": {"Year": "2023"}
                            }
                        }
                    }
                }
            }
        ]
    }
    mock_entrez.efetch.return_value = mock_fetch_handle
    
    api = PubMedAPI(email="test@example.com")
    papers = api.fetch_and_filter_papers("test query", min_companies=1)
    
    assert len(papers) == 1
    assert papers[0]["pmid"] == "12345"
    assert papers[0]["title"] == "Test Paper 1"
    assert any("Pfizer" in aff for aff in papers[0]["affiliations"])
