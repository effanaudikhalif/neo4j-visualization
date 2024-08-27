from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from neo4j import GraphDatabase

app = Flask(__name__)
CORS(app)

# Neo4j connection setup
uri = "bolt://localhost:7687"
username = "neo4j"
password = "Semarang12"
driver = GraphDatabase.driver(uri, auth=(username, password))

def get_db():
  return driver.session()

# Get everything
@app.route("/", methods=["GET"])
def get_all_data():
  query = """
  MATCH (n)  // Matches all nodes regardless of type
  OPTIONAL MATCH (n)-[r]-(m)  // Matches all relationships for each node
  RETURN n, collect(r) as relationships, collect(m) as connected_nodes
  """
  with get_db() as session:
      result = session.run(query)
      output = []

      for record in result:
          node = record["n"]
          relationships = record["relationships"]

          node_data = {
              "id": node.id,
              "labels": list(node.labels),
              "properties": dict(node)
          }

          node_data["relationships"] = [
              {
                  "id": rel.id,
                  "type": rel.type,
                  "start_node_id": rel.start_node.id,
                  "end_node_id": rel.end_node.id,
                  "properties": dict(rel)
              }
              for rel in relationships if rel is not None
          ]

          output.append(node_data)

      return jsonify(output)

if __name__ == "__main__":
  app.run(debug=True)
