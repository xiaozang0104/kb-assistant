"""split_text 函数的单元测试"""
from rag.splitter import split_text


def test_split_short_text():
    """短文本（小于 chunk_size）应该只切出 1 块"""
    text = "短文本"
    chunks = split_text(text, chunk_size=200, overlap=0)
    assert len(chunks) == 1
    assert chunks[0] == "短文本"


def test_split_long_text_no_overlap():
    """长文本无重叠切分：块数 = ceil(长度/chunk_size)"""
    text = "A" * 1000
    chunks = split_text(text, chunk_size=200, overlap=0)
    assert len(chunks) == 5  # 1000/200 = 5


def test_split_with_overlap_more_chunks():
    """有重叠时块数应该比无重叠多"""
    text = "A" * 1000
    chunks_no_ov = split_text(text, chunk_size=200, overlap=0)
    chunks_with_ov = split_text(text, chunk_size=200, overlap=50)
    assert len(chunks_with_ov) > len(chunks_no_ov)


def test_chunks_cover_full_text():
    """所有块拼接（去重叠）应覆盖原文"""
    text = "测试文本" * 100
    chunks = split_text(text, chunk_size=50, overlap=10)
    # 每块都不为空
    assert all(len(c) > 0 for c in chunks)
    # 拼接后应包含原文开头
    joined = "".join(chunks)
    assert text[:50] in joined