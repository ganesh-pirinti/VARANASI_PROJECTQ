import urllib.request
import re

with urllib.request.urlopen('http://localhost:4173/') as response:
    html = response.read().decode('utf-8')

urls = set()
for match in re.finditer(r'(?:href|src)=["\']([^"\']+)["\']', html):
    url = match.group(1)
    if not url.startswith('http') and not url.startswith('#') and not url.startswith('mailto:'):
        urls.add(url)

print(f"Found {len(urls)} local asset URLs to verify:")
failed = 0
for u in sorted(urls):
    full_url = f"http://localhost:4173/{u.lstrip('/')}"
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            data = res.read()
            print(f"  [200 OK] {u} ({len(data):,} bytes)")
    except Exception as e:
        print(f"  [FAILED] {u} -> {e}")
        failed += 1

print(f"Asset verification finished. Failures: {failed}")
if failed > 0:
    exit(1)
