import bs4
from bs4 import BeautifulSoup
from urllib import urlopen
import top_reddit_backend

def main():
    reddit_rss_url = "https://reddit.com/.rss"
    url_client = urlopen(reddit_rss_url)
    page_html = url_client.read()
    url_client.close()
    #with urlopen(reddit_rss_url) as url_client:
    #    page_html = url_client.read()
    # html parsing
    page_soup = BeautifulSoup(page_html, "html.parser")
    # find 25 entries
    entries = page_soup.findAll("entry");
    for entry in entries:
        username = entry.findAll("name")[0].text
        subreddit = entry.findAll("category")[0]['term']
        post_hash = entry.findAll("id")[0].text
        post_url = entry.findAll("link")[0]['href']
        last_updated = entry.findAll("updated")[0].text
        title = entry.findAll("title")[0].text

        print("username = " + username)
        print("subreddit = " + subreddit)
        print("post_hash = " + post_hash)
        print("post_url = " + post_url)
        print("last_updated = " + last_updated)
        print("title = " + title)


if __name__ == '__main__':
    main()
