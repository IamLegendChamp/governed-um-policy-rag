
import networkx as nx
import importlib

from pathlib import Path
CHUNKS_PATH = Path(__file__).resolve().parent.parent / "data" / "chunks" / "chunks.jsonl"

CONCEPTS = ["appeal", "formulary", "audit", "retrieval", "prior authorization", "medical necessity"]

def main() -> None:
    graph = nx.Graph()
    graph.add_node("audit log", chunk_ids=["C0006", "C0007"])
    graph.add_node("retrieval log", chunk_ids=["C0007", "C0008"])
    graph.add_edge("audit log", "retrieval log", shared_chunks=["C0007"])
    neighbors = list(graph.neighbors("audit log"))
    neighbor_chunks = graph.nodes[neighbors[0]]["chunk_ids"]
    bm25_module = importlib.import_module("02_bm25_search")
    chunks = bm25_module.load_chunks(CHUNKS_PATH)

    appeal_ids = [row["chunk_id"] for row in chunks if "appeal" in row["text"].lower()]

if __name__ == "__main__":
    main()
