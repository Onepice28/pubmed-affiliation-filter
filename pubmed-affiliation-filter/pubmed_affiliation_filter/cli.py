import argparse
import logging
import sys
from pubmed_affiliation_filter.api import PubMedAPI
from pubmed_affiliation_filter.utils import save_to_csv, format_paper_details

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and filter PubMed papers by author affiliations with pharmaceutical and biotech companies."
    )
    parser.add_argument("query", type=str, help="Search query for PubMed")
    parser.add_argument("-f", "--file", type=str, help="Output filename for CSV format")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--min-companies", type=int, default=1,
                      help="Minimum number of company affiliations required (default: 1)")
    parser.add_argument("--email", type=str, help="Your email address for NCBI E-utilities")
    parser.add_argument("--max-results", type=int, default=100,
                      help="Maximum number of results to fetch (default: 100)")

    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    try:
        # Initialize PubMed API
        api = PubMedAPI(email=args.email)
        
        print(f"Query: {args.query}")
        print("Searching PubMed...")
        
        papers = api.fetch_and_filter_papers(
            args.query,
            min_companies=args.min_companies,
            max_results=args.max_results
        )
        
        if not papers:
            print("No papers found matching the criteria.")
            return
            
        print(f"Found {len(papers)} papers with company affiliations.")
        
        if args.file:
            save_to_csv(papers, args.file)
            print(f"Results saved to {args.file}")
        else:
            for paper in papers:
                print("\n" + format_paper_details(paper))
                
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if args.debug:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
