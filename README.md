# CineGraph — Neo4j Movie Explorer

A mini project for the NoSQL subject demonstrating a Neo4j graph database
with a Flask backend and vanilla JS frontend.

## Features
- Search movies by title
- Browse movies by genre
- Actor filmography search
- Actor connection finder (shortest path via Neo4j)
- Director profiles and filmography
- Interactive graph visualizer (D3.js)
- Movie recommendations based on shared genres
- TMDB movie posters

## Dataset

Download the dataset from Kaggle:
https://www.kaggle.com/datasets/mihirgaonkar/tmdb-5000-movies-dataset-corrected

Files needed:
- `tmdb_5000_movies.csv`
- `properly_formatted_credits.csv` 

Place both files in your Neo4j import folder, once when you have created a new database:
```
C:\Users\<YourName>\.Neo4jDesktop\Data\dbmss\<your-dbms-id>\import\
```

---

## Setup

### Step 1 — Clone the repo
```cmd
git clone https://github.com/mysteriousmihir/movie-graph.git
cd movie-graph
```

### Step 2 — Install dependencies
```cmd
pip install -r requirements.txt
```

### Step 3 — Import the database
- Open Neo4j Desktop and create a new database
- Start the database
- IMP: Before executing cypher queries, import both the files downloaded from Kaggle onto to the described path as below.
```
C:\Users\<YourName>\.Neo4jDesktop\Data\dbmss\<your-dbms-id>\import\
```
- Run the Cypher queries from the `cypher/` folder **in order**

### Step 4 — Configure environment
Create a file named `.env` in the `movie-graph` folder and paste the following:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=your_database_name
```
Replace `your_neo4j_password` and `your_database_name` with your actual values.

### Step 5 — Run the app
Make sure your Neo4j database is running, then:
```cmd
python app.py
```
You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Step 6 — Open the frontend
Open `templates/index.html` in your browser.

---

## Project Structure
```
movie-graph/
├── app.py               # Flask backend (all API routes)
├── db.py                # Neo4j connection
├── requirements.txt     # Python dependencies
├── .env                 # Your credentials (never commit this)
├── cypher/
│   └── import.cypher    # All Neo4j schema + import queries
└── templates/
    └── index.html       # Frontend (HTML + CSS + JS)
```

---

## Tech Stack
- **Database** — Neo4j (graph database)
- **Backend** — Python, Flask
- **Frontend** — Vanilla HTML, CSS, JavaScript
- **Graph Visualization** — D3.js
- **Movie Posters** — TMDB API
