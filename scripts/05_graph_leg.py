

import networkx as nx

def main() -> None:
    graph = nx.Graph()
    print(f"empty graph: nodes={graph.number_of_nodes()} edges={graph.number_of_edges()}")


if __name__ == "__main__":
    main()
