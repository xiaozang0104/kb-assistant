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
    real_text = """根据公司员工手册第三章规定，员工请假需遵守以下流程：第一，提前三天在OA系统提交请假申请；第二，注明请假类型（事假、病假、年假）；第三，部门主管在24小时内审批；第四，审批通过后方可休假。如遇紧急情况无法提前申请，需当天电话告知直属主管，并在返岗后一个工作日内补交申请。"""
    chunks = split_text(real_text, chunk_size=100, overlap=20)
    for i, c in enumerate(chunks):
        print(f"--- 块{i+1} ({len(c)}字) ---")
        print(c)