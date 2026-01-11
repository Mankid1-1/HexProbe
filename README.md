# HexProbe

HexProbe is a **self-evolving, multi-agent repository auditing system** designed to detect, analyze, and suggest fixes for code issues across multiple repos.  

## Features

- Multi-agent approval system
- Static analysis, fuzz testing, performance, chaos probes
- Automatic probe generation from memory and past bugs
- Persistent pattern learning and cross-repo memory
- AI-assisted patch synthesis
- Aging and pruning of stale probes

## Folder Structure

- `agents/` – HexProbe agents and approval logic
- `probes/` – All probe types and supporting modules
- `knowledge/` – Persistent learning and pattern analysis
- `memory/` – Cross-repo memory storage
- `maintenance/` – Aging and pruning system
- `ai/` – AI-assisted patch synthesis
- `core/` – Orchestrator coordinating probes, agents, AI, and memory

## Getting Started

1. Clone the repo
2. Install dependencies (e.g., Python 3.10+)
3. Configure `hexprobe.yaml` for your pipeline
4. Run orchestration via `core/synthesis.py`
