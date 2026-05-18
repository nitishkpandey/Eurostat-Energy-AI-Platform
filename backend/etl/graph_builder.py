"""
Knowledge Graph Builder (Neo4j)
Reads the transformed energy data from PostgreSQL and builds a semantic graph in Neo4j.
This enables GraphRAG (multi-hop semantic reasoning) over energy supply chains.
"""

import os
import logging
import pandas as pd
from neo4j import GraphDatabase
from backend.core.database import get_engine

logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "energy_graph_pass")

def load_data_from_pg() -> pd.DataFrame:
    engine = get_engine()
    query = """
    SELECT 
        country_code, 
        country_name, 
        indicator_code, 
        indicator_label,
        year,
        value,
        unit_label
    FROM observations
    WHERE year = 2023 -- Limit to recent year for graph simplicity
    """
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        logger.error(f"Failed to read from PostgreSQL: {e}")
        return pd.DataFrame()


def build_knowledge_graph():
    df = load_data_from_pg()
    if df.empty:
        logger.warning("No data found in PostgreSQL to build the graph.")
        return

    logger.info(f"Building Knowledge Graph with {len(df)} relationships...")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    with driver.session() as session:
        # Clear existing graph
        session.run("MATCH (n) DETACH DELETE n")

        for _, row in df.iterrows():
            country = row['country_name']
            indicator = row['indicator_label']
            val = float(row['value'])
            unit = row['unit_label']

            # Cypher Query to create Nodes and Relationships
            cypher = """
            MERGE (c:Country {name: $country})
            MERGE (i:EnergyIndicator {name: $indicator, unit: $unit})
            MERGE (c)-[r:REPORTS_ENERGY {year: 2023, amount: $val}]->(i)
            """
            
            session.run(cypher, country=country, indicator=indicator, val=val, unit=unit)
    
    driver.close()
    logger.info("Knowledge Graph successfully built in Neo4j.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_knowledge_graph()
