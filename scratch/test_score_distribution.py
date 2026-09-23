import asyncio
import app.api.v1.api
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.modules.materials.models import DocumentChunk, Document
from app.modules.materials.embeddings import get_embedding_provider

async def test_scores():
    async with AsyncSessionLocal() as session:
        provider = get_embedding_provider()
        queries = [
            "What is the main problem this project solves?",
            "What is PRAGYA?",
            "What is SIH26101?",
            "What is stratified sampling?",
            "What is the capital of Japan?",
            "Who won the 1998 World Cup?",
            "PRAGYA AI-Powered Competency & Personalized Learning Platform"
        ]
        
        doc_id = "72a9be4e-b1e5-4c06-a5eb-263e696e1de1" # PRAGYA
        print("=== COSINE SIMILARITY SCORES FOR PRAGYA DOC ===")
        for q in queries:
            q_emb = provider.embed_text(q)
            dist_expr = DocumentChunk.embedding.cosine_distance(q_emb).label("distance")
            stmt = (
                select(DocumentChunk, dist_expr)
                .where(DocumentChunk.document_id == doc_id)
                .order_by(dist_expr.asc())
                .limit(3)
            )
            rows = (await session.execute(stmt)).all()
            top_sim = 1.0 - float(rows[0][1]) if rows else 0.0
            print(f"Query: \"{q}\"")
            for rank, (chunk, dist) in enumerate(rows, 1):
                sim = 1.0 - float(dist)
                snippet = chunk.text.replace("\n", " ")[:60]
                print(f"   #{rank} score={sim:.4f} (dist={float(dist):.4f}) p.{chunk.page_number}: {snippet}...")

        # Also test on Sampling Manual
        sampling_doc_res = await session.execute(select(Document).where(Document.title.ilike("%Sampling%")).limit(1))
        sampling_doc = sampling_doc_res.scalar()
        if sampling_doc:
            print(f"\n=== COSINE SIMILARITY SCORES FOR SAMPLING MANUAL ({sampling_doc.id}) ===")
            for q in [
                "What is stratified sampling?",
                "What is the main problem this project solves?",
                "What is the capital of Japan?"
            ]:
                q_emb = provider.embed_text(q)
                dist_expr = DocumentChunk.embedding.cosine_distance(q_emb).label("distance")
                stmt = (
                    select(DocumentChunk, dist_expr)
                    .where(DocumentChunk.document_id == sampling_doc.id)
                    .order_by(dist_expr.asc())
                    .limit(3)
                )
                rows = (await session.execute(stmt)).all()
                print(f"Query: \"{q}\"")
                for rank, (chunk, dist) in enumerate(rows, 1):
                    sim = 1.0 - float(dist)
                    snippet = chunk.text.replace("\n", " ")[:60]
                    print(f"   #{rank} score={sim:.4f} (dist={float(dist):.4f}) p.{chunk.page_number}: {snippet}...")

if __name__ == "__main__":
    asyncio.run(test_scores())
