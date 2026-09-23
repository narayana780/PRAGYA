import asyncio
import app.api.v1.api
from sqlalchemy import select, func, text
from app.db.session import AsyncSessionLocal
from app.modules.materials.models import Document, DocumentChunk, UploadedMaterial, MaterialStatus
from app.modules.materials.embeddings import LocalEmbeddingProvider

async def reindex():
    print("=== STARTING DOCUMENT RE-INDEXING WITH REAL LOCAL EMBEDDINGS ===")
    provider = LocalEmbeddingProvider()
    print(f"Loaded provider: {type(provider).__name__}, Dimension: {provider.dimension}")
    assert provider.dimension == 384, f"Dimension mismatch: expected 384, got {provider.dimension}"

    async with AsyncSessionLocal() as session:
        # Check all documents
        doc_stmt = (
            select(Document, UploadedMaterial)
            .join(UploadedMaterial, UploadedMaterial.id == Document.uploaded_material_id)
            .where(UploadedMaterial.status == MaterialStatus.PROCESSED)
            .order_by(Document.created_at.asc())
        )
        docs = (await session.execute(doc_stmt)).all()
        print(f"Found {len(docs)} processed documents to re-embed:")
        for doc, mat in docs:
            print(f" - Doc ID: {doc.id}, Title: {doc.title}, Mat ID: {mat.id}, File: {mat.original_filename}")

        # Total chunks before reindex
        total_chunks_before = await session.scalar(
            select(func.count(DocumentChunk.id))
        )
        print(f"\nTotal document chunks in database before reindex: {total_chunks_before}")

        total_updated = 0
        for doc, mat in docs:
            chunk_stmt = (
                select(DocumentChunk)
                .where(DocumentChunk.document_id == doc.id)
                .order_by(DocumentChunk.chunk_index.asc())
            )
            chunks = (await session.execute(chunk_stmt)).scalars().all()
            print(f"\nRe-indexing Doc '{doc.title}' ({mat.original_filename}): {len(chunks)} chunks")
            
            chunk_texts = [c.text for c in chunks]
            real_embeddings = provider.embed_batch(chunk_texts)
            assert len(real_embeddings) == len(chunks), "Batch size mismatch"

            for c, emb in zip(chunks, real_embeddings):
                assert len(emb) == 384, f"Chunk {c.id} generated vector of dim {len(emb)}, expected 384"
                c.embedding = emb
                total_updated += 1
            
            await session.flush()
            print(f"  Successfully updated {len(chunks)} chunk embeddings in memory for {mat.original_filename}")

        # Commit transaction
        await session.commit()
        print(f"\n=== TRANSACTION COMMITTED: {total_updated} chunks re-embedded ===")

        # Verification
        total_chunks_after = await session.scalar(select(func.count(DocumentChunk.id)))
        assert total_chunks_after == total_chunks_before, f"Chunk count changed! Before: {total_chunks_before}, After: {total_chunks_after}"
        print(f"Chunk count verified unchanged: {total_chunks_after}")

        # Verify dimension on PostgreSQL vector column
        dim_check = await session.execute(text("""
            SELECT 
                d.title,
                count(c.id) as chunk_count,
                count(c.embedding) as emb_count,
                min(vector_dims(c.embedding)) as min_dim,
                max(vector_dims(c.embedding)) as max_dim
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            GROUP BY d.title
        """))
        print("\nPostgreSQL Vector Index Status by Document:")
        for row in dim_check.fetchall():
            rm = dict(row._mapping)
            print(f" - {rm['title']}: chunks={rm['chunk_count']}, embeddings={rm['emb_count']}, dims={rm['min_dim']}-{rm['max_dim']}")
            assert rm['chunk_count'] == rm['emb_count'], "Missing embeddings!"
            assert rm['min_dim'] == 384 and rm['max_dim'] == 384, "Dimension mismatch in pgvector!"

    print("\nRE-INDEX COMPLETE AND VERIFIED 100% SUCCESS!")

if __name__ == "__main__":
    asyncio.run(reindex())
