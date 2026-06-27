from pathlib import Path

root = Path(__file__).resolve().parent.parent

gg_path = root / "src/ggplotpy/core/gg.py"
text = gg_path.read_text(encoding="utf-8")
if "GG ? ggplot2" in text:
    text = text.replace('"""GG ? ggplot2 plot wrapper."""', '"""GG — ggplot2 plot wrapper."""')
marker = "    device_open = False"
if marker not in text:
    old = "    w, h, dpi = opts.width, opts.height, opts.dpi\n    try:\n        if device == \"svg\":"
    new = "    w, h, dpi = opts.width, opts.height, opts.dpi\n    device_open = False\n    try:\n        if device == \"svg\":"
    if old not in text:
        raise SystemExit("gg render anchor missing")
    text = text.replace(old, new)
    text = text.replace(
        "            )\n        ro.r[\"print\"](plot)\n        ro.r(\"dev.off()\")",
        "            )\n        device_open = True\n        ro.r[\"print\"](plot)\n        ro.r(\"dev.off()\")\n        device_open = False",
    )
    text = text.replace(
        "    finally:\n        try:\n            os.unlink(path)",
        "    finally:\n        if device_open:\n            try:\n                ro.r(\"try(dev.off(), silent=TRUE)\")\n            except Exception:\n                pass\n        try:\n            os.unlink(path)",
    )
    gg_path.write_text(text, encoding="utf-8", newline="\n")
    print("patched gg.py")
else:
    print("gg.py already patched")

aes_path = root / "r-helper/ggplotpy/R/aes.R"
aes_path.write_text(aes_path.read_text(encoding="utf-8-sig"), encoding="utf-8", newline="\n")
print("aes.R ok")
