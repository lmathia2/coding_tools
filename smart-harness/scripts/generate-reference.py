#!/usr/bin/env python3
"""Generate docs/REFERENCE.md entirely from repository-local sources."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def scalar(front,key):
    m=re.search(rf'(?m)^{re.escape(key)}:\s*(.+)$',front)
    return m.group(1).strip().strip('"\'') if m else ''

def generate():
    version=(ROOT/'VERSION').read_text().strip()
    models=json.loads((ROOT/'config/models.json').read_text())
    sources=json.loads((ROOT/'vendor/SOURCES.json').read_text())
    skills=[]
    for p in sorted((ROOT/'shared/skills').glob('*/SKILL.md')):
        text=p.read_text(); end=text.find('\n---\n',4); front=text[4:end]
        skills.append((scalar(front,'name'),scalar(front,'description'),str(p.parent.relative_to(ROOT))))
    lines=['# Generated Smart Harness Reference','',f'> Generated from repository-local files for version `{version}`. Do not edit by hand.','', '## Model routing','']
    for platform in ('copilot','claude_code'):
        lines += [f'### {platform.replace("_"," ").title()}','', '| Role | Model | Effort |','|---|---|---|']
        for role,spec in models[platform].items(): lines.append(f'| `{role}` | `{spec["model"]}` | `{spec.get("effort","")}` |')
        lines.append('')
    lines += ['## Shared skills','', '| Skill | Description | Local path |','|---|---|---|']
    for name,desc,path in skills: lines.append(f'| `{name}` | {desc.replace("|","\\|")} | `{path}` |')
    lines += ['','## Vendored sources','', '| Component | Pinned commit | License | Local paths |','|---|---|---|---|']
    for item in sources['components']:
        paths=', '.join(f'`{p}`' for p in item['local_paths'])
        lines.append(f'| {item["name"]} | `{item["commit"]}` | {item["license"]} | {paths} |')
    lines += ['','## Runtime network dependency','', 'None. Installers copy repository-local files only. Host applications and target-project dependencies are prerequisites, not downloaded by this harness.','']
    return '\n'.join(lines)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args(); path=ROOT/'docs/REFERENCE.md'; new=generate()
    if args.check:
        if not path.exists() or path.read_text()!=new: print('generated reference is stale'); return 1
        print('generated reference is current'); return 0
    path.write_text(new); print(f'wrote {path.relative_to(ROOT)}'); return 0
if __name__=='__main__': raise SystemExit(main())
