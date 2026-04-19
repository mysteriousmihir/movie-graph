from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def get_session():
    return driver.session(database=DATABASE)

def close():
    driver.close()