from pathlib import Path
Path("src/ggplotpy/core/gg.py").write_text(Path("scripts/gg_template.py").read_text(encoding="utf-8"), encoding="utf-8")
print("ok")
