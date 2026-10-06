# -*- coding: utf-8 -*-
"""按首次引用顺序重编参考文献（Vancouver / Springer 要求）。

用法：
    python3 renumber_refs.py --check 稿件.md [补充材料.md ...]
    python3 renumber_refs.py --apply 稿件.md [补充材料.md ...]

第一个文件必须是含 `## References` 编号列表的主稿；其余文件只改正文引用编号。
--check 只报告映射与将要改动的处数，不写盘；--apply 才落盘。

首现顺序取自主稿中 `## References` 之前与之后的全部正文（含表格与图注），
按文件出现次序扫描——与期刊排版后的阅读顺序一致。
"""
import io, re, sys

CITE = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]")
REF_HEAD = re.compile(r"^## References\s*$", re.M)
REF_ITEM = re.compile(r"^(\d+)\.\s+(.*)$", re.M)


def split_refs(text):
    m = REF_HEAD.search(text)
    if not m:
        raise SystemExit("主稿中未找到 `## References` 段落")
    head, rest = text[:m.end()], text[m.end():]
    # 文献表在 References 之后、下一个二级标题之前
    nxt = re.search(r"^## ", rest, re.M)
    body_after = rest[nxt.start():] if nxt else ""
    reflist = rest[:nxt.start()] if nxt else rest
    return head, reflist, body_after


def parse_nums(group):
    """把 '3,5,6,7' 或 '2-4' 展开为编号列表（本稿只用逗号，范围仅作保险）。"""
    out = []
    for part in re.split(r"\s*,\s*", group):
        m = re.match(r"^(\d+)\s*[–-]\s*(\d+)$", part)
        if m:
            out.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            out.append(int(part))
    return out


def first_appearance(scan_text):
    order, seen = [], set()
    for m in CITE.finditer(scan_text):
        for n in parse_nums(m.group(1)):
            if n not in seen:
                seen.add(n); order.append(n)
    return order


def renumber_citations(text, mapping):
    changed = [0]

    def sub(m):
        nums = parse_nums(m.group(1))
        new = [mapping.get(n, n) for n in nums]
        if new != nums:
            changed[0] += 1
        return "[" + ",".join(str(x) for x in new) + "]"

    return CITE.sub(sub, text), changed[0]


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    mode, files = sys.argv[1], sys.argv[2:]

    main_text = io.open(files[0], encoding="utf-8").read()
    head, reflist, tail = split_refs(main_text)

    items = {int(n): body for n, body in REF_ITEM.findall(reflist)}
    if not items:
        raise SystemExit("未能解析文献表条目")

    # 首现顺序：正文（References 之前）+ 表格图注（References 之后）
    order = first_appearance(head + "\n" + tail)
    missing = [n for n in items if n not in order]
    extra = [n for n in order if n not in items]
    if extra:
        raise SystemExit("引用了文献表中不存在的编号: %s" % extra)

    mapping = {old: i + 1 for i, old in enumerate(order)}
    for n in sorted(missing):                      # 列而未引者顺延到最后
        mapping[n] = len(mapping) + 1

    moved = {o: n for o, n in mapping.items() if o != n}
    print("文献条目 %d 条；首现顺序已解析 %d 条；列而未引 %d 条"
          % (len(items), len(order), len(missing)))
    if not moved:
        print("首现顺序已正确，无需重编。")
        return
    print("需重编 %d 条（旧 → 新）：" % len(moved))
    for o in sorted(moved):
        print("   [%2d] → [%2d]   %s" % (o, moved[o], items[o][:60]))

    # 重建文献表：按新编号升序。只替换编号列表本身所占的那一段，
    # 保留其前后的其它内容（如列表末尾的 <!--pagebreak--> 分页标记）。
    inv = {v: k for k, v in mapping.items()}
    spans = [m.span() for m in REF_ITEM.finditer(reflist)]
    list_start, list_end = spans[0][0], spans[-1][1]
    rebuilt = "\n".join("%d. %s" % (i, items[inv[i]]) for i in sorted(inv))
    new_reflist = reflist[:list_start] + rebuilt + reflist[list_end:]

    total = 0
    outputs = {}
    new_head, c1 = renumber_citations(head, mapping)
    new_tail, c2 = renumber_citations(tail, mapping)
    total += c1 + c2
    outputs[files[0]] = new_head + new_reflist + new_tail
    print("  %s：正文/表格引用改动 %d 处" % (files[0], c1 + c2))

    for f in files[1:]:
        t = io.open(f, encoding="utf-8").read()
        nt, c = renumber_citations(t, mapping)
        outputs[f] = nt
        total += c
        print("  %s：引用改动 %d 处" % (f, c))

    if mode == "--apply":
        for f, t in outputs.items():
            io.open(f, "w", encoding="utf-8").write(t)
        print("已写入 %d 个文件，共改动 %d 处引用。" % (len(outputs), total))
    else:
        print("（--check 模式，未写盘；共 %d 处待改）" % total)


if __name__ == "__main__":
    main()
