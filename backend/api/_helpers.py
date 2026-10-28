"""API 公共辅助函数"""
def ok(data):
    return {"ok": True, "data": data}

def err(error: str):
    return {"ok": False, "error": error}
