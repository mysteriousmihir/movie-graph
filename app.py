from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_session

app = Flask(__name__)
CORS(app)


# ── 1. Search movies by title ──────────────────────────────────────────────
@app.route("/api/search")
def search_movies():
    search_term = request.args.get("q", "").strip()
    if not search_term:
        return jsonify([])
    with get_session() as session:
        result = session.run(
            """
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($search_term)
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            RETURN m.id AS id, m.title AS title,
                   m.release_date AS release_date,
                   m.vote_average AS vote_average,
                   m.overview AS overview,
                   m.popularity AS popularity,
                   collect(DISTINCT g.name) AS genres
            ORDER BY m.vote_average DESC
            LIMIT 20
            """,
            search_term=search_term,
        )
        return jsonify([dict(r) for r in result])


# ── 2. Get all genres ──────────────────────────────────────────────────────
@app.route("/api/genres")
def get_genres():
    with get_session() as session:
        result = session.run(
            """
            MATCH (g:Genre)<-[:IN_GENRE]-(m:Movie)
            RETURN g.name AS name, count(m) AS movie_count
            ORDER BY movie_count DESC
            """
        )
        return jsonify([dict(r) for r in result])


# ── 3. Browse movies by genre ──────────────────────────────────────────────
@app.route("/api/genre/<genre_name>")
def movies_by_genre(genre_name):
    with get_session() as session:
        result = session.run(
            """
            MATCH (m:Movie)-[:IN_GENRE]->(g:Genre {name: $genre})
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g2:Genre)
            RETURN m.id AS id, m.title AS title,
                   m.release_date AS release_date,
                   m.vote_average AS vote_average,
                   m.overview AS overview,
                   collect(DISTINCT g2.name) AS genres
            ORDER BY m.vote_average DESC
            LIMIT 30
            """,
            genre=genre_name,
        )
        return jsonify([dict(r) for r in result])


# ── 4. Search actor & their movies ────────────────────────────────────────
@app.route("/api/actor")
def actor_movies():
    actor_name = request.args.get("name", "").strip()
    if not actor_name:
        return jsonify([])
    with get_session() as session:
        result = session.run(
            """
            MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
            WHERE toLower(p.name) CONTAINS toLower($actor_name)
            RETURN p.id AS actor_id, p.name AS actor_name,
                   m.id AS movie_id, m.title AS title,
                   m.release_date AS release_date,
                   m.vote_average AS vote_average,
                   r.character AS character
            ORDER BY m.release_date DESC
            LIMIT 50
            """,
            actor_name=actor_name,
        )
        rows = [dict(r) for r in result]
        actors = {}
        for row in rows:
            aid = row["actor_id"]
            if aid not in actors:
                actors[aid] = {"actor_name": row["actor_name"], "movies": []}
            actors[aid]["movies"].append({
                "movie_id": row["movie_id"],
                "title": row["title"],
                "release_date": row["release_date"],
                "vote_average": row["vote_average"],
                "character": row["character"],
            })
        return jsonify(list(actors.values()))


# ── 5. Movie recommendations ───────────────────────────────────────────────
@app.route("/api/recommend/<int:movie_id>")
def recommend(movie_id):
    with get_session() as session:
        result = session.run(
            """
            MATCH (m:Movie {id: $id})-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec:Movie)
            WHERE rec.id <> $id
            WITH rec, count(DISTINCT g) AS sharedGenres
            OPTIONAL MATCH (rec)-[:IN_GENRE]->(g2:Genre)
            RETURN rec.id AS id, rec.title AS title,
                   rec.vote_average AS vote_average,
                   rec.release_date AS release_date,
                   rec.overview AS overview,
                   sharedGenres,
                   collect(DISTINCT g2.name) AS genres
            ORDER BY sharedGenres DESC, rec.vote_average DESC
            LIMIT 10
            """,
            id=movie_id,
        )
        return jsonify([dict(r) for r in result])


# ── 6. Movie detail ────────────────────────────────────────────────────────
@app.route("/api/movie/<int:movie_id>")
def movie_detail(movie_id):
    with get_session() as session:
        movie = session.run(
            """
            MATCH (m:Movie {id: $id})
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(m)
            OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
            RETURN m.id AS id, m.title AS title, m.overview AS overview,
                   m.release_date AS release_date, m.runtime AS runtime,
                   m.vote_average AS vote_average, m.vote_count AS vote_count,
                   m.budget AS budget, m.revenue AS revenue, m.status AS status,
                   m.tagline AS tagline,
                   collect(DISTINCT g.name) AS genres,
                   collect(DISTINCT {name: p.name})[0..10] AS cast,
                   collect(DISTINCT {id: d.id, name: d.name}) AS directors
            """,
            id=movie_id,
        )
        row = movie.single()
        if not row:
            return jsonify({"error": "Movie not found"}), 404
        return jsonify(dict(row))


# ── 7. Director profile ────────────────────────────────────────────────────
@app.route("/api/director/<int:director_id>")
def director_profile(director_id):
    with get_session() as session:
        result = session.run(
            """
            MATCH (d:Person {id: $id})-[:DIRECTED]->(m:Movie)
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            RETURN d.id AS id, d.name AS name,
                   m.id AS movie_id, m.title AS title,
                   m.release_date AS release_date,
                   m.vote_average AS vote_average,
                   m.overview AS overview,
                   collect(DISTINCT g.name) AS genres
            ORDER BY m.release_date DESC
            """,
            id=director_id,
        )
        rows = [dict(r) for r in result]
        if not rows:
            return jsonify({"error": "Director not found"}), 404
        movies = [{
            "movie_id":     r["movie_id"],
            "title":        r["title"],
            "release_date": r["release_date"],
            "vote_average": r["vote_average"],
            "overview":     r["overview"],
            "genres":       r["genres"],
        } for r in rows]
        avg = round(sum(m["vote_average"] for m in movies if m["vote_average"]) / max(len(movies), 1), 1)
        return jsonify({
            "id":            rows[0]["id"],
            "name":          rows[0]["name"],
            "movie_count":   len(movies),
            "average_rating": avg,
            "movies":        movies,
        })


# ── 8. Search directors ────────────────────────────────────────────────────
@app.route("/api/directors/search")
def search_directors():
    director_name = request.args.get("name", "").strip()
    if not director_name:
        return jsonify([])
    with get_session() as session:
        result = session.run(
            """
            MATCH (d:Person)-[:DIRECTED]->(m:Movie)
            WHERE toLower(d.name) CONTAINS toLower($director_name)
            RETURN d.id AS id, d.name AS name,
                   count(m) AS movie_count,
                   round(avg(m.vote_average) * 10) / 10 AS avg_rating
            ORDER BY movie_count DESC
            LIMIT 10
            """,
            director_name=director_name,
        )
        return jsonify([dict(r) for r in result])


# ── 9. Graph data for a movie ──────────────────────────────────────────────
@app.route("/api/graph/movie/<int:movie_id>")
def graph_movie(movie_id):
    with get_session() as session:
        result = session.run(
            """
            MATCH (m:Movie {id: $id})
            OPTIONAL MATCH (a:Person)-[:ACTED_IN]->(m)
            OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            RETURN m.id AS movie_id, m.title AS movie_title,
                   collect(DISTINCT {id: a.id, name: a.name, type: 'actor'})[0..12] AS actors,
                   collect(DISTINCT {id: d.id, name: d.name, type: 'director'}) AS directors,
                   collect(DISTINCT {name: g.name, type: 'genre'}) AS genres
            """,
            id=movie_id,
        )
        row = result.single()
        if not row:
            return jsonify({"error": "Not found"}), 404

        nodes, links = [], []
        # Movie node
        nodes.append({"id": f"m_{row['movie_id']}", "label": row["movie_title"], "type": "movie"})
        # Actor nodes
        for a in row["actors"]:
            if a["id"]:
                nid = f"a_{a['id']}"
                nodes.append({"id": nid, "label": a["name"], "type": "actor"})
                links.append({"source": nid, "target": f"m_{row['movie_id']}", "label": "ACTED_IN"})
        # Director nodes
        for d in row["directors"]:
            if d["id"]:
                nid = f"d_{d['id']}"
                nodes.append({"id": nid, "label": d["name"], "type": "director"})
                links.append({"source": nid, "target": f"m_{row['movie_id']}", "label": "DIRECTED"})
        # Genre nodes
        for g in row["genres"]:
            nid = f"g_{g['name']}"
            nodes.append({"id": nid, "label": g["name"], "type": "genre"})
            links.append({"source": f"m_{row['movie_id']}", "target": nid, "label": "IN_GENRE"})

        return jsonify({"nodes": nodes, "links": links})


# ── 10. Graph explore — search any node ───────────────────────────────────
@app.route("/api/graph/explore")
def graph_explore():
    search_term = request.args.get("q", "").strip()
    if not search_term:
        return jsonify({"nodes": [], "links": []})
    with get_session() as session:
        result = session.run(
            """
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($search_term)
            WITH m LIMIT 1
            OPTIONAL MATCH (a:Person)-[:ACTED_IN]->(m)
            OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            RETURN m.id AS movie_id, m.title AS movie_title,
                   collect(DISTINCT {id: a.id, name: a.name})[0..10] AS actors,
                   collect(DISTINCT {id: d.id, name: d.name}) AS directors,
                   collect(DISTINCT {name: g.name}) AS genres
            """,
            search_term=search_term,
        )
        row = result.single()
        if not row:
            return jsonify({"nodes": [], "links": []})

        nodes, links = [], []
        nodes.append({"id": f"m_{row['movie_id']}", "label": row["movie_title"], "type": "movie"})
        for a in row["actors"]:
            if a["id"]:
                nid = f"a_{a['id']}"
                nodes.append({"id": nid, "label": a["name"], "type": "actor"})
                links.append({"source": nid, "target": f"m_{row['movie_id']}", "label": "ACTED_IN"})
        for d in row["directors"]:
            if d["id"]:
                nid = f"d_{d['id']}"
                nodes.append({"id": nid, "label": d["name"], "type": "director"})
                links.append({"source": nid, "target": f"m_{row['movie_id']}", "label": "DIRECTED"})
        for g in row["genres"]:
            nid = f"g_{g['name']}"
            nodes.append({"id": nid, "label": g["name"], "type": "genre"})
            links.append({"source": f"m_{row['movie_id']}", "target": nid, "label": "IN_GENRE"})

        return jsonify({"nodes": nodes, "links": links})


# ── 11. Actor connection finder (shortest path) ───────────────────────────
@app.route("/api/connect")
def actor_connect():
    name1 = request.args.get("a", "").strip()
    name2 = request.args.get("b", "").strip()
    if not name1 or not name2:
        return jsonify({"error": "Provide both actor names"}), 400
    with get_session() as session:
        result = session.run(
            """
            MATCH (a:Person), (b:Person)
            WHERE toLower(a.name) CONTAINS toLower($name1)
            AND   toLower(b.name) CONTAINS toLower($name2)
            WITH a, b LIMIT 1
            MATCH path = shortestPath((a)-[:ACTED_IN|DIRECTED*..10]-(b))
            RETURN
                [n IN nodes(path) | {
                    id:    CASE WHEN n:Person THEN n.id ELSE n.id END,
                    name:  CASE WHEN n:Person THEN n.name ELSE n.title END,
                    type:  CASE WHEN n:Person THEN 'person' ELSE 'movie' END
                }] AS path_nodes,
                length(path) AS hops
            """,
            name1=name1,
            name2=name2,
        )
        row = result.single()
        if not row:
            return jsonify({"error": "No connection found between these actors"}), 404
        return jsonify({"path": row["path_nodes"], "hops": row["hops"]})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
