from pathlib import Path
root = Path(r"c:\ProfDM_Rproject\Ggplot2PY")
gg = root / "src/ggplotpy/core/gg.py"
text = gg.read_text(encoding="utf-8")
if "GG - ggplot2" not in text:
    import re
    text = re.sub(r'"""GG.*?ggplot2 plot wrapper\."""', '"""GG - ggplot2 plot wrapper."""', text, count=1)
old = """    finally:
        if device_open:
            try:
                ro.r(\"try(dev.off(), silent=TRUE)\")
            except Exception:
                pass
        try:
            os.unlink(path)
        except OSError:
            pass"""
new = """    finally:
        try:
            ro.r(\"try(dev.off(), silent=TRUE)\")
        except Exception:
            pass
        try:
            os.unlink(path)
        except OSError:
            pass"""
if old in text:
    text = text.replace(old, new)
else:
    print("WARN: finally pattern mismatch")
gg.write_text(text, encoding="utf-8", newline="\n")
print("done")
