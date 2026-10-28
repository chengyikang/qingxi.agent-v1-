"""向量存储服务 - ChromaDB"""
import uuid
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings


class VectorStore:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"description": "用户记忆向量存储"}
        )
    
    def add_memory(self, user_id, memory_id, content, category, importance):
        try:
            self.collection.add(
                ids=[f"{user_id}_{memory_id}"],
                documents=[content],
                metadatas=[{"user_id": user_id, "memory_id": memory_id, "category": category, "importance": importance}]
            )
            return True
        except Exception as e:
            print(f"添加记忆失败: {e}")
            return False
    
    def search_memories(self, user_id, query, n_results=5, category=None):
        try:
            where_filter = {"user_id": user_id}
            if category:
                where_filter["category"] = category
            results = self.collection.query(query_texts=[query], n_results=n_results, where=where_filter)
            memories = []
            if results and results["ids"]:
                for i, memory_id in enumerate(results["ids"][0]):
                    memories.append({
                        "memory_id": results["metadatas"][0][i].get("memory_id", ""),
                        "content": results["documents"][0][i],
                        "category": results["metadatas"][0][i].get("category", ""),
                        "importance": results["metadatas"][0][i].get("importance", 5),
                        "distance": results["distances"][0][i] if "distances" in results else 0
                    })
            return memories
        except Exception as e:
            print(f"搜索记忆失败: {e}")
            return []
    
    def count_memories(self, user_id):
        try:
            return self.collection.count(where={"user_id": user_id})
        except:
            return 0
    
    def delete_memory(self, user_id, memory_id):
        try:
            self.collection.delete(ids=[f"{user_id}_{memory_id}"])
            return True
        except:
            return False


vector_store = VectorStore()
