import asyncio
import httpx
from uuid import UUID
import app.api.v1.api
from app.db.session import AsyncSessionLocal
from app.modules.materials.service import MaterialService
from app.modules.materials.embeddings import get_embedding_provider
from app.core.config import settings

async def run_suite():
    print("==================================================")
    print("PRAGYA RETRIEVAL SUITE WITH REAL SENTENCE TRANSFORMERS")
    print("==================================================")
    print(f"Active EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")
    print(f"Active EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
    provider = get_embedding_provider()
    print(f"Provider class: {type(provider).__name__}")
    print(f"Model dimension: {provider.dimension}")
    print(f"Threshold: {settings.MIN_RETRIEVAL_SCORE}")
    print("--------------------------------------------------\n")

    queries = [
        ("A", "What is the main problem this project solves?"),
        ("B", "What is PRAGYA?"),
        ("C", "What is SIH26101?"),
        ("D", "What is the skill gap engine?"),
        ("E", "What is stratified sampling?"),
        ("F", "What is the capital of Japan?")
    ]

    emp_id = UUID("e85b4b98-7177-4c62-8eee-6c6f5702c04a") # Ananya Sharma

    async with AsyncSessionLocal() as session:
        service = MaterialService(session)
        for label, q in queries:
            results, is_vec, status, message = await service.retrieve_evidence(
                employee_id=emp_id,
                query=q,
                top_k=5
            )
            print(f"Query {label}: \"{q}\"")
            print(f"  Retrieval Status: {status}")
            print(f"  Vector Active: {is_vec}")
            if results:
                top = results[0]
                print(f"  Top Score: {top.score:.4f}")
                print(f"  Top Document: {top.document_title}")
                print(f"  Page: {top.page_number}")
                snippet = top.text.replace("\n", " ")[:150]
                print(f"  Snippet: {snippet}...")
                print(f"  Total Chunks Above Threshold: {len(results)}")
                for idx, r in enumerate(results[1:3], 2):
                    print(f"    #{idx} Score: {r.score:.4f} | Doc: {r.document_title} (p.{r.page_number})")
            else:
                print(f"  Top Score: N/A (< {settings.MIN_RETRIEVAL_SCORE})")
                print(f"  Top Document: None")
                print(f"  Page: None")
                print(f"  Message: {message}")
            print()

        # Also test raw vector scores without threshold for inspection
        print("=== RAW (UNFILTERED) VECTOR SCORES ===")
        raw_provider = provider
        for label, q in queries:
            q_emb = raw_provider.embed_text(q)
            raw_res = await service.vector_store.search(
                query_embedding=q_emb,
                query_text=q,
                employee_id=emp_id,
                top_k=3
            )
            top_raw = raw_res[0] if raw_res else None
            if top_raw:
                print(f"Query {label} [RAW]: top_score={top_raw.score:.4f} | doc={top_raw.document_title} (p.{top_raw.page_number})")
            else:
                print(f"Query {label} [RAW]: No matches")

if __name__ == "__main__":
    asyncio.run(run_suite())
