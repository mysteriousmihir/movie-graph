# CineGraph — Neo4j Movie Explorer

A mini project for NoSQL subject demonstrating Neo4j graph database
with a Flask backend and vanilla JS frontend.

## Dataset
- 4,800+ movies
- 56,000+ persons (actors & directors)
- sourced from TMDB credits dataset

## Setup

## Dataset
Download the dataset from Kaggle:
https://www.kaggle.com/datasets/mihirgaonkar/tmdb-5000-movies-dataset-corrected

Files needed:
- tmdb_5000_movies.csv
- properly_formatted_credits.csv

## Perform this before Step 3 
Place both files in your Neo4j import folder:
C:\Users\<YourName>\.Neo4jDesktop\Data\dbmss\<your-dbms-id>\import\

### 1. Clone the repo
git clone https://github.com/mysteriousmihir/movie-graph.git
cd movie-graph

### 2. Install dependencies
pip install -r requirements.txt

# Allow CSVs despite gitignore
!*.csv

### 3. Import the database
- Open Neo4j Desktop and create a new database
- Run the schema constraints and import queries
  from `cypher/` folder in order

### 4. Configure environment
cp .env.example .env
# Edit .env with your Neo4j password

### 5. Run the app
python app.py

### 6. Open the frontend
Open templates/index.html in your browser
