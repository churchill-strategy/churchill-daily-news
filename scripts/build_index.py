"""Builds index.json: the latest 5:00 a.m. briefing for each province or territory,
with slide paths, headlines and sources, for churchillstrategy.ca to read."""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, 'daily')
latest, history = {}, {}

for date in sorted(os.listdir(DAILY)):
    if not re.match(r'\d{4}-\d{2}-\d{2}$', date):
        continue
    for region in sorted(os.listdir(os.path.join(DAILY, date))):
        rdir = os.path.join(DAILY, date, region)
        cap = os.path.join(rdir, 'captions.md')
        if not os.path.isfile(cap):
            continue
        pdfs = {f.split('-')[0]: f for f in os.listdir(rdir) if f.endswith('.pdf')}
        names = {re.sub(r'\.pdf$', '', f).split('-', 1)[1].replace('-', ' '): code for code, f in pdfs.items() if '-' in f}
        text = open(cap, encoding='utf-8').read()
        for sec in re.split(r'^## ', text, flags=re.M)[1:]:
            head, _, body = sec.partition('\n')
            name = re.sub(r'\s*\(\d+ slides?\)\s*$', '', head).strip()
            code = names.get(name) or next((c for n, c in names.items() if n.lower() == name.lower()), None)
            if not code or not os.path.isdir(os.path.join(rdir, code)):
                continue
            lines = [l.strip() for l in body.strip().split('\n') if l.strip()]
            intro = lines[0] if lines else ''
            heads = []
            for l in lines[1:]:
                if l.startswith('Public sources only') or l.startswith('Source:'):
                    break
                m = re.match(r'(BREAKING:\s*)?(.*?)\s*\(([^)]+)\)$', l)
                if m:
                    heads.append({'breaking': bool(m.group(1)), 'headline': m.group(2), 'level': m.group(3)})
            srcs = [re.match(r'Source:\s*(.*?),\s*(https?://\S+)', l) for l in lines if l.startswith('Source:')]
            srcs = [(s.group(1), s.group(2)) for s in srcs if s]
            for i, h in enumerate(heads):
                if i < len(srcs):
                    h['source'], h['url'] = srcs[i]
            slides = sorted(f for f in os.listdir(os.path.join(rdir, code)) if f.endswith('.jpg'))
            entry = {
                'code': code, 'name': name, 'date': date, 'region': region, 'intro': intro,
                'slides': [f'daily/{date}/{region}/{code}/{s}' for s in slides],
                'pdf': f'daily/{date}/{region}/{pdfs[code]}', 'items': heads,
            }
            latest[code] = entry
            history.setdefault(code, []).append(date)

out = {
    'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'base': 'https://raw.githubusercontent.com/churchill-strategy/churchill-daily-news/main/',
    'latest': dict(sorted(latest.items())),
    'history': {k: sorted(set(v), reverse=True)[:14] for k, v in sorted(history.items())},
}
open(os.path.join(ROOT, 'index.json'), 'w', encoding='utf-8').write(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
print('index.json:', ', '.join(f"{k} {v['date']}" for k, v in out['latest'].items()))
