"""Monthly commit counts (last 12 months) for a list of repos. usage: monthly.py names.json out.json"""
import json, subprocess, sys, time, datetime
months = []
d = datetime.date(2025, 11, 1)
for i in range(13):
    nxt = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    months.append((d.isoformat(), nxt.isoformat())); d = nxt
def frag(i):
    hs = ' '.join(f'm{j}: history(since:"{a}T00:00:00Z", until:"{b}T00:00:00Z"){{totalCount}}' for j,(a,b) in enumerate(months))
    return hs
names = json.load(open(sys.argv[1])); out = {}
B = 6
for k in range(0, len(names), B):
    chunk = names[k:k+B]
    q = '{' + '\n'.join(f'r{i}: repository(owner:{json.dumps(n.split("/")[0])}, name:{json.dumps(n.split("/")[1])}){{defaultBranchRef{{target{{... on Commit{{{frag(i)}}}}}}}}}' for i,n in enumerate(chunk)) + '}'
    for attempt in range(3):
        p = subprocess.run(['gh','api','graphql','-f',f'query={q}'],capture_output=True,text=True)
        try: data = json.loads(p.stdout).get('data') or {}
        except Exception: data = {}
        if data: break
        time.sleep(5)
    for i,n in enumerate(chunk):
        r = data.get(f'r{i}')
        try: out[n.lower()] = [r['defaultBranchRef']['target'][f'm{j}']['totalCount'] for j in range(len(months))]
        except Exception: pass
    print(k, file=sys.stderr)
json.dump({'months':[m[0] for m in months], 'counts':out}, open(sys.argv[2],'w'))
