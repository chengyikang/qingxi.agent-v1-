"""
Module 01: Life Import Engine
用户人生资料导入引擎
支持 QQ/微信聊天记录、TXT、Markdown、PDF、DOCX、日记、笔记等格式
"""
import os
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class LifeImportEngine:
    """人生资料导入引擎"""
    
    # 支持的文件格式
    SUPPORTED_EXTENSIONS = {
        ".txt": "txt",
        ".md": "markdown",
        ".markdown": "markdown",
        ".pdf": "pdf",
        ".docx": "docx",
    }
    
    # 聊天记录格式标识
    CHAT_FORMAT_MARKERS = {
        "qq_chat": ["QQ聊天记录", "消息记录", "Chat Record"],
        "wechat_chat": ["微信聊天记录", "WeChat", "聊天记录"],
    }
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.preview_length = 1000
    
    def detect_source_type(self, file_name: str, content_preview: str = "") -> str:
        """检测文件来源类型"""
        ext = Path(file_name).suffix.lower()
        
        # 先检测聊天记录格式
        if content_preview:
            for source_type, markers in self.CHAT_FORMAT_MARKERS.items():
                for marker in markers:
                    if marker in content_preview:
                        return source_type
        
        # 再按扩展名
        if ext in self.SUPPORTED_EXTENSIONS:
            return self.SUPPORTED_EXTENSIONS[ext]
        
        # 按文件名关键词
        name_lower = file_name.lower()
        if "diary" in name_lower or "日记" in name_lower:
            return "diary"
        if "note" in name_lower or "笔记" in name_lower:
            return "note"
        if "chat" in name_lower or "聊天" in name_lower:
            return "qq_chat"
        
        return "txt"  # 默认
    
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """读取文件内容"""
        path = Path(file_path)
        
        if not path.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        if path.stat().st_size > self.max_file_size:
            return {"error": f"文件过大，最大支持 {self.max_file_size // 1024 // 1024}MB"}
        
        ext = path.suffix.lower()
        
        try:
            if ext in [".txt", ".md", ".markdown"]:
                return await self._read_text(path)
            elif ext == ".pdf":
                return await self._read_pdf(path)
            elif ext == ".docx":
                return await self._read_docx(path)
            else:
                return {"error": f"不支持的文件格式: {ext}"}
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return {"error": str(e)}
    
    async def _read_text(self, path: Path) -> Dict[str, Any]:
        """读取文本文件"""
        try:
            # 尝试多种编码
            for encoding in ["utf-8", "gbk", "gb2312", "utf-16"]:
                try:
                    content = path.read_text(encoding=encoding)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            else:
                return {"error": "无法解码文件"}
            
            return {
                "content": content,
                "content_preview": content[:self.preview_length],
                "line_count": content.count("\n") + 1,
                "char_count": len(content),
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _read_pdf(self, path: Path) -> Dict[str, Any]:
        """读取 PDF 文件"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            content_parts = []
            for page in doc:
                content_parts.append(page.get_text())
            content = "\n\n".join(content_parts)
            doc.close()
            
            return {
                "content": content,
                "content_preview": content[:self.preview_length],
                "page_count": len(content_parts),
                "char_count": len(content),
            }
        except ImportError:
            # fallback: 使用 pdfplumber
            try:
                import pdfplumber
                content_parts = []
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            content_parts.append(text)
                content = "\n\n".join(content_parts)
                return {
                    "content": content,
                    "content_preview": content[:self.preview_length],
                    "page_count": len(content_parts),
                    "char_count": len(content),
                }
            except ImportError:
                return {"error": "PDF 读取需要安装 PyMuPDF 或 pdfplumber"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _read_docx(self, path: Path) -> Dict[str, Any]:
        """读取 DOCX 文件"""
        try:
            from docx import Document
            doc = Document(str(path))
            content_parts = [para.text for para in doc.paragraphs if para.text.strip()]
            content = "\n\n".join(content_parts)
            
            return {
                "content": content,
                "content_preview": content[:self.preview_length],
                "paragraph_count": len(content_parts),
                "char_count": len(content),
            }
        except ImportError:
            return {"error": "DOCX 读取需要安装 python-docx"}
        except Exception as e:
            return {"error": str(e)}
    
    def parse_chat_format(self, content: str, source_type: str) -> List[Dict[str, Any]]:
        """解析聊天记录格式"""
        messages = []
        lines = content.split("\n")
        
        if source_type == "qq_chat":
            messages = self._parse_qq_chat(lines)
        elif source_type == "wechat_chat":
            messages = self._parse_wechat_chat(lines)
        else:
            # 通用解析：每行一条消息
            for line in lines:
                line = line.strip()
                if line:
                    messages.append({
                        "content": line,
                        "sender": "unknown",
                        "time": None,
                    })
        
        return messages
    
    def _parse_qq_chat(self, lines: List[str]) -> List[Dict[str, Any]]:
        """解析 QQ 聊天记录格式"""
        messages = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # QQ格式: 2024-01-01 12:00:00 昵称\n消息内容
            # 或: 2024-01-01 12:00:00 昵称: 消息内容
            import re
            pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+?)[：:]\s*(.+)'
            match = re.match(pattern, line)
            if match:
                messages.append({
                    "time": match.group(1),
                    "sender": match.group(2).strip(),
                    "content": match.group(3).strip(),
                })
            elif messages:
                # 续行内容
                messages[-1]["content"] += "\n" + line
        
        return messages
    
    def _parse_wechat_chat(self, lines: List[str]) -> List[Dict[str, Any]]:
        """解析微信聊天记录格式"""
        messages = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            import re
            # 微信格式: 2024-01-01 12:00 昵称: 消息
            pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+(.+?)[：:]\s*(.+)'
            match = re.match(pattern, line)
            if match:
                messages.append({
                    "time": match.group(1),
                    "sender": match.group(2).strip(),
                    "content": match.group(3).strip(),
                })
            elif messages:
                messages[-1]["content"] += "\n" + line
        
        return messages
    
    async def import_from_text(
        self,
        user_id: str,
        content: str,
        source_type: str,
        file_name: str = "",
        db = None,
    ) -> Dict[str, Any]:
        """
        从文本内容导入人生资料
        完整流程：读取 → 检测格式 → 解析 → 调用 LifeParser
        """
        from engines.life_parser.engine import life_parser_engine
        
        # 检测格式
        if source_type == "auto":
            source_type = self.detect_source_type(file_name, content[:500])
        
        # 解析聊天记录
        if source_type in ["qq_chat", "wechat_chat"]:
            parsed_messages = self.parse_chat_format(content, source_type)
        else:
            parsed_messages = None
        
        # 调用 LifeParser 提取结构化数据
        parsed_data = await life_parser_engine.parse(
            content=content,
            source_type=source_type,
            parsed_messages=parsed_messages,
        )
        
        return {
            "source_type": source_type,
            "file_name": file_name,
            "content_preview": content[:self.preview_length],
            "parsed_data": parsed_data,
            "char_count": len(content),
        }


# 全局实例
life_import_engine = LifeImportEngine()
