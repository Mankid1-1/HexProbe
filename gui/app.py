import json
import threading
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from queue import Queue, Empty
from tkinter import Tk, StringVar, Text, filedialog, messagebox
from tkinter import ttk

from core.synthesis import HexProbeOrchestrator
from probes.fuzz.fuzz_probe import run as fuzz_probe
from probes.perf.chaos import run as chaos_probe
from probes.perf.perf_probe import run as perf_probe
from probes.static.surface_sweep import run as surface_sweep


@dataclass(frozen=True)
class ProbeDefinition:
    key: str
    name: str
    description: str
    func: callable


PROBES = [
    ProbeDefinition(
        key="static.surface_sweep",
        name="Static Surface Sweep",
        description="Scan for lint, type, and boundary input risks.",
        func=surface_sweep,
    ),
    ProbeDefinition(
        key="fuzz.fuzz_probe",
        name="Fuzz Probe",
        description="Run fuzzing scripts to detect crashes and memory safety issues.",
        func=fuzz_probe,
    ),
    ProbeDefinition(
        key="perf.perf_probe",
        name="Performance Probe",
        description="Compare load test metrics against a baseline.",
        func=perf_probe,
    ),
    ProbeDefinition(
        key="perf.chaos",
        name="Chaos Probe",
        description="Simulate service disruptions and report failures.",
        func=chaos_probe,
    ),
]


class HexProbeGUI:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("HexProbe Control Center")
        self.root.geometry("980x720")
        self.root.minsize(880, 620)

        self.repo_path = StringVar(value=str(Path.cwd()))
        self.selected_probe = StringVar(value=PROBES[0].key)
        self.status_text = StringVar(value="Ready to run probes.")
        self.last_result = None
        self.task_queue: Queue = Queue()
        self.worker: threading.Thread | None = None

        self._build_layout()
        self._bind_events()
        self._update_probe_description()
        self._poll_queue()

    def _build_layout(self) -> None:
        root = self.root

        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        header = ttk.Frame(root, padding=12)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Repository").grid(row=0, column=0, sticky="w")
        ttk.Entry(header, textvariable=self.repo_path).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(header, text="Browse", command=self._browse_repo).grid(row=0, column=2, sticky="e")

        ttk.Label(header, text="Probe").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.probe_combo = ttk.Combobox(
            header,
            textvariable=self.selected_probe,
            values=[probe.key for probe in PROBES],
            state="readonly",
        )
        self.probe_combo.grid(row=1, column=1, sticky="w", pady=(8, 0))
        self.probe_description = ttk.Label(header, text="", foreground="#4a4a4a", wraplength=520)
        self.probe_description.grid(row=1, column=2, sticky="w", padx=(12, 0), pady=(8, 0))

        action_bar = ttk.Frame(root, padding=(12, 0, 12, 12))
        action_bar.grid(row=1, column=0, sticky="ew")
        action_bar.columnconfigure(0, weight=1)

        self.run_button = ttk.Button(action_bar, text="Run Full Cycle", command=self._run_probe)
        self.run_button.grid(row=0, column=0, sticky="w")

        self.export_button = ttk.Button(action_bar, text="Export Report", command=self._export_report)
        self.export_button.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.export_button.state(["disabled"])

        self.status_label = ttk.Label(action_bar, textvariable=self.status_text)
        self.status_label.grid(row=0, column=2, sticky="e")

        body = ttk.Frame(root, padding=(12, 0, 12, 12))
        body.grid(row=2, column=0, sticky="nsew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(body)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.findings_text = self._make_tab("Findings")
        self.approvals_text = self._make_tab("Approvals")
        self.patches_text = self._make_tab("Patch Proposals")
        self.summary_text = self._make_tab("Summary")
        self.logs_text = self._make_tab("Logs")

        self._set_text(self.logs_text, "Select a probe and run a full cycle to begin.")

    def _make_tab(self, label: str) -> Text:
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        text = Text(frame, wrap="word")
        text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.configure(yscrollcommand=scrollbar.set)
        self.notebook.add(frame, text=label)
        return text

    def _bind_events(self) -> None:
        self.probe_combo.bind("<<ComboboxSelected>>", lambda _event: self._update_probe_description())

    def _update_probe_description(self) -> None:
        probe = self._get_selected_probe()
        if probe:
            self.probe_description.config(text=probe.description)

    def _browse_repo(self) -> None:
        selected = filedialog.askdirectory(title="Select repository")
        if selected:
            self.repo_path.set(selected)

    def _set_text(self, widget: Text, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def _get_selected_probe(self) -> ProbeDefinition | None:
        key = self.selected_probe.get()
        for probe in PROBES:
            if probe.key == key:
                return probe
        return None

    def _run_probe(self) -> None:
        repo = self.repo_path.get().strip()
        if not repo:
            messagebox.showwarning("Missing repository", "Please select a repository path.")
            return
        repo_path = Path(repo)
        if not repo_path.exists():
            messagebox.showerror("Repository not found", f"{repo_path} does not exist.")
            return

        probe = self._get_selected_probe()
        if not probe:
            messagebox.showwarning("Missing probe", "Please select a probe to run.")
            return

        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Probe running", "A probe is already running. Please wait.")
            return

        self.status_text.set("Running probe...")
        self.run_button.state(["disabled"])
        self.export_button.state(["disabled"])
        self._set_text(self.logs_text, f"Running {probe.name} against {repo_path}...\n")

        self.worker = threading.Thread(
            target=self._run_probe_worker,
            args=(repo_path, probe),
            daemon=True,
        )
        self.worker.start()

    def _run_probe_worker(self, repo_path: Path, probe: ProbeDefinition) -> None:
        orchestrator = HexProbeOrchestrator()
        start = time.monotonic()
        try:
            result = orchestrator.run_full_cycle(probe.func, str(repo_path))
            elapsed = time.monotonic() - start
            self.task_queue.put(
                {
                    "type": "result",
                    "payload": result,
                    "elapsed": elapsed,
                    "probe": probe,
                    "repo": str(repo_path),
                }
            )
        except Exception as exc:
            self.task_queue.put(
                {
                    "type": "error",
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                    "probe": probe,
                    "repo": str(repo_path),
                }
            )

    def _poll_queue(self) -> None:
        try:
            while True:
                message = self.task_queue.get_nowait()
                if message["type"] == "result":
                    self._handle_result(message)
                elif message["type"] == "error":
                    self._handle_error(message)
        except Empty:
            pass
        self.root.after(200, self._poll_queue)

    def _handle_result(self, message: dict) -> None:
        result = message["payload"]
        self.last_result = self._serialize_result(message)
        self.export_button.state(["!disabled"])
        elapsed = message["elapsed"]
        probe = message["probe"]

        result_payload = result["result"]
        findings = result_payload.findings
        approvals = result["approvals"]
        patches = result["patches"]

        self._set_text(self.findings_text, self._format_json(findings))
        self._set_text(self.approvals_text, self._format_json(approvals))
        self._set_text(self.patches_text, self._format_json(self._serialize_patches(patches)))

        summary = {
            "severity": result_payload.severity,
            "rationale": result_payload.rationale,
            "repro": result_payload.repro,
            "elapsed_seconds": round(elapsed, 2),
            "probe": probe.name,
        }
        self._set_text(self.summary_text, self._format_json(summary))

        self._append_log(
            f"Completed {probe.name} in {elapsed:.2f}s. Severity: {result_payload.severity}."
        )
        self.status_text.set("Probe completed.")
        self.run_button.state(["!disabled"])

    def _handle_error(self, message: dict) -> None:
        probe = message["probe"]
        self._append_log(f"Probe failed: {probe.name}\n{message['traceback']}")
        self.status_text.set("Probe failed.")
        self.run_button.state(["!disabled"])
        messagebox.showerror("Probe failed", message["error"])

    def _append_log(self, entry: str) -> None:
        self.logs_text.configure(state="normal")
        self.logs_text.insert("end", f"{entry}\n")
        self.logs_text.configure(state="disabled")
        self.logs_text.see("end")

    def _format_json(self, payload: object) -> str:
        return json.dumps(payload, indent=2, default=str)

    def _serialize_patches(self, patches: list) -> list[dict]:
        serialized = []
        for patch in patches:
            serialized.append(
                {
                    "id": getattr(patch, "id", None),
                    "description": getattr(patch, "description", None),
                    "rationale": getattr(patch, "rationale", None),
                    "code_snippet": getattr(patch, "code_snippet", None),
                    "created_at": str(getattr(patch, "created_at", "")),
                }
            )
        return serialized

    def _serialize_result(self, message: dict) -> dict:
        result = message["payload"]
        result_payload = result["result"]
        return {
            "repo": message["repo"],
            "probe": message["probe"].key,
            "elapsed_seconds": round(message["elapsed"], 2),
            "result": {
                "findings": result_payload.findings,
                "severity": result_payload.severity,
                "repro": result_payload.repro,
                "rationale": result_payload.rationale,
            },
            "approvals": result["approvals"],
            "patches": self._serialize_patches(result["patches"]),
        }

    def _export_report(self) -> None:
        if not self.last_result:
            messagebox.showinfo("No results", "Run a probe before exporting a report.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save report",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                json.dump(self.last_result, handle, indent=2)
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))
            return

        self._append_log(f"Report exported to {file_path}")


def main() -> None:
    root = Tk()
    ttk.Style().theme_use("clam")
    HexProbeGUI(root)
    root.mainloop()
