"""Assemble spike_summary.md from the header, the generated tables, and the anomaly list."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parts = [ROOT / "scripts" / "_head.md", ROOT / "data" / "_summary_tables.md", ROOT / "scripts" / "_tail.md"]
(ROOT / "spike_summary.md").write_text("".join(p.read_text(encoding="utf-8") for p in parts), encoding="utf-8")
print("wrote", ROOT / "spike_summary.md")
