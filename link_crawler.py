import re
import urlparse
from datetime import datetime,timedelta
import robotparser
import pickle
import zlib
from downloader import Downloader,Cache

def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, user_agent='wswp', proxies=None, num_retries=1, scrape_callback=None,cache=None):
    """Crawl from the given seed URL following links matched by link_regex
    """
    fn=open('flag.txt','a')
    fn.write('1')
    fn.flush()
    fn.close()
    # the queue of URL's that still need to be crawled
    crawl_queue = [seed_url]
    # the URL's that have been seen and at what depth
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent,num_retries=num_retries,cache=cache)
    count=0
    while crawl_queue:
        if count>=4:
            break
        else:
            count+=1
        url = crawl_queue.pop()
        depth = seen[url]
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            html = D(url)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])

            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url



def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp
        

def get_links(html):
    """Return a list of links from html 
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    expire=timedelta(days=30)
    timenow=datetime.utcnow()
    try:
        fileread=open('cache.pkl','rb')
        timenow,c=pickle.loads(zlib.decompress(fileread.read()))
        if timenow+expire<=datetime.utcnow():
            raise Exception('cache is expired')
    except Exception ,e:
        #print str(e)
        fn=open('flag.txt','w')
        fn.write('1')
        fn.flush()
        fn.close()
        c=Cache()
    #link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=1,cache=c,user_agent='GoodCrawler')
    print 'Cache is saving'
    # pklfilewrite=open('data.pkl','wb')
    # pickle.dump(pripire,pklfilewrite)
    fn=open('flag.txt','r')
    flag=fn.read()
    if flag=='11':
        timenow=datetime.utcnow()
    data=pickle.dumps((timenow,c))
    pklfilewrite=open('cache.pkl','wb')
    pklfilewrite.write(zlib.compress(data))
