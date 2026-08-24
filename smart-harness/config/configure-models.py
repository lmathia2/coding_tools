#!/usr/bin/env python3
"""Apply local config/models.json to Copilot and Claude Code frontmatter."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
CONFIG=json.loads((HERE/'models.json').read_text(encoding='utf-8'))
ROLE_RE=re.compile(r'<!--\s*harness-role:\s*([a-z-]+)\s*-->')

def rewrite(path:Path, platform:str)->str|None:
    text=path.read_text(encoding='utf-8'); match=ROLE_RE.search(text)
    if not match: return None
    spec=CONFIG[platform].get(match.group(1))
    if not spec: raise RuntimeError(f'{path}: missing role {match.group(1)!r}')
    end=text.find('\n---\n',4)
    if not text.startswith('---\n') or end<0: raise RuntimeError(f'{path}: invalid frontmatter')
    front,body=text[4:end],text[end+5:]
    model=spec['model']
    front=re.sub(r'(?m)^model:\s*.*$',f'model: {model}',front) if re.search(r'(?m)^model:',front) else front+f'\nmodel: {model}'
    if platform=='claude_code':
        effort=spec.get('effort')
        if effort: front=re.sub(r'(?m)^effort:\s*.*$',f'effort: {effort}',front) if re.search(r'(?m)^effort:',front) else front+f'\neffort: {effort}'
        else: front=re.sub(r'(?m)^effort:\s*.*\n?','',front)
    return '---\n'+front.rstrip()+'\n---\n'+body

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    files=[*((p,'copilot') for p in (ROOT/'copilot/agents').glob('*.agent.md')),*((p,'claude_code') for p in (ROOT/'claude-code/agents').glob('*.md')),*((p,'claude_code') for p in (ROOT/'claude-code/commands').glob('*.md'))]
    stale=[]
    for path,platform in files:
        new=rewrite(path,platform)
        if new is not None and new!=path.read_text(encoding='utf-8'):
            stale.append(str(path.relative_to(ROOT)))
            if not args.check: path.write_text(new,encoding='utf-8')
    if args.check and stale:
        print('stale model frontmatter:'); print('\n'.join('  '+x for x in stale)); return 1
    print('model configuration is current' if args.check or not stale else 'updated model frontmatter')
    return 0
if __name__=='__main__': raise SystemExit(main())
