import asyncio
import json
import re
import app.api.v1.api
from sqlalchemy import text, select
from app.db.session import AsyncSessionLocal
from app.modules.materials.models import UploadedMaterial, Document, DocumentChunk
from app.modules.competencies.models import Competency
from app.modules.materials.models import UploadedMaterial, Document, DocumentChunk
from app.modules.materials.embeddings import get_embedding_provider
from app.modules.materials.vector_store import PgVectorStore

async def main():
    async with AsyncSessionLocal() as session:
        print("==================================================")
        print("1. VERIFY DOCUMENT CHUNKS")
        print("==================================================")
        res = await session.execute(text("""
            SELECT 
                d.id as document_id, 
                d.title as document_title, 
                d.page_count,
                m.id as material_id,
                m.original_filename as material_filename,
                m.employee_id,
                m.status as material_status,
                count(c.id) as chunk_count
            FROM documents d
            JOIN uploaded_materials m ON d.uploaded_material_id = m.id
            LEFT JOIN document_chunks c ON c.document_id = d.id
            WHERE d.title ILIKE '%PRAGYA%' OR m.original_filename ILIKE '%PRAGYA%'
            GROUP BY d.id, d.title, d.page_count, m.id, m.original_filename, m.employee_id, m.status
        """))
        doc_rows = res.fetchall()
        for r in doc_rows:
            d = dict(r._mapping)
            print(f"Document ID: {d['document_id']}")
            print(f"Document Title: {d['document_title']}")
            print(f"Page Count: {d['page_count']}")
            print(f"Material ID: {d['material_id']}")
            print(f"Material Filename: {d['material_filename']}")
            print(f"Material Status: {d['material_status']}")
            print(f"Employee ID: {d['employee_id']}")
            print(f"Chunk Count: {d['chunk_count']}")

        if not doc_rows:
            print("No PRAGYA document found!")
            return

        doc_id = doc_rows[0]._mapping['document_id']
        material_id = doc_rows[0]._mapping['material_id']
        employee_id = doc_rows[0]._mapping['employee_id']

        # First 10 chunks
        chunk_res = await session.execute(text("""
            SELECT 
                id as chunk_id,
                chunk_index,
                page_number,
                vector_dims(embedding) as embedding_dim,
                embedding IS NOT NULL as has_embedding,
                length(text) as text_length,
                text
            FROM document_chunks
            WHERE document_id = :doc_id
            ORDER BY chunk_index ASC
            LIMIT 10
        """), {"doc_id": doc_id})
        chunks = chunk_res.fetchall()
        print(f"\nFirst {len(chunks)} chunks for document {doc_id}:")
        for c in chunks:
            cm = dict(c._mapping)
            snippet = cm['text'].replace('\n', ' ')[:150]
            print(f"Chunk [{cm['chunk_index']}]: id={cm['chunk_id']}, page={cm['page_number']}, dim={cm['embedding_dim']}, len={cm['text_length']}")
            print(f"  Snippet: {snippet}...\n")

        print("==================================================")
        print("2. SEARCH CHUNK TEXT DIRECTLY")
        print("==================================================")
        terms = ["PRAGYA", "SIH26101", "problem", "objective", "solution", "competency", "learning", "MoSPI"]
        for term in terms:
            term_res = await session.execute(text("""
                SELECT count(*) as cnt
                FROM document_chunks
                WHERE document_id = :doc_id AND text ILIKE :term
            """), {"doc_id": doc_id, "term": f"%{term}%"})
            cnt = term_res.scalar()
            print(f"Term '{term}': {cnt} matching chunks")

        print("\n==================================================")
        print("3. VERIFY EMBEDDING DATA")
        print("==================================================")
        emb_res = await session.execute(text("""
            SELECT 
                count(*) as total_chunks,
                count(embedding) as chunks_with_embedding,
                min(vector_dims(embedding)) as min_dim,
                max(vector_dims(embedding)) as max_dim
            FROM document_chunks
            WHERE document_id = :doc_id
        """), {"doc_id": doc_id})
        emb_data = dict(emb_res.fetchone()._mapping)
        print(f"Total Chunks: {emb_data['total_chunks']}")
        print(f"Chunks with non-null embedding: {emb_data['chunks_with_embedding']}")
        print(f"Embedding dimension: min={emb_data['min_dim']}, max={emb_data['max_dim']} (Expected 384)")

        print("\n==================================================")
        print("8. VERIFY QUERY EMBEDDING")
        print("==================================================")
        provider = get_embedding_provider()
        print(f"Embedding provider: {type(provider).__name__}")
        q1 = "What is the main problem this project solves?"
        q1_emb = provider.embed_text(q1)
        print(f"Query 1 embedding length: {len(q1_emb)}")
        print(f"Has nulls: {any(v is None for v in q1_emb)}")
        print(f"Sample values (first 5): {q1_emb[:5]}")

        print("\n==================================================")
        print("4. BYPASS 0.50 THRESHOLD FOR DEBUGGING (Query A)")
        print("==================================================")
        # Using DocumentChunk.embedding.cosine_distance(q1_emb) via ORM exactly as vector_store does
        dist_expr = DocumentChunk.embedding.cosine_distance(q1_emb).label("distance")
        stmt = (
            select(DocumentChunk, Document.title.label("doc_title"), dist_expr)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(DocumentChunk.document_id == doc_id)
            .order_by(dist_expr.asc())
            .limit(10)
        )
        raw_res = await session.execute(stmt)
        raw_rows = raw_res.all()
        for idx, (chunk, doc_title, distance) in enumerate(raw_rows, 1):
            sim = 1.0 - float(distance) if distance is not None else 0.0
            print(f"Rank {idx}:")
            print(f"  chunk_id: {chunk.id}")
            print(f"  document: {doc_title}")
            print(f"  page: {chunk.page_number}")
            print(f"  cosine distance: {float(distance):.6f}")
            print(f"  similarity score: {sim:.6f}")
            print(f"  first 200 chars: {chunk.text.replace(chr(10), ' ')[:200]}")

        print("\n==================================================")
        print("5. TEST THREE QUERIES (RAW)")
        print("==================================================")
        queries = [
            ("A", "What is the main problem this project solves?"),
            ("B", "What is PRAGYA?"),
            ("C", "What is SIH26101?")
        ]
        for label, q_text in queries:
            q_emb = provider.embed_text(q_text)
            d_expr = DocumentChunk.embedding.cosine_distance(q_emb).label("distance")
            q_stmt = (
                select(DocumentChunk, d_expr)
                .where(DocumentChunk.document_id == doc_id)
                .order_by(d_expr.asc())
                .limit(5)
            )
            top_rows = (await session.execute(q_stmt)).all()
            print(f"\nQuery {label}: '{q_text}'")
            for i, (ch, dist) in enumerate(top_rows, 1):
                sim = 1.0 - float(dist) if dist is not None else 0.0
                print(f"  #{i}: score={sim:.4f}, dist={float(dist):.4f}, p.{ch.page_number}: {ch.text[:80].replace(chr(10), ' ')}")

        print("\n==================================================")
        print("6. TEST A DIRECT TEXT QUERY")
        print("==================================================")
        for term in ["PRAGYA", "problem", "competency"]:
            res = await session.execute(text("""
                SELECT c.id, c.page_number, c.text
                FROM document_chunks c
                WHERE c.document_id = :doc_id AND c.text ILIKE :term
                LIMIT 2
            """), {"doc_id": doc_id, "term": f"%{term}%"})
            rows = res.fetchall()
            print(f"Term '{term}' matches ({len(rows)} samples):")
            for r in rows:
                rm = dict(r._mapping)
                print(f"  Chunk {rm['id']} (p.{rm['page_number']}): {rm['text'][:120].replace(chr(10), ' ')}...")

        print("\n==================================================")
        print("9. CHECK CHUNKING METRICS")
        print("==================================================")
        metrics_res = await session.execute(text("""
            SELECT 
                d.page_count,
                count(c.id) as num_chunks,
                avg(length(c.text)) as avg_len,
                min(length(c.text)) as min_len,
                max(length(c.text)) as max_len
            FROM documents d
            LEFT JOIN document_chunks c ON c.document_id = d.id
            WHERE d.id = :doc_id
            GROUP BY d.page_count
        """), {"doc_id": doc_id})
        metrics = dict(metrics_res.fetchone()._mapping)
        print(f"Page count: {metrics['page_count']}")
        print(f"Number of chunks: {metrics['num_chunks']}")
        print(f"Average chunk length: {metrics['avg_len']:.1f} chars")
        print(f"Minimum chunk length: {metrics['min_len']} chars")
        print(f"Maximum chunk length: {metrics['max_len']} chars")

        print("\n==================================================")
        print("12. TEST KNOWN-CONTENT QUERY")
        print("==================================================")
        first_chunk_text = chunks[0]._mapping['text']
        sentences = [s.strip() for s in re.split(r'\. |\n', first_chunk_text) if len(s.strip()) > 30]
        exact_sentence = sentences[0] if sentences else first_chunk_text[:100]
        print(f"Exact sentence query: \"{exact_sentence}\"")
        s_emb = provider.embed_text(exact_sentence)
        s_d_expr = DocumentChunk.embedding.cosine_distance(s_emb).label("distance")
        s_stmt = (
            select(DocumentChunk, s_d_expr)
            .where(DocumentChunk.document_id == doc_id)
            .order_by(s_d_expr.asc())
            .limit(3)
        )
        s_rows = (await session.execute(s_stmt)).all()
        for i, (sch, sdist) in enumerate(s_rows, 1):
            ssim = 1.0 - float(sdist) if sdist is not None else 0.0
            print(f"  #{i}: score={ssim:.4f}, dist={float(sdist):.4f}, p.{sch.page_number}: {sch.text[:100].replace(chr(10), ' ')}")

        print("\n==================================================")
        print("7. INVESTIGATE DOCUMENT FILTER / FRONTEND & BACKEND")
        print("==================================================")
        print(f"PRAGYA Document ID: {doc_id}")
        print(f"PRAGYA Material ID: {material_id}")
        print(f"PRAGYA Employee ID: {employee_id}")
        
        all_mat = await session.execute(text("""
            SELECT m.id as material_id, m.original_filename, m.employee_id, d.id as doc_id, d.title
            FROM uploaded_materials m
            LEFT JOIN documents d ON d.uploaded_material_id = m.id
        """))
        print("\nAll Materials in DB:")
        for m in all_mat.fetchall():
            print(dict(m._mapping))

        # Test search with PgVectorStore directly using both document_id and material_id
        store = PgVectorStore(session)
        res_with_doc_id = await store.search(
            query_embedding=q1_emb,
            query_text=q1,
            employee_id=employee_id,
            top_k=5,
            document_id=doc_id
        )
        print(f"\nPgVectorStore.search with document_id={doc_id}: {len(res_with_doc_id)} results")
        for r in res_with_doc_id:
            print(f"  score={r.score}, chunk_id={r.chunk_id}, p.{r.page_number}")

        res_with_mat_id = await store.search(
            query_embedding=q1_emb,
            query_text=q1,
            employee_id=employee_id,
            top_k=5,
            document_id=material_id
        )
        print(f"\nPgVectorStore.search with document_id set to material_id={material_id}: {len(res_with_mat_id)} results")

if __name__ == "__main__":
    asyncio.run(main())
