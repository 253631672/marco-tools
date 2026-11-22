#!/usr/bin/env python3
"""batchrename - 批量重命名小工具（单文件，零依赖，只用 Python 标准库）

特点
- 默认只预览，不真改文件；加 --apply 才执行
- 执行前自动生成撤销脚本，改错一条命令还原
- 支持前缀/后缀/序号/查找替换/去空格/大小写/日期前缀，可叠加使用
- 只改文件名，不动内容；跳过同名冲突

用法
  python3 batchrename.py 目标目录 [选项]

常用选项
  --prefix 项目_        加前缀
  --suffix _终稿        加后缀（在扩展名前）
  --seq 3              追加序号，从 3 开始
  --seq-width 3        序号位数，默认 3（001）
  --replace 旧=新       查找替换，可写多次
  --strip-space        去掉名字里的空格，换成下划线
  --lower / --upper    转小写 / 大写
  --date               加今天日期前缀 2026-11-22_
  --ext jpg,png        只处理这些扩展名
  --recursive          连子目录一起处理
  --apply              真正执行（不加就是预览）

示例
  python3 batchrename.py ~/Downloads/截图 --prefix 课程_ --seq 1 --apply
  python3 batchrename.py ./合同 --replace 副本= --strip-space --apply
  python3 batchrename.py ./照片 --date --seq 1 --ext jpg,heic
"""
import argparse
import datetime
import json
import os
import sys
from pathlib import Path


def build_new_name(path: Path, args, index):
    stem, ext = path.stem, path.suffix
    if args.replace:
        for pair in args.replace:
            if "=" not in pair:
                raise SystemExit(f"--replace 需要 旧=新 的形式，收到：{pair}")
            old, new = pair.split("=", 1)
            stem = stem.replace(old, new)
    if args.strip_space:
        stem = stem.replace(" ", "_")
        stem = "_".join(filter(None, stem.split("_")))
    if args.lower:
        stem = stem.lower()
    if args.upper:
        stem = stem.upper()
    if args.date:
        stem = datetime.date.today().isoformat() + "_" + stem
    if args.prefix:
        stem = args.prefix + stem
    if args.suffix:
        stem = stem + args.suffix
    if args.seq is not None:
        width = max(args.seq_width, len(str(args.seq + index)))
        stem = f"{stem}_{str(args.seq + index).zfill(width)}"
    return stem + ext


def collect(root: Path, args):
    exts = None
    if args.ext:
        exts = {"." + e.strip().lower().lstrip(".") for e in args.ext.split(",") if e.strip()}
    items = []
    walker = root.rglob("*") if args.recursive else root.glob("*")
    for p in sorted(walker):
        if not p.is_file():
            continue
        if p.name.startswith("."):          # 跳过隐藏文件
            continue
        if exts and p.suffix.lower() not in exts:
            continue
        items.append(p)
    return items


def main():
    ap = argparse.ArgumentParser(description="批量重命名（默认预览，--apply 才执行）")
    ap.add_argument("target", help="要处理的目录")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--seq", type=int, default=None, help="起始序号")
    ap.add_argument("--seq-width", type=int, default=3)
    ap.add_argument("--replace", action="append", default=[], help="旧=新，可多次")
    ap.add_argument("--strip-space", action="store_true")
    ap.add_argument("--lower", action="store_true")
    ap.add_argument("--upper", action="store_true")
    ap.add_argument("--date", action="store_true")
    ap.add_argument("--ext", default="")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = Path(args.target).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"不是目录：{root}")

    files = collect(root, args)
    if not files:
        print("没有匹配的文件。")
        return

    plan, used, skipped = [], set(), 0
    for i, p in enumerate(files):
        new_name = build_new_name(p, args, i)
        if new_name == p.name:
            continue
        target = p.with_name(new_name)
        if target.exists() or new_name in used:
            skipped += 1
            continue
        used.add(new_name)
        plan.append((p, target))

    print(f"目录：{root}")
    print(f"匹配 {len(files)} 个文件，需要改名 {len(plan)} 个，跳过冲突 {skipped} 个")
    for src, dst in plan[:30]:
        print(f"  {src.name}  ->  {dst.name}")
    if len(plan) > 30:
        print(f"  …… 还有 {len(plan) - 30} 个")

    if not args.apply:
        print("\n这是预览。确认无误后加 --apply 执行。")
        return

    undo = []
    for src, dst in plan:
        os.rename(src, dst)
        undo.append({"from": str(dst), "to": str(src)})
    log = root / "_rename_undo.json"
    log.write_text(json.dumps(undo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已改名 {len(plan)} 个。撤销记录：{log}")


if __name__ == "__main__":
    sys.exit(main())
