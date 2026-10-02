

import networkx as nx
import importlib

from pathlib import Path
CHUNKS_PATH = Path(__file__).resolve().parent.parent / "data" / "chunks" / "chunks.jsonl"

CONCEPTS = ["appeal", "formulary", "audit", "retrieval", "prior authorization", "medical necessity"]

def main() -> None:
    graph = nx.Graph()
    print(f"empty graph: nodes={graph.number_of_nodes()} edges={graph.number_of_edges()}")
    graph.add_node("audit log", chunk_ids=["C0006", "C0007"])
    print(f"after add_node: nodes={graph.number_of_nodes()} edges={graph.number_of_edges()} data={graph.nodes['audit log']}")
    graph.add_node("retrieval log", chunk_ids=["C0007", "C0008"])
    graph.add_edge("audit log", "retrieval log", shared_chunks=["C0007"])
    print(f"after add_edge: nodes={graph.number_of_nodes()} edges={graph.number_of_edges()} edge_data={graph.edges['audit log', 'retrieval log']}")
    neighbors = list(graph.neighbors("audit log"))
    print(f"neighbors of 'audit log': {neighbors}")
    neighbor_chunks = graph.nodes[neighbors[0]]["chunk_ids"]
    print(f"chunks reached via neighbor: {neighbor_chunks}")
    print(f"chunks path: {CHUNKS_PATH} exists={CHUNKS_PATH.exists()}")
    bm25_module = importlib.import_module("02_bm25_search")
    chunks = bm25_module.load_chunks(CHUNKS_PATH)
    print(f"loaded {len(chunks)} chunks; first={chunks[0]['chunk_id']}; C0007 text starts: {chunks[7]['text'][:80]!r}")

    appeal_ids = [row["chunk_id"] for row in chunks if "appeal" in row["text"].lower()]
    print(f"chunks mentioning 'appeal': {appeal_ids}")
    

if __name__ == "__main__":
    main()
