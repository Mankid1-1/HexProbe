# HexProbe

HexProbe is an **advanced multi-agent, self-learning repository auditing system** designed to
detect, analyze, and resolve code issues automatically. It combines static analysis, fuzzing,
performance and chaos probes with assisted patch suggestions and cross-repo memory to learn
from prior fixes and improve over time.

## What it does

- Runs multi-agent approval across probe findings
- Executes static, fuzz, performance, and chaos probes
- Generates new probes based on learned patterns
- Records findings and lineage for long-term memory
- Synthesizes patch suggestions for detected issues
- Prunes stale probes and patterns to keep memory fresh

## Repository layout

- `agents/` – agent approval logic
- `probes/` – probe implementations (static/fuzz/perf/chaos + generated)
- `knowledge/` – local pattern learning
- `memory/` – cross-repo memory storage
- `maintenance/` – aging and pruning routines
- `ai/` – patch synthesis helpers
- `core/` – orchestrator and shared storage utilities

## Quickstart

1. **Install dependencies**
   ```bash
   poetry install
   ```
2. **Run a probe cycle programmatically**
   ```python
   from core.synthesis import HexProbeOrchestrator
   from probes.static.surface_sweep import surface_sweep

   orchestrator = HexProbeOrchestrator()
   result = orchestrator.run_full_cycle(surface_sweep, repo=".")
   print(result["result"].findings)
   ```
3. **Optional: configure the pipeline**
   Edit `hexprobe.yaml` to control which probes run in your pipeline.

## Configuration

HexProbe uses local SQLite databases for knowledge and global memory.

- Data directory defaults to `~/.hexprobe`
- Override with `HEXPROBE_DATA_DIR=/path/to/dir`

Databases created:

- `hexprobe_knowledge.db` (local knowledge)
- `global.db` (cross-repo memory)

## Notes

- No external backend is required; everything runs locally by default.
- If you embed HexProbe in CI, set `HEXPROBE_DATA_DIR` to a writable path.
