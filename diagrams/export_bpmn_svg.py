import argparse
import html
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree


PAGE = """<!doctype html>
<meta charset="utf-8">
<div id="canvas" style="width: 1600px; height: 900px"></div>
<pre id="result"></pre>
<script src="viewer.js"></script>
<script>
(async () => {
  const result = document.getElementById('result');
  try {
    const viewer = new BpmnJS({
      container: '#canvas',
      bpmnRenderer: {
        defaultFill: '#ffffff',
        defaultStroke: '#25272c',
        defaultLabelColor: '#25272c'
      },
      textRenderer: {
        defaultStyle: { fontFamily: 'Arial, sans-serif', fontSize: 15 }
      }
    });
    const { warnings } = await viewer.importXML(__BPMN_XML__);
    const { svg } = await viewer.saveSVG();
    result.textContent = JSON.stringify({ svg, warnings: warnings.map(w => w.message) });
  } catch (error) {
    result.textContent = JSON.stringify({ error: error.message });
  }
})();
</script>
"""


def export(source, viewer_bundle, browser, output):
    with tempfile.TemporaryDirectory(prefix="it4350-bpmn-") as temp:
        directory = Path(temp)
        (directory / "viewer.js").write_bytes(viewer_bundle.read_bytes())
        page = directory / "diagram.html"
        xml_literal = json.dumps(source.read_text(encoding="utf-8-sig")).replace("<", r"\u003c")
        page.write_text(PAGE.replace("__BPMN_XML__", xml_literal), encoding="utf-8")
        result = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--disable-background-networking",
                "--no-first-run",
                "--no-default-browser-check",
                "--allow-file-access-from-files",
                f"--user-data-dir={directory / 'profile'}",
                "--virtual-time-budget=10000",
                "--dump-dom",
                page.as_uri(),
            ],
            capture_output=True,
            timeout=45,
        )

    dom = result.stdout.decode("utf-8", errors="replace")
    match = re.search(r'<pre id="result">(.*?)</pre>', dom, re.DOTALL)
    if result.returncode or not match or not match[1]:
        details = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Trình duyệt chưa xuất được hình BPMN ({result.returncode}). {details}")
    payload = json.loads(html.unescape(match[1]))
    if payload.get("error") or payload.get("warnings"):
        raise RuntimeError(payload.get("error") or "\n".join(payload["warnings"]))

    svg = payload["svg"]
    root = ElementTree.fromstring(svg)
    x, y, width, height = (float(value) for value in root.attrib["viewBox"].split())
    margin = 16
    bounds = f"{x - margin:g} {y - margin:g} {width + 2 * margin:g} {height + 2 * margin:g}"
    canvas = (
        f'<rect x="{x - margin:g}" y="{y - margin:g}" '
        f'width="{width + 2 * margin:g}" height="{height + 2 * margin:g}" fill="#ffffff"/>'
    )
    # Cắt theo kích thước nội dung và thêm nền trắng để hình đọc được cả ở giao diện tối.
    svg = re.sub(r'<svg\b[^>]*>', lambda match: (
        re.sub(r' (?:width|height|viewBox)="[^"]+"', "", match[0][:-1])
        + f' width="{width + 2 * margin:g}" height="{height + 2 * margin:g}" viewBox="{bounds}">'
        + canvas
    ), svg, count=1)
    ElementTree.fromstring(svg)
    output.write_text(svg + "\n", encoding="utf-8")


if __name__ == "__main__":
    programs = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    chrome = programs / "Google/Chrome/Application/chrome.exe"
    parser = argparse.ArgumentParser(description="Xuất sơ đồ BPMN 2.0 thành ảnh SVG.")
    parser.add_argument("source", type=Path, help="Tệp .bpmn có tọa độ sơ đồ")
    parser.add_argument("--viewer", type=Path, required=True, help="Tệp bpmn-viewer.production.min.js")
    parser.add_argument("--browser", type=Path, default=chrome, help="Đường dẫn tới Chrome hoặc Chromium")
    parser.add_argument("--output", type=Path, help="Đường dẫn ảnh SVG đầu ra")
    args = parser.parse_args()
    export(args.source, args.viewer, args.browser, args.output or args.source.with_suffix(".svg"))
