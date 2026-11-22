import argparse, io
from pathlib import Path
from PIL import Image, ImageOps

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".tga"}

def human(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"

def fit(img, max_side):
    w, h = img.size
    if max(w, h) <= max_side:
        return img
    r = max_side / max(w, h)
    return img.resize((max(1, round(w * r)), max(1, round(h * r))), Image.LANCZOS)

def encode(img, fmt, q):
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.convert("RGB").save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    elif fmt == "WEBP":
        img.save(buf, "WEBP", quality=q, method=5)
    else:
        img.save(buf, "PNG", optimize=True)
    return buf.getvalue()

def shrink_to(img, fmt, target_bytes, lo=40, hi=92):
    data = encode(img, fmt, hi)
    if len(data) <= target_bytes:
        return data, hi
    best = encode(img, fmt, lo)
    if len(best) > target_bytes:
        return best, lo
    while lo < hi - 1:
        mid = (lo + hi) // 2
        data = encode(img, fmt, mid)
        if len(data) <= target_bytes:
            lo, best = mid, data
        else:
            hi = mid
    return best, lo

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--max-side", type=int, default=1600)
    ap.add_argument("--kb", type=int, default=200)
    ap.add_argument("--format", default="AUTO", choices=["AUTO", "JPEG", "PNG", "WEBP"])
    ap.add_argument("--keep", action="store_true", help="保留目录结构")
    a = ap.parse_args()

    src = Path(a.src)
    files = [src] if src.is_file() else [p for p in sorted(src.rglob("*")) if p.suffix.lower() in IMG_EXT]
    total_in = total_out = 0
    for p in files:
        img = Image.open(p)
        img = ImageOps.exif_transpose(img)
        fmt = a.format
        if fmt == "AUTO":
            fmt = "PNG" if (p.suffix.lower() == ".png" and img.mode in ("RGBA", "LA", "P")) else "JPEG"
        img = fit(img, a.max_side)
        data, q = shrink_to(img, fmt, a.kb * 1024)
        rel = p.relative_to(src) if (a.keep and src.is_dir()) else Path(p.name)
        out = (Path(a.dst) / rel).with_suffix(".png" if fmt == "PNG" else f".{fmt.lower()}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        total_in += p.stat().st_size
        total_out += len(data)
        print(f"{p.name}  {human(p.stat().st_size)} -> {human(len(data))}  q={q}")

    if files:
        print(f"共{len(files)}张  {human(total_in)} -> {human(total_out)}  压缩{100 - total_out / total_in * 100:.0f}%")

if __name__ == "__main__":
    main()
