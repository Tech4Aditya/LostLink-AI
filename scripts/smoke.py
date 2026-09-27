import urllib.request, json
for url in ["http://localhost:8000/health", "http://localhost:8000/docs"]:
    with urllib.request.urlopen(url, timeout=5) as r:
        print(url, r.status)
