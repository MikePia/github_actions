from duckduckgo_search import DDGS

with DDGS() as ddgs:
    for i, r in enumerate(ddgs.text('live free or die', region='wt-wt', safesearch='off', timelimit='y')):
        print()
        print(f'{i+1}:', r['title'])
        print(r['href'])
        print(r['body'][:110])
        if i >= 35:
            break

# Searching for pdf files
with DDGS() as ddgs:
    for r in ddgs.text('russia filetype:pdf', region='wt-wt', safesearch='off', timelimit='y'):
        print()
        print(f'{i+1}:', r['title'])
        print(r['href'])
        print(r['body'][:110])
        if i >= 35:
            break

# Using lite backend and limit the number of results to 10
from itertools import islice

with DDGS() as ddgs:
    ddgs_gen = ddgs.text("notes from a dead house", backend="lite")
    for r in islice(ddgs_gen, 10):
        print()
        print(f'{i+1}:', r['title'])
        print(r['href'])
        print(r['body'][:110])