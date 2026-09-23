import httpx
import json

r = httpx.get("http://localhost:8000/api/v1/materials")
data = r.json()
print("Status code:", r.status_code)
print("Total items:", len(data.get("items", [])))
for item in data.get("items", []):
    print(f"Material id={item['id']}, filename={item['original_filename']}")
    docs = item.get("documents", [])
    print(f"   docs count={len(docs)}")
    for d in docs:
        print(f"      doc id={d['id']}, title={d['title']}")

# Now test RAG search through the API directly!
print("\n--- Testing RAG Search via API ---")
# 1. No filter
rag_r1 = httpx.post("http://localhost:8000/api/v1/rag/search", json={
    "query": "What is the main problem this project solves?",
    "top_k": 5
})
print("Search without doc filter:")
print("Status:", rag_r1.status_code)
print(rag_r1.json())

# 2. With PRAGYA document_id
pragya_doc_id = "72a9be4e-b1e5-4c06-a5eb-263e696e1de1"
rag_r2 = httpx.post("http://localhost:8000/api/v1/rag/search", json={
    "query": "What is the main problem this project solves?",
    "top_k": 5,
    "document_id": pragya_doc_id
})
print("\nSearch with PRAGYA Document ID:", pragya_doc_id)
print("Status:", rag_r2.status_code)
print(rag_r2.json())

# 3. With PRAGYA material_id
pragya_mat_id = "a161b7fd-8de8-430e-bd08-1d8628354742"
rag_r3 = httpx.post("http://localhost:8000/api/v1/rag/search", json={
    "query": "What is the main problem this project solves?",
    "top_k": 5,
    "document_id": pragya_mat_id
})
print("\nSearch with PRAGYA Material ID:", pragya_mat_id)
print("Status:", rag_r3.status_code)
print(rag_r3.json())

# 4. Stratified sampling query
rag_r4 = httpx.post("http://localhost:8000/api/v1/rag/search", json={
    "query": "What is stratified sampling?",
    "top_k": 5
})
print("\nSearch 'What is stratified sampling?':")
print("Status:", rag_r4.status_code)
data4 = rag_r4.json()
print("RAG Status:", data4.get("status"))
print("Results count:", len(data4.get("results", [])))
for r in data4.get("results", []):
    print(f"  score={r['score']}, doc={r['document_title']}, page={r['page_number']}")

# 5. Known content query from PRAGYA
rag_r5 = httpx.post("http://localhost:8000/api/v1/rag/search", json={
    "query": "PRAGYA | SIH26101 | Master Project Context",
    "top_k": 5,
    "document_id": pragya_doc_id
})
print("\nSearch known content 'PRAGYA | SIH26101 | Master Project Context':")
print("Status:", rag_r5.status_code)
data5 = rag_r5.json()
print("RAG Status:", data5.get("status"))
print("Results count:", len(data5.get("results", [])))
for r in data5.get("results", []):
    print(f"  score={r['score']}, doc={r['document_title']}, page={r['page_number']}")

