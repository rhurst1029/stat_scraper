# Water Polo Data Pipeline

This project implements an automated data pipeline for collecting and analyzing water polo match data from multiple sources, including Total Water Polo (TWP) and 6-8 Sports platforms. The data is processed, stored in AWS, and visualized using Tableau.

> **Legal Note**: This project's data collection methods are legally protected under the precedent set by [hiQ Labs v. LinkedIn](https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn), which established that web scraping of publicly available data is legal under U.S. law.

## Data Flow Architecture

```mermaid
graph LR
    A[TWP Scraper] --> D[Data Processing]
    B[6-8 Sports Scraper] --> D
    D --> E[AWS Storage]
    E --> F[Tableau]
    F --> G[Visualization Dashboard]
```

## AWS Infrastructure

```mermaid
graph TD
    A[Web Scrapers] -->|New Game Data| B[Lambda Trigger]
    B -->|Trigger| C[EC2 Instance]
    C -->|Process Data| D[Redshift]
    D -->|Connect| E[Tableau]
    
    subgraph AWS Cloud
        B
        C
        D
    end
    
    subgraph Data Sources
        A
    end
    
    subgraph Visualization
        E
    end
```

## Components

### 1. Data Collection
- **TWP Scraper** (`twp_scraper.py`): Collects match data from Total Water Polo platform
  - Play-by-play data
  - Team statistics
  - Match metadata
  - Player performance metrics

- **6-8 Sports Scraper** (`6_8_scraper.py`): Collects data from 6-8 Sports platform
  - Game statistics
  - Team performance data
  - Match details

### 2. Data Processing
- **TWP Constructor** (`twp_constructor.py`): Processes and standardizes data from both sources
  - Data cleaning and normalization
  - Format standardization
  - Data validation

### 3. Data Storage
- **AWS Infrastructure**:
  - Lambda triggers on new game creation
  - EC2 instances for data processing
  - Redshift for data warehousing
  - Tableau connector for visualization
- Structured data storage for easy querying
- Historical data archiving

### 4. Visualization
- Tableau dashboards for data analysis
- Interactive visualizations
- Performance metrics and trends
- Team and player statistics

## Example Visualizations

### Champions League Analysis
<iframe src="https://public.tableau.com/app/profile/ryan.hurst/viz/ChampionsLeagueBreakdown2/OLYRECChampionsLeague?:showVizHome=no&:embed=true" width="800" height="600"></iframe>

### Champions League Matchup Analysis
<iframe src="https://public.tableau.com/app/profile/ryan.hurst/viz/MatchupAnalysisChampionsLeague/OLYRECChampionsLeague?:showVizHome=no&:embed=true" width="800" height="600"></iframe>

### Champions League Individual Contributions
<iframe src="https://public.tableau.com/app/profile/ryan.hurst/viz/MatchupAnalysisChampionsLeague/OLYRECChampionsLeague?:showVizHome=no&:embed=true" width="800" height="600"></iframe>

### World Championships 2024: Croatia vs Italy
<iframe src="https://public.tableau.com/app/profile/ryan.hurst/viz/CroatiaVSItalyWorldChampionships2024/OLYRECChampionsLeague?:showVizHome=no&:embed=true" width="800" height="600"></iframe>

### National League 2023 Breakdown
<iframe src="https://public.tableau.com/app/profile/ryan.hurst/viz/CroatiaVSItalyWorldChampionships2024/OLYRECChampionsLeague?:showVizHome=no&:embed=true" width="800" height="600"></iframe>

## Setup and Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials
4. Set up Tableau connection

## Dependencies

- selenium==4.15.2
- fake-useragent==1.4.0
- numpy==1.24.3
- pandas==2.1.3
- openpyxl==3.1.2
- requests-html==0.10.0
- beautifulsoup4==4.12.2
- playwright==1.41.2
- regex==2023.12.25

## Usage

1. Run TWP scraper:
```bash
python twp_scraper.py
```

2. Run 6-8 Sports scraper:
```bash
python 6_8_scraper.py
```

3. Process data:
```bash
python twp_constructor.py
```

## Visualization

View the interactive dashboards at: [Tableau Public Profile](https://public.tableau.com/app/profile/ryan.hurst/vizzes)

## Custom Analysis

For custom analysis and development of sport-specific metrics, please contact:
- Email: ryanhurst@berkeley.edu

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.