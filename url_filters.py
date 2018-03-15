from collections import defaultdict

# https://www150.statcan.gc.ca/n1/daily-quotidien/000105/dq000105a-eng.htm
# https://www150.statcan.gc.ca/n1/daily-quotidien/000105/dq000105b-eng.htm
# https://www150.statcan.gc.ca/n1/daily-quotidien/130103/dq130103c-eng.htm?rid=3572
# https://www150.statcan.gc.ca/n1/daily-quotidien/180126/dq180126f-eng.htm?rid=3572
# https://www150.statcan.gc.ca/n1/daily-quotidien/130103/dq130103d-eng.htm?rid=1000

def daily_archive_filter(urls, latest=None, current=None):
    if not latest:
        latest = daily_latest_filter(urls)
    if not current:
        current = daily_filter(urls, latest)
    res = {}
    for link, d in urls.items():
        link = link.replace('.ca/daily', '.ca/n1/daily')
        i = link.find('?rid=')
        if i > 0:
            link = link[:i]
        if link and link not in latest and link not in current:
            res[link] = d
    return res

def proc(url):
        url = url.replace('.ca/daily', '.ca/n1/daily')
        if url.find('/n1/daily') < 0: return None, None # vs '/daily-q..'
        i = url.find('?rid=')
        if i < 0: return None, None
        url, rid = url[:i], url[i+5:]
        return url, rid

def daily_filter(urls, latest=None):
    if not latest:
        latest = daily_latest_filter(urls)
    res = {}
    for url, d in urls.items():
        link, _ = proc(url)
        if link and link not in latest:
            ds = int(url.split('/')[5])
            if ds < 150616: continue
            res[link] = d
    return res

def daily_latest_filter(urls):
    rids = defaultdict(list)
    new_urls={}
    for url, d in urls.items():
        link, rid = proc(url)
        if link:
            new_urls[link] = d
            rids[rid].append(link)
    res = {}
    for rid, links in rids.items():
        links.sort()
        url = links[-1]
        res[url] = new_urls[url]
    return res

