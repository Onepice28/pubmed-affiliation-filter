from typing import List, Dict, Any
import pandas as pd
import logging

def save_to_csv(papers: List[Dict[str, Any]], filename: str) -> None:
    """
    Save paper details to a CSV file.
    
    Args:
        papers: List of paper dictionaries
        filename: Output filename
    """
    if not papers:
        logging.warning("No papers to save")
        return
        
    # Flatten the paper data for CSV output
    flattened_data = []
    for paper in papers:
        row = {
            "PMID": paper["pmid"],
            "Title": paper["title"],
            "Publication Date": paper["publication_date"],
            "Corresponding Email": paper["corresponding_email"] or "",
            "Author Count": len(paper["authors"]),
            "Affiliations": "; ".join(paper["affiliations"]),
        }
        
        # Add author information
        authors = paper["authors"]
        for i, author in enumerate(authors, 1):
            if i <= 5:  # Include details for first 5 authors
                prefix = f"Author{i}"
                row[f"{prefix} Name"] = f"{author['first_name']} {author['last_name']}"
                row[f"{prefix} Affiliation"] = author["affiliation"]
        
        flattened_data.append(row)
    
    # Convert to DataFrame and save
    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False)
    logging.info(f"Saved {len(papers)} papers to {filename}")

def format_paper_details(paper: Dict[str, Any]) -> str:
    """
    Format paper details for console output.
    
    Args:
        paper: Paper dictionary
        
    Returns:
        Formatted string with paper details
    """
    lines = [
        f"PMID: {paper['pmid']}",
        f"Title: {paper['title']}",
        f"Publication Date: {paper['publication_date']}",
    ]
    
    if paper["corresponding_email"]:
        lines.append(f"Corresponding Email: {paper['corresponding_email']}")
    
    lines.append("\nAuthors:")
    for author in paper["authors"]:
        name = f"{author['first_name']} {author['last_name']}"
        lines.append(f"  - {name}")
        if author["affiliation"]:
            lines.append(f"    Affiliation: {author['affiliation']}")
    
    return "\n".join(lines) + "\n"
