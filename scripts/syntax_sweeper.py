#!/usr/bin/env python3
"""
Syntax and indentation error sweeper
"""
from __future__ import annotations
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDES = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", "legacy"}
PY = [p for p in ROOT.rglob("*.py") if not any(x in p.parts for x in EXCLUDES)]

bad = []
for p in PY:
    try:
        content = p.read_text(encoding="utf-8", errors='ignore')
        ast.parse(content)
    except (SyntaxError, IndentationError) as e:
        bad.append((p, f"{e.__class__.__name__}: {e}"))
    except Exception as e:
        # Skip files that can't be read
        pass

if bad:
    print("⚠️  Syntax/Indentation issues:")
    for p, msg in bad[:10]:  # Limit to first 10
        print(f"- {p}: {msg}")
    if len(bad) > 10:
        print(f"... and {len(bad) - 10} more")
    sys.exit(2)
else:
    print("✅ No syntax/indentation errors found.")