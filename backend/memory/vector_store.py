"""
向量存储服务
使用 ChromaDB 存储和检索记忆向量
"""
import uuid
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings


class VectorStore:
    """向量存储类"""
    
    def __init__(self):
        """初始化 ChromaDB 客户端"""
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        
        # 创建持久化客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"description": "用户记忆向量存储"}
        )
    
    def add_memory(
        self,
        user_id: str,
        memory_id: str,
        content: str,
        category: str,
        importance: int
    ) -> bool:
        """
        添加记忆到向量存储
        
        Args:
            user_id: 用户ID
            memory_id: 记忆ID
            content: 记忆内容
            category: 记忆类别
            importance: 重要性
            
        Returns:
            是否成功
        """
        try:
            # 生成嵌入向量（使用内容本身作为元数据）
            self.collection.add(
                ids=[f"{user_id}_{memory_id}"],
                documents=[content],
                metadatas=[{
                    "user_id": user_id,
                    "memory_id": memory_id,
                    "category": category,
                    "importance": importance
                }]
            )
            return True
        except Exception as e:
            print(f"添加记忆失败: {e}")
            return False
    
    def search_memories(
        self,
        user_id: str,
        query: str,
        n_results: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索用户记忆
        
        Args:
            user_id: 用户ID
            query: 查询文本
            n_results: 返回数量
            category: 可选的类别过滤
            
        Returns:
            记忆列表
        """
        try:
            # 构建查询
            where_filter = {"user_id": user_id}
            if category:
                where_filter["category"] = category
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            # 解析结果
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
    
    def get_all_memories(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取用户所有记忆
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            记忆列表
        """
        try:
            # 获取所有记忆（按ID前缀过滤）
            results = self.collection.get(
                where={"user_id": user_id},
                limit=limit
            )
            
            memories = []
            if results and results["ids"]:
                for i, memory_id in enumerate(results["ids"]):
                    memories.append({
                        "memory_id": results["metadatas"][i].get("memory_id", ""),
                        "content": results["documents"][i],
                        "category": results["metadatas"][i].get("category", ""),
                        "importance": results["metadatas"][i].get("importance", 5)
                    })
            
            return memories
        except Exception as e:
            print(f"获取记忆失败: {e}")
            return []
    
    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """
        删除记忆
        
        Args:
            user_id: 用户ID
            memory_id: 记忆ID
            
        Returns:
            是否成功
        """
        try:
            self.collection.delete(ids=[f"{user_id}_{memory_id}"])
            return True
        except Exception as e:
            print(f"删除记忆失败: {e}")
            return False
    
    def delete_user_memories(self, user_id: str) -> bool:
        """
        删除用户所有记忆
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        try:
            self.collection.delete(where={"user_id": user_id})
            return True
        except Exception as e:
            print(f"删除用户记忆失败: {e}")
            return False
    
    def count_memories(self, user_id: str) -> int:
        """
        统计用户记忆数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            记忆数量
        """
        try:
            results = self.collection.get(
                where={"user_id": user_id},
                limit=1000
            )
            return len(results["ids"]) if results and results["ids"] else 0
        except Exception as e:
            print(f"统计记忆失败: {e}")
            return 0
    
    def reset(self) -> bool:
        """
        重置向量存储（危险操作）
        
        Returns:
            是否成功
        """
        try:
            self.client.delete_collection("memories")
            self.collection = self.client.get_or_create_collection(
                name="memories",
                metadata={"description": "用户记忆向量存储"}
            )
            return True
        except Exception as e:
            print(f"重置向量存储失败: {e}")
            return False


# 全局向量存储实例
vector_store = VectorStore()
