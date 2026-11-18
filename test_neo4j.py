
import os
import ssl
import certifi
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configure trusted CA certificates
os.environ["SSL_CERT_FILE"] = certifi.where()

ssl_context = ssl.create_default_context(
    cafile=certifi.where()
)

# Neo4j credentials
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

print("URI loaded:", bool(uri))
print("Username loaded:", bool(username))
print("Password loaded:", bool(password))
print("CA certificate:", certifi.where())

try:
    driver = GraphDatabase.driver(
        uri.replace("neo4j+s://", "neo4j://"),
        auth=(username, password),
        encrypted=True,
        ssl_context=ssl_context
    )

    driver.verify_connectivity()

    with driver.session() as session:
        result = session.run(
            "RETURN 'Neo4j Connected Successfully' AS message"
        )

        print(result.single()["message"])

    driver.close()

except Exception as error:
    print("Connection failed:")
    print(type(error).__name__, error)
