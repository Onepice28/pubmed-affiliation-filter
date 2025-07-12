# PubMed Affiliation Filter

A command-line tool to search PubMed and filter papers based on author affiliations with pharmaceutical and biotech companies.

## Features

- Search PubMed using any valid query
- Filter papers where authors are affiliated with pharmaceutical or biotech companies
- Extract key paper details:
  - PubMed ID
  - Title
  - Publication date
  - Author information
  - Author affiliations
  - Corresponding author email (when available)
- Output results to CSV or console
- Configurable minimum number of company affiliations required

## Installation

1. Make sure you have Python 3.8+ and Poetry installed
2. Clone this repository
3. Install dependencies:
   ```bash
   poetry install
   ```

## Configuration

Before using the tool, you need to set your email address for NCBI's E-utilities. This can be done in two ways:

1. Environment variable:
   ```bash
   export NCBI_EMAIL="your.email@example.com"
   ```

2. Command line option:
   ```bash
   poetry run get-papers-list "your query" --email your.email@example.com
   ```

## Usage

The tool can be used in two ways:

1. Using the installed command:
   ```bash
   poetry run get-papers-list "your search query" [options]
   ```

2. Running the module directly:
   ```bash
   poetry run python -m pubmed_affiliation_filter "your search query" [options]
   ```

### Options

- `-f, --file`: Output filename for CSV format
- `-d, --debug`: Enable debug logging
- `--min-companies`: Minimum number of company affiliations required (default: 1)
- `--email`: Your email address for NCBI E-utilities (required if not set via environment variable)
- `--max-results`: Maximum number of results to fetch (default: 100)

### Examples

1. Search and display results in console:
   ```bash
   poetry run get-papers-list "cancer immunotherapy" --email your.email@example.com
   ```

2. Save results to CSV:
   ```bash
   poetry run get-papers-list "CRISPR" -f results.csv --email your.email@example.com
   ```

3. Require at least 2 company affiliations:
   ```bash
   poetry run get-papers-list "antibody therapy" --min-companies 2 --email your.email@example.com
   ```

## Development

The project uses:
- Poetry for dependency management
- Biopython for PubMed API interaction
- Pandas for CSV output
- Type hints throughout the codebase
- Pytest for testing

### Project Structure

```
pubmed-affiliation-filter/
├── pubmed_affiliation_filter/
│   ├── __init__.py
│   ├── api.py          # PubMed API interaction
│   ├── cli.py          # Command-line interface
│   ├── filters.py      # Affiliation filtering logic
│   └── utils.py        # CSV and formatting utilities
├── tests/
│   └── test_api.py     # API tests
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Important Note

When using this tool, please be mindful of NCBI's E-utilities usage guidelines:
- Make no more than 3 requests per second
- Use your email address so NCBI can contact you if there are problems
- Run large jobs on weekends or between 9 pm and 5 am Eastern time weekdays

The tool includes reasonable defaults for rate limiting and batch sizes. 