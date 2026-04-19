//Step 1 — Create Constraints

CREATE CONSTRAINT FOR (m:Movie) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT FOR (g:Genre) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT FOR (k:Keyword) REQUIRE k.id IS UNIQUE;
CREATE CONSTRAINT FOR (c:ProductionCompany) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT FOR (pc:ProductionCountry) REQUIRE pc.iso_3166_1 IS UNIQUE;


//Step 2 — Import Movies

CALL apoc.periodic.iterate(
  'LOAD CSV WITH HEADERS FROM "file:///tmdb_5000_movies.csv" AS row RETURN row',
  'MERGE (m:Movie {id: toInteger(row.id)})
   SET m.title          = row.title,
       m.budget         = toInteger(row.budget),
       m.revenue        = toInteger(row.revenue),
       m.release_date   = row.release_date,
       m.runtime        = toFloat(row.runtime),
       m.status         = row.status,
       m.tagline        = row.tagline,
       m.overview       = row.overview,
       m.popularity     = toFloat(row.popularity),
       m.vote_average   = toFloat(row.vote_average),
       m.vote_count     = toInteger(row.vote_count),
       m.original_title = row.original_title,
       m.original_language = row.original_language,
       m.homepage       = row.homepage',
  {batchSize: 100, parallel: false}
);


//Step 3 — Import Genres

CALL apoc.periodic.iterate(
  'LOAD CSV WITH HEADERS FROM "file:///tmdb_5000_movies.csv" AS row
   WITH row WHERE row.genres IS NOT NULL
   WITH row, apoc.convert.fromJsonList(row.genres) AS genres
   UNWIND genres AS genre RETURN row, genre',
  'MERGE (g:Genre {id: toInteger(genre.id)})
   ON CREATE SET g.name = genre.name
   WITH g, row
   MATCH (m:Movie {id: toInteger(row.id)})
   MERGE (m)-[:IN_GENRE]->(g)',
  {batchSize: 100, parallel: false}
);


//Step 4 — Import Keywords


CALL apoc.periodic.iterate(
  'LOAD CSV WITH HEADERS FROM "file:///tmdb_5000_movies.csv" AS row
   WITH row WHERE row.keywords IS NOT NULL
   WITH row, apoc.convert.fromJsonList(row.keywords) AS keywords
   UNWIND keywords AS kw RETURN row, kw',
  'MERGE (k:Keyword {id: toInteger(kw.id)})
   ON CREATE SET k.name = kw.name
   WITH k, row
   MATCH (m:Movie {id: toInteger(row.id)})
   MERGE (m)-[:HAS_KEYWORD]->(k)',
  {batchSize: 100, parallel: false}
);


//Step 5 — Import Production Companies


CALL apoc.periodic.iterate(
  'LOAD CSV WITH HEADERS FROM "file:///tmdb_5000_movies.csv" AS row
   WITH row WHERE row.production_companies IS NOT NULL
   WITH row, apoc.convert.fromJsonList(row.production_companies) AS companies
   UNWIND companies AS company RETURN row, company',
  'MERGE (c:ProductionCompany {id: toInteger(company.id)})
   ON CREATE SET c.name = company.name
   WITH c, row
   MATCH (m:Movie {id: toInteger(row.id)})
   MERGE (m)-[:PRODUCED_BY]->(c)',
  {batchSize: 100, parallel: false}
);


//Step 6 — Import Production Countries


CALL apoc.periodic.iterate(
  'LOAD CSV WITH HEADERS FROM "file:///tmdb_5000_movies.csv" AS row
   WITH row WHERE row.production_countries IS NOT NULL
   WITH row, apoc.convert.fromJsonList(row.production_countries) AS countries
   UNWIND countries AS country RETURN row, country',
  'MERGE (pc:ProductionCountry {iso_3166_1: country.iso_3166_1})
   ON CREATE SET pc.name = country.name
   WITH pc, row
   MATCH (m:Movie {id: toInteger(row.id)})
   MERGE (m)-[:PRODUCED_IN]->(pc)',
  {batchSize: 100, parallel: false}
);


//Step 7 — Import Cast (from credits.csv)


CALL apoc.periodic.iterate(
  'LOAD CSV WITH HEADERS FROM "file:///properly_formatted_credits.csv" AS row RETURN row',
  'MATCH (m:Movie {id: toInteger(row.movie_id)})
   WITH m, apoc.convert.fromJsonList(row.cast) AS cast
   UNWIND cast AS actor
   MERGE (p:Person {id: toInteger(actor.id)})
   ON CREATE SET p.name = actor.name
   MERGE (p)-[:ACTED_IN {character: actor.character}]->(m)',
  {batchSize: 1, parallel: false}
);


//Step 8 — Import Crew / Directors (from credits.csv)


CALL apoc.periodic.iterate(
  'LOAD CSV WITH HEADERS FROM "file:///properly_formatted_credits.csv" AS row RETURN row',
  'MATCH (m:Movie {id: toInteger(row.movie_id)})
   WITH m, apoc.convert.fromJsonList(row.crew) AS crew
   UNWIND crew AS member
   WITH m, member WHERE member.job = "Director"
   MERGE (p:Person {id: toInteger(member.id)})
   ON CREATE SET p.name = member.name
   MERGE (p)-[:DIRECTED]->(m)',
  {batchSize: 1, parallel: false}
);


//Step 9 — Verify Final Counts

MATCH (n) RETURN labels(n) AS label, count(n) AS count ORDER BY count DESC;
MATCH ()-[r]->() RETURN type(r) AS relationship, count(r) AS count ORDER BY count DESC;