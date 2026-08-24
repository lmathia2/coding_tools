#!/usr/bin/env python3
"""Validate the self-contained Smart Harness using only the standard library."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def fail(msg): raise AssertionError(msg)
def must(path):
    p=ROOT/path
    if not p.exists(): fail(f'missing {path}')
    return p

def main():
    required=['README.md','VERSION','vendor/SOURCES.json','vendor/THIRD_PARTY_NOTICES.md','docs/SELF_CONTAINED.md','docs/VENDORED_COMPONENTS.md','pi/tools/parallel-pi.py','shared/skills/documentation-sync/SKILL.md','shared/skills/superpowers-methodology/SKILL.md','shared/skills/ponytail/SKILL.md','shared/skills/ponytail-review/SKILL.md','shared/skills/vscode/SKILL.md']
    for x in required: must(x)
    sources=json.loads(must('vendor/SOURCES.json').read_text())
    for item in sources['components']:
        must(item['license_file'])
        for path in item['local_paths']: must(path)
    for p in (ROOT/'shared/skills').glob('*/SKILL.md'):
        t=p.read_text()
        if not t.startswith('---\n') or '\n---\n' not in t[4:]: fail(f'{p}: invalid frontmatter')
        front=t[4:t.find('\n---\n',4)]
        if not re.search(r'(?m)^name:\s*\S+',front) or not re.search(r'(?m)^description:\s*\S+',front): fail(f'{p}: name/description required')
    # Only executable harness code is forbidden from installing/fetching third-party
    # runtime resources. Documentation may explain that those operations are not needed.
    runtime_files=[ROOT/'install.sh',ROOT/'install-global.sh',*list((ROOT/'pi/tools').glob('*.py'))]
    forbidden=[r'git\s+clone',r'gh\s+skill\s+install',r'/plugin\s+install',r'copilot\s+plugin\s+install',r'pi\s+install',r'npm\s+install',r'pip(?:3)?\s+install',r'curl\s+https?://',r'wget\s+https?://']
    for p in runtime_files:
        text=p.read_text()
        for pattern in forbidden:
            if re.search(pattern,text,re.I): fail(f'{p.relative_to(ROOT)} contains forbidden runtime external-install pattern {pattern!r}')

    # Legacy external-install and upstream-sync surfaces must not return.
    forbidden_paths=[
        'integrations/install-methodologies.sh',
        'integrations/upstreams.lock.json',
        'scripts/check-upstreams.py',
        'pi/install-extensions.sh',
        'pi/install-skills.sh',
        'pi/extensions.json',
        'pi/skills.json',
    ]
    for path in forbidden_paths:
        if (ROOT/path).exists(): fail(f'legacy external dependency surface still present: {path}')
    if (ROOT.parent/'.github/workflows/smart-harness-upstream-sync.yml').exists():
        fail('legacy network-based upstream sync workflow still present')
    for p in [ROOT/'copilot/agents/dev.agent.md',ROOT/'claude-code/commands/dev.md',ROOT/'pi/prompts/dev.md']:
        text=p.read_text()
        for term in ('plan-first','documentation-sync','ponytail','verification'):
            if term.lower() not in text.lower(): fail(f'{p.relative_to(ROOT)} missing {term}')
    for p in [ROOT/'copilot/agents/review-pr.agent.md',ROOT/'claude-code/commands/review-pr.md',ROOT/'pi/prompts/review-pr.md']:
        text=p.read_text().lower()
        for term in ('worktree','unit','integration','documentation','ponytail-review'):
            if term not in text: fail(f'{p.relative_to(ROOT)} missing {term}')
    if 'packages' in must('pi/settings.example.json').read_text(): fail('Pi settings must not declare external packages')
    print('smart harness validation: PASS'); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except AssertionError as exc: print(f'ERROR: {exc}',file=sys.stderr); raise SystemExit(1)
