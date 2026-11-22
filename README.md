# Marco 小工具全家桶（单文件版）

两个零依赖 Python 脚本，一条命令跑完，Mac 和 Windows 通用。不需要装环境，装个 Python 3 就行。

## 1. batchrename.py — 批量重命名

几百个文件改名一条命令。支持前缀、后缀、序号、查找替换、去空格、大小写转换，默认只预览（dry-run），加 `--apply` 才真改，改完自动留撤销记录 `_rename_undo.json`。

```
python3 batchrename.py ~/Downloads/会议纪要 --prefix "销售_" --date 2026-11-22
python3 batchrename.py ./photos --replace "副本" "" --apply
python3 batchrename.py ./photos --undo _rename_undo.json
```

## 2. imgcomp.py — 图片批量压缩

按最大边或质量压图，保持目录结构输出。默认不覆盖原图。

```
python3 imgcomp.py ./原图 ./压缩后 --max-side 1600 --quality 82
```

依赖 Pillow（`pip3 install pillow`），其余零依赖。

## 来源

- batchrename 源码： https://github.com/253631672/batchrename
- imgcomp 源码： https://github.com/253631672/imgcomp

## 常见用法

**一堆下载文件统一改名加日期前缀**
`python3 batchrename.py ~/Downloads --prefix "$(date +%Y-%m-%d)_"`

**公众号配图统一压到 1600 宽**
`python3 imgcomp.py ./配图 ./上传 --max-side 1600 --quality 85`

**改坏了想撤回**
`python3 batchrename.py ./目录 --undo _rename_undo.json`

## 说明

脚本是纯本地运行的，不联网、不上传任何文件。买断制，脚本可随意改，二次分发请保留作者信息。
