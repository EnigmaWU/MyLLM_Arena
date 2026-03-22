#!/usr/bin/env python3
"""Generate and serve a review page for a newly created skill.

Reads a skill workspace directory, discovers test case outputs, and serves
a self-contained HTML page for the user to review and provide feedback.
Feedback auto-saves to feedback.json in the workspace.

Adapted from Anthropic's skill-creator eval-viewer for use with save-as-skill.

Usage:
    python generate_review.py <workspace-path> --skill-name NAME
    python generate_review.py <workspace-path> --static /tmp/review.html
    python generate_review.py <workspace-path> --previous-workspace /path/to/prev

No dependencies beyond the Python stdlib are required.
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import signal
import subprocess
import sys
import time
import webbrowser
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

METADATA_FILES = {"transcript.md", "user_notes.md", "metrics.json"}

TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".csv", ".py", ".js", ".ts", ".tsx", ".jsx",
    ".yaml", ".yml", ".xml", ".html", ".css", ".sh", ".rb", ".go", ".rs",
    ".java", ".c", ".cpp", ".h", ".hpp", ".sql", ".toml",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


def get_mime_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def find_runs(workspace: Path) -> list:
    """Recursively find directories that contain an outputs/ subdirectory."""
    runs = []
    _find_runs_recursive(workspace, workspace, runs)
    runs.sort(key=lambda r: (r.get("eval_id", float("inf")), r["id"]))
    return runs


def _find_runs_recursive(root: Path, current: Path, runs: list) -> None:
    if not current.is_dir():
        return
    outputs_dir = current / "outputs"
    if outputs_dir.is_dir():
        run = build_run(root, current)
        if run:
            runs.append(run)
        return  # Don't recurse into runs
    for child in sorted(current.iterdir()):
        if child.is_dir() and child.name not in {".git", "__pycache__", "node_modules"}:
            _find_runs_recursive(root, child, runs)


def build_run(root: Path, run_dir: Path) -> dict | None:
    """Build a run dict from a directory containing outputs/."""
    prompt = ""
    eval_id = None

    # Try eval_metadata.json
    for candidate in [run_dir / "eval_metadata.json"]:
        if candidate.exists():
            try:
                metadata = json.loads(candidate.read_text())
                prompt = metadata.get("prompt", "")
                eval_id = metadata.get("eval_id")
            except (json.JSONDecodeError, OSError):
                pass
            if prompt:
                break

    if not prompt:
        prompt = "(No prompt found)"

    run_id = str(run_dir.relative_to(root)).replace("/", "-").replace("\\", "-")

    # Collect output files
    outputs_dir = run_dir / "outputs"
    output_files = []
    if outputs_dir.is_dir():
        for f in sorted(outputs_dir.iterdir()):
            if f.is_file() and f.name not in METADATA_FILES:
                output_files.append(embed_file(f))

    # Load grading if present
    grading = None
    for candidate in [run_dir / "grading.json", run_dir.parent / "grading.json"]:
        if candidate.exists():
            try:
                grading = json.loads(candidate.read_text())
            except (json.JSONDecodeError, OSError):
                pass
            if grading:
                break

    return {
        "id": run_id,
        "prompt": prompt,
        "eval_id": eval_id,
        "outputs": output_files,
        "grading": grading,
    }


def embed_file(path: Path) -> dict:
    """Read a file and return an embedded representation."""
    ext = path.suffix.lower()
    mime = get_mime_type(path)

    if ext in TEXT_EXTENSIONS:
        try:
            content = path.read_text(errors="replace")
        except OSError:
            content = "(Error reading file)"
        return {"name": path.name, "type": "text", "content": content}

    elif ext in IMAGE_EXTENSIONS:
        try:
            raw = path.read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
        except OSError:
            return {"name": path.name, "type": "error", "content": "(Error reading file)"}
        return {"name": path.name, "type": "image", "mime": mime, "data_uri": f"data:{mime};base64,{b64}"}

    else:
        try:
            raw = path.read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
        except OSError:
            return {"name": path.name, "type": "error", "content": "(Error reading file)"}
        return {"name": path.name, "type": "binary", "mime": mime, "data_uri": f"data:{mime};base64,{b64}"}


def load_previous_iteration(workspace: Path) -> dict:
    """Load previous iteration's feedback and outputs."""
    result = {}
    feedback_map = {}
    feedback_path = workspace / "feedback.json"
    if feedback_path.exists():
        try:
            data = json.loads(feedback_path.read_text())
            feedback_map = {
                r["run_id"]: r["feedback"]
                for r in data.get("reviews", [])
                if r.get("feedback", "").strip()
            }
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    prev_runs = find_runs(workspace)
    for run in prev_runs:
        result[run["id"]] = {
            "feedback": feedback_map.get(run["id"], ""),
            "outputs": run["outputs"],
        }
    return result


def generate_html(runs: list, skill_name: str, previous: dict, benchmark: dict | None = None) -> str:
    """Generate a self-contained HTML review page."""
    template_path = Path(__file__).parent / "viewer.html"
    if not template_path.exists():
        # Fallback: generate minimal HTML inline
        return _generate_minimal_html(runs, skill_name, previous, benchmark)

    template = template_path.read_text()
    data = {
        "runs": runs,
        "skill_name": skill_name,
        "previous_feedback": {k: v.get("feedback", "") for k, v in previous.items()},
        "previous_outputs": {k: v.get("outputs", []) for k, v in previous.items()},
        "benchmark": benchmark,
    }
    data_json = json.dumps(data, ensure_ascii=False)
    return template.replace("/*__EMBEDDED_DATA__*/", f"const EMBEDDED_DATA = {data_json};")


def _generate_minimal_html(runs: list, skill_name: str, previous: dict, benchmark: dict | None) -> str:
    """Generate a minimal self-contained HTML page when viewer.html template is not available."""
    data = {
        "runs": runs,
        "skill_name": skill_name,
        "previous_feedback": {k: v.get("feedback", "") for k, v in previous.items()},
        "previous_outputs": {k: v.get("outputs", []) for k, v in previous.items()},
        "benchmark": benchmark,
    }
    data_json = json.dumps(data, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skill Review - {skill_name}</title>
  <style>
    :root {{ --bg: #faf9f5; --surface: #fff; --border: #e8e6dc; --text: #141413;
             --accent: #d97757; --green: #788c5d; --red: #c44; --radius: 6px; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg); color: var(--text); }}
    .header {{ background: var(--text); color: var(--bg); padding: 1rem 2rem;
               display: flex; justify-content: space-between; align-items: center; }}
    .header h1 {{ font-size: 1.1rem; }}
    .main {{ max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
    .section {{ background: var(--surface); border: 1px solid var(--border);
                border-radius: var(--radius); margin-bottom: 1.5rem; }}
    .section-header {{ padding: 0.75rem 1rem; font-weight: 600; font-size: 0.875rem;
                       border-bottom: 1px solid var(--border); }}
    .section-body {{ padding: 1rem; }}
    .prompt-text {{ font-size: 0.875rem; line-height: 1.6; white-space: pre-wrap; }}
    .output-file {{ border: 1px solid var(--border); border-radius: var(--radius);
                    margin-bottom: 0.75rem; overflow: hidden; }}
    .output-file-header {{ background: var(--bg); padding: 0.5rem 0.75rem;
                           font-size: 0.75rem; font-family: monospace; font-weight: 600; }}
    .output-file-content {{ padding: 0.75rem; }}
    .output-file-content pre {{ font-size: 0.8125rem; line-height: 1.5;
                                 white-space: pre-wrap; word-break: break-word;
                                 font-family: 'SF Mono', Consolas, monospace; }}
    .output-file-content img {{ max-width: 100%; height: auto; }}
    textarea {{ width: 100%; min-height: 100px; padding: 0.75rem; border: 1px solid var(--border);
                border-radius: var(--radius); font-size: 0.875rem; resize: vertical; }}
    .nav {{ display: flex; justify-content: space-between; padding: 1rem 0; }}
    .nav button {{ padding: 0.5rem 1.5rem; border: 1px solid var(--border);
                   border-radius: var(--radius); cursor: pointer; font-size: 0.875rem; }}
    .nav button:disabled {{ opacity: 0.4; cursor: default; }}
    .done-btn {{ background: var(--accent); color: white; border: none !important; }}
    .progress {{ text-align: center; font-size: 0.8rem; color: #888; padding: 0.5rem; }}
    .grade-pass {{ color: var(--green); }} .grade-fail {{ color: var(--red); }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Skill Review: <span id="skill-name">{skill_name}</span></h1>
    <div id="counter"></div>
  </div>
  <div class="progress" id="progress"></div>
  <div class="main">
    <div class="section">
      <div class="section-header">Prompt</div>
      <div class="section-body"><div class="prompt-text" id="prompt-text"></div></div>
    </div>
    <div class="section">
      <div class="section-header">Output</div>
      <div class="section-body" id="outputs-body"></div>
    </div>
    <div class="section" id="grades-section" style="display:none;">
      <div class="section-header">Grades</div>
      <div class="section-body" id="grades-body"></div>
    </div>
    <div class="section">
      <div class="section-header">Feedback</div>
      <div class="section-body">
        <textarea id="feedback" placeholder="What looks good? What needs improvement?"></textarea>
        <div id="feedback-status" style="font-size:0.75rem;color:#888;margin-top:0.25rem;"></div>
      </div>
    </div>
    <div class="nav">
      <button id="prev-btn" onclick="navigate(-1)">&larr; Previous</button>
      <button class="done-btn" id="done-btn" onclick="submitAll()">Submit All Reviews</button>
      <button id="next-btn" onclick="navigate(1)">Next &rarr;</button>
    </div>
  </div>
  <script>
    const DATA = {data_json};
    let feedbackMap = {{}};
    let currentIndex = 0;

    function init() {{
      showRun(0);
      document.getElementById("feedback").addEventListener("input", () => {{
        clearTimeout(window._saveTimeout);
        window._saveTimeout = setTimeout(saveFeedback, 800);
      }});
    }}

    function navigate(delta) {{
      saveFeedback();
      const n = currentIndex + delta;
      if (n >= 0 && n < DATA.runs.length) showRun(n);
    }}

    function showRun(index) {{
      currentIndex = index;
      const run = DATA.runs[index];
      document.getElementById("counter").textContent = (index + 1) + " / " + DATA.runs.length;
      document.getElementById("progress").textContent = "Test case " + (index + 1) + " of " + DATA.runs.length;
      document.getElementById("prompt-text").textContent = run.prompt;

      // Outputs
      const ob = document.getElementById("outputs-body");
      ob.innerHTML = "";
      for (const f of run.outputs) {{
        const div = document.createElement("div");
        div.className = "output-file";
        const header = document.createElement("div");
        header.className = "output-file-header";
        header.textContent = f.name;
        div.appendChild(header);
        const content = document.createElement("div");
        content.className = "output-file-content";
        if (f.type === "text") {{
          const pre = document.createElement("pre");
          pre.textContent = f.content;
          content.appendChild(pre);
        }} else if (f.type === "image") {{
          const img = document.createElement("img");
          img.src = f.data_uri;
          content.appendChild(img);
        }} else {{
          const a = document.createElement("a");
          a.href = f.data_uri || "#";
          a.download = f.name;
          a.textContent = "Download " + f.name;
          content.appendChild(a);
        }}
        div.appendChild(content);
        ob.appendChild(div);
      }}
      if (run.outputs.length === 0) ob.innerHTML = "<div style='color:#888'>No output files</div>";

      // Grades
      const gs = document.getElementById("grades-section");
      const gb = document.getElementById("grades-body");
      if (run.grading) {{
        gs.style.display = "block";
        let html = "";
        for (const exp of (run.grading.expectations || [])) {{
          const cls = exp.passed ? "grade-pass" : "grade-fail";
          const icon = exp.passed ? "\\u2713" : "\\u2717";
          html += '<div class="' + cls + '">' + icon + " " + (exp.text || "") + "</div>";
        }}
        gb.innerHTML = html;
      }} else {{ gs.style.display = "none"; }}

      // Feedback
      document.getElementById("feedback").value = feedbackMap[run.id] || "";
      document.getElementById("prev-btn").disabled = index === 0;
      document.getElementById("next-btn").disabled = index === DATA.runs.length - 1;
    }}

    function saveFeedback() {{
      const run = DATA.runs[currentIndex];
      const text = document.getElementById("feedback").value;
      if (text.trim()) feedbackMap[run.id] = text;
      else delete feedbackMap[run.id];

      const reviews = DATA.runs.map(r => ({{ run_id: r.id, feedback: feedbackMap[r.id] || "", timestamp: new Date().toISOString() }}));
      const payload = JSON.stringify({{ reviews, status: "in_progress" }}, null, 2);

      fetch("/api/feedback", {{ method: "POST", headers: {{"Content-Type": "application/json"}}, body: payload }})
        .then(() => {{ document.getElementById("feedback-status").textContent = "Saved"; }})
        .catch(() => {{ document.getElementById("feedback-status").textContent = "Will download on submit"; }});
    }}

    function submitAll() {{
      saveFeedback();
      const reviews = DATA.runs.map(r => ({{ run_id: r.id, feedback: feedbackMap[r.id] || "", timestamp: new Date().toISOString() }}));
      const payload = JSON.stringify({{ reviews, status: "complete" }}, null, 2);

      fetch("/api/feedback", {{ method: "POST", headers: {{"Content-Type": "application/json"}}, body: payload }})
        .then(() => alert("Feedback saved. Go back to your agent session and say you're done reviewing."))
        .catch(() => {{
          const blob = new Blob([payload], {{ type: "application/json" }});
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url; a.download = "feedback.json"; a.click();
          URL.revokeObjectURL(url);
          alert("Feedback downloaded as feedback.json");
        }});
    }}

    init();
  </script>
</body>
</html>"""


def _kill_port(port: int) -> None:
    """Kill any process listening on the given port."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5,
        )
        for pid_str in result.stdout.strip().split("\n"):
            if pid_str.strip():
                try:
                    os.kill(int(pid_str.strip()), signal.SIGTERM)
                except (ProcessLookupError, ValueError):
                    pass
        if result.stdout.strip():
            time.sleep(0.5)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


class ReviewHandler(BaseHTTPRequestHandler):
    """Serves the review HTML and handles feedback saves."""

    def __init__(self, workspace, skill_name, feedback_path, previous, benchmark_path, *args, **kwargs):
        self.workspace = workspace
        self.skill_name = skill_name
        self.feedback_path = feedback_path
        self.previous = previous
        self.benchmark_path = benchmark_path
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            runs = find_runs(self.workspace)
            benchmark = None
            if self.benchmark_path and self.benchmark_path.exists():
                try:
                    benchmark = json.loads(self.benchmark_path.read_text())
                except (json.JSONDecodeError, OSError):
                    pass
            html = generate_html(runs, self.skill_name, self.previous, benchmark)
            content = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/api/feedback":
            data = b"{}"
            if self.feedback_path.exists():
                data = self.feedback_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/feedback":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                if not isinstance(data, dict):
                    raise ValueError("Expected JSON object")
                self.feedback_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                resp = b'{"status": "ok"}'
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            except (json.JSONDecodeError, ValueError) as e:
                self.send_error(400, str(e))
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # Suppress request logging


def main():
    parser = argparse.ArgumentParser(description="Skill review viewer")
    parser.add_argument("workspace", type=Path, help="Path to workspace directory with test outputs")
    parser.add_argument("--port", "-p", type=int, default=3117, help="Server port (default: 3117)")
    parser.add_argument("--skill-name", "-n", type=str, default=None, help="Skill name for header")
    parser.add_argument(
        "--previous-workspace", type=Path, default=None,
        help="Path to previous iteration workspace (shows old outputs and feedback)",
    )
    parser.add_argument(
        "--benchmark", type=Path, default=None,
        help="Path to benchmark.json for quantitative stats",
    )
    parser.add_argument(
        "--static", "-s", type=Path, default=None,
        help="Write standalone HTML to this path instead of starting a server",
    )
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"Error: {workspace} is not a directory", file=sys.stderr)
        sys.exit(1)

    runs = find_runs(workspace)
    if not runs:
        print(f"No runs found in {workspace}", file=sys.stderr)
        print("Expected structure: <workspace>/<eval-name>/outputs/<files>", file=sys.stderr)
        sys.exit(1)

    skill_name = args.skill_name or workspace.name.replace("-workspace", "")
    feedback_path = workspace / "feedback.json"

    previous = {}
    if args.previous_workspace:
        previous = load_previous_iteration(args.previous_workspace.resolve())

    benchmark_path = args.benchmark.resolve() if args.benchmark else None
    benchmark = None
    if benchmark_path and benchmark_path.exists():
        try:
            benchmark = json.loads(benchmark_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    # Static mode: write HTML and exit
    if args.static:
        html = generate_html(runs, skill_name, previous, benchmark)
        args.static.write_text(html, encoding="utf-8")
        print(f"Wrote static review to {args.static}")
        sys.exit(0)

    # Server mode
    port = args.port
    _kill_port(port)

    handler = partial(ReviewHandler, workspace, skill_name, feedback_path, previous, benchmark_path)
    try:
        server = HTTPServer(("127.0.0.1", port), handler)
    except OSError:
        server = HTTPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]

    url = f"http://localhost:{port}"
    print(f"\n  Skill Review Viewer")
    print(f"  {'─' * 35}")
    print(f"  URL:       {url}")
    print(f"  Workspace: {workspace}")
    print(f"  Feedback:  {feedback_path}")
    if previous:
        print(f"  Previous:  {args.previous_workspace} ({len(previous)} runs)")
    if benchmark_path:
        print(f"  Benchmark: {benchmark_path}")
    print(f"\n  Press Ctrl+C to stop.\n")

    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        server.shutdown()


if __name__ == "__main__":
    main()
