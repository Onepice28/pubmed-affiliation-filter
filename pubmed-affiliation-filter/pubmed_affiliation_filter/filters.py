from typing import List

def is_company_affiliated(affiliation: str) -> bool:
    """
    Check if an affiliation is from a pharmaceutical or biotech company.
    
    Args:
        affiliation: The affiliation string to check
        
    Returns:
        True if the affiliation appears to be from a company
    """
    # Common company indicators
    company_keywords = [
        "Inc", "Ltd", "LLC", "Corporation", "Corp", "GmbH",
        "Pharma", "Biotech", "Therapeutics", "Company", "Co",
        "Pharmaceuticals", "Biotechnology", "Biosciences",
        "Labs", "Laboratories", "Technologies"
    ]
    
    # Academic/non-company indicators
    non_company_keywords = [
        "University", "Institute", "College", "School",
        "Hospital", "Medical Center", "Clinic", "Foundation",
        "Research Center", "Academy", "Department of",
        "Ministry of", "National", "Federal"
    ]
    
    # Convert to uppercase for case-insensitive matching
    affiliation_upper = affiliation.upper()
    
    # Check for non-company keywords first
    for keyword in non_company_keywords:
        if keyword.upper() in affiliation_upper:
            return False
            
    # Then check for company keywords
    for keyword in company_keywords:
        if keyword.upper() in affiliation_upper:
            return True
            
    return False
