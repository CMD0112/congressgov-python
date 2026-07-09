from pathlib import Path

h = Path("examples/output/network_graph/live_network_explorer.html").read_text(encoding="utf-8")
lines = [
    f"len={len(h)}",
    f"fullLabel={h.count('fullLabel')}",
    f"nodeDisplayLabel={h.count('nodeDisplayLabel')}",
    f"Rep.={h.count('Rep.')}",
]
Path("examples/output/html_check2.txt").write_text("\n".join(lines))
