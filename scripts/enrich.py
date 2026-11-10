"""Enrich repo list with GitHub GraphQL metrics. usage: enrich.py in.json out.json"""
import json, subprocess, sys, time
SINCE = '2025-11-10T00:00:00Z'
FIELDS = '''
 nameWithOwner description url homepageUrl stargazerCount forkCount isArchived isFork createdAt pushedAt
 primaryLanguage{name} licenseInfo{spdxId}
 repositoryTopics(first:12){nodes{topic{name}}}
 openIssues: issues(states:OPEN){totalCount}
 closedIssues: issues(states:CLOSED){totalCount}
 openPRs: pullRequests(states:OPEN){totalCount}
 mergedPRs: pullRequests(states:MERGED){totalCount}
 watchers{totalCount}
 releases(first:1, orderBy:{field:CREATED_AT, direction:DESC}){totalCount nodes{tagName publishedAt}}
 refs(refPrefix:"refs/tags/", first:1, orderBy:{field:TAG_COMMIT_DATE, direction:DESC}){totalCount nodes{name}}
 defaultBranchRef{name target{... on Commit{
   all: history(first:1){totalCount nodes{committedDate}}
   recent: history(since:"%s"){totalCount}
 }}}
''' % SINCE

def run(names):
    parts = []
    for i, n in enumerate(names):
        o, r = n.split('/', 1)
        parts.append(f'r{i}: repository(owner:{json.dumps(o)}, name:{json.dumps(r)}){{{FIELDS}}}')
    q = '{' + '\n'.join(parts) + '}'
    for attempt in range(4):
        p = subprocess.run(['gh','api','graphql','-f',f'query={q}'],capture_output=True,text=True)
        try:
            d = json.loads(p.stdout)
        except Exception:
            d = None
        if d and d.get('data'):
            return [d['data'].get(f'r{i}') for i in range(len(names))], d.get('errors')
        print('retry', p.stderr[:300], (p.stdout or '')[:300], file=sys.stderr); time.sleep(10)
    return [None]*len(names), 'failed'

def main(inp, out, batch=20):
    names = json.load(open(inp))
    names = [n if isinstance(n,str) else n['full_name'] for n in names]
    res, missing = {}, []
    for i in range(0, len(names), batch):
        chunk = names[i:i+batch]
        data, err = run(chunk)
        if err == 'failed' and batch > 1:
            for n in chunk:
                d, _ = run([n]);
                if d[0]: res[n.lower()] = d[0]
                else: missing.append(n)
            continue
        for n, d in zip(chunk, data):
            if d: res[n.lower()] = d
            else: missing.append(n)
        print(f'{i+len(chunk)}/{len(names)}', file=sys.stderr)
    json.dump(res, open(out,'w'))
    print('missing:', missing, file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
