"""
Hybrid retrieval: merge BM25 (keyword) + Pinecone (semantic) rankings via RRF.

    python 04_hybrid_search.py --query "What is step therapy?"

Requires: scripts/02_bm25_search.py's BM25 leg and scripts/03_pinecone_upsert.py's
Pinecone leg both working. Runs both, merges rankings by rank position (not raw
score), prints the fused top chunk_ids.
"""

from __future__ import annotations

import argparse
import importlib
import os
import cohere
import re

from openai import OpenAI
from pathlib import Path

from dotenv import load_dotenv

bm25_module = importlib.import_module("02_bm25_search")
pinecone_module = importlib.import_module("03_pinecone_upsert")

CHUNKS_PATH = bm25_module.CHUNKS_PATH
DEFAULT_TOP_K = bm25_module.DEFAULT_TOP_K

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hybrid retrieval: BM25 + Pinecone merged via RRF."
    )
    parser.add_argument("--query", "-q", type=str, required=True, help="Retrieval query.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Chunks per leg.")
    parser.add_argument("--backend", choices=["cohere", "openai"], default="openai", help="Which chat backend to use for grounded generation.")
    parser.add_argument("--role", choices=["adjuster", "member"], default="adjuster", help="Caller's role for access filtering.")
    return parser

def combine_rrf(
    bm25_hits: list[tuple[float, dict[str, str]]],
    pinecone_matches: list,
    k: int = 60,
) -> list[tuple[float, str]]:
    bm25_ranks = {row["chunk_id"]: rank for rank, (score, row) in enumerate(bm25_hits, start=1)}
    pinecone_ranks = {match.id: rank for rank, match in enumerate(pinecone_matches, start=1)}
    all_chunk_ids = set(bm25_ranks) | set(pinecone_ranks)
    fused_scores = {
        chunk_id: 1 / (k + bm25_ranks.get(chunk_id, float("inf"))) + 1 / (k + pinecone_ranks.get(chunk_id, float("inf")))
        for chunk_id in all_chunk_ids
    }
    ranked = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)
    return ranked[:len(bm25_hits)]

def get_cohere_client() -> cohere.Client:
    api_key = pinecone_module.require_env("COHERE_API_KEY")
    return cohere.Client(api_key=api_key)

def get_openai_client() -> "OpenAI":
    api_key = pinecone_module.require_env("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)

def main() -> None:
    args = build_parser().parse_args()
    chunks = bm25_module.load_chunks(CHUNKS_PATH)
    chunks = [row for row in chunks if args.role in row["allowed_roles"]]
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")

    bm25_hits = bm25_module.retrieve(args.query, chunks, top_k=args.top_k)
    print(f"Query: {args.query}")
    print("--- BM25 leg ---")
    for rank, (score, row) in enumerate(bm25_hits, start=1):
        print(f"{rank}. score={score:.3f} chunk_id={row["chunk_id"]}")

    endpoint = pinecone_module.require_env("AZURE_OPENAI_ENDPOINT")
    api_key = pinecone_module.require_env("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    deployment = pinecone_module.require_env("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    client = pinecone_module.AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )

    query_vector = pinecone_module.embed_text(client, deployment, args.query)
    index = pinecone_module.get_pinecone_index()
    result = index.query(vector=query_vector, top_k=args.top_k, include_metadata=True, filter={"allowed_roles": {"$in": [args.role]}})

    print("--- Pinecone leg ---")
    for rank, match in enumerate(result.matches, start=1):
        print(f"{rank}. score={match.score:.3f} chunk_id={match.id}")
    rrf = combine_rrf(bm25_hits, result.matches)
    print(f"rrf = {rrf}")

    cohere_client = get_cohere_client()
    chunks_by_id = {row["chunk_id"]: row for row in chunks}
    print(f"chunk_by_id keys = {list(chunks_by_id.keys())}")
    documents = [chunks_by_id[chunk_id]["text"] for chunk_id, score in rrf]
    print(f"documents")
    for doc in documents:
        print(f"  - {doc}\n")
    rerank_result = cohere_client.rerank(
        query=args.query,
        documents=documents,
        model="rerank-v3.5",
        top_n=len(documents)
    )
    # print(f"rerank_result = ", rerank_result)
    print(f"rerank_result.results: ")
    for item in rerank_result.results:
        print(f"  index={item.index} relevance_score={item.relevance_score:.4f}")
    chunk_ids = [chunk_id for chunk_id, score in rrf]
    final = [(chunk_ids[item.index], item.relevance_score) for item in rerank_result.results]
    print(f"final: {final}")
    chat_documents = [{ "id": chunk_id, "text": chunks_by_id[chunk_id]["text"]} for chunk_id, score in final]
    print("chat_documents")
    for doc in chat_documents:
        print(f"id: {doc["id"]} text={doc["text"][:60]}")

    if args.backend == "cohere":
        chat_response = cohere_client.chat(message=args.query, documents=chat_documents, model="command-a-03-2025")
        print(f"chat_response.text", chat_response.text)
        print("chat_response.citations")
        for citation in chat_response.citations:
            print(f"  text={citation.text!r} document_ids={citation.document_ids}")
    else: 
        context_block = "\n\n".join(f"[{doc['id']}] {doc['text']}" for doc in chat_documents)
        system_prompt = "Answer only using the provided documents. After each sentence, cite the document id(s) it came from in square brackets, like [C0002]. If the documents don't contain the answer, say so."                                                                                                                   
        open_ai_client = get_openai_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context_block}\n\nQuestion: {args.query}"}
        ]
        openai_response = open_ai_client.chat.completions.create(model="gpt-5.6-luna", messages=messages)
        print(f"openai_response.choices[0].message.content: ", openai_response.choices[0].message.content)
        openai_citations = re.findall(r"\[(C\d+)\]", openai_response.choices[0].message.content)
        print(f"openai_citations", openai_citations)

    

if __name__ == "__main__":
    main()
