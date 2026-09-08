def split_text(text, chunk_size=300, overlap=50):
    """
    最简单的固定长度切分器。
    原理：从位置0开始，每 chunk_size 个字符切一块；
         下一块从 (上一块结尾 - overlap) 开始，保证重叠。
    """
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start = end - overlap
    return chunks


if __name__ == "__main__":
    with open("data/employee_handbook.txt", encoding="utf-8") as f:
        text = f.read()
    print(f"手册长度: {len(text)} 字")
    for size, ov in [(200, 0), (200, 50), (500, 100)]:
        result = split_text(text, chunk_size=size, overlap=ov)
        print(f"chunk_size={size}, overlap={ov} → 切出 {len(result)} 块")