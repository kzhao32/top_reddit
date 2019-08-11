#!/usr/bin/env python

from __future__ import print_function
import bs4
from bs4 import BeautifulSoup
import datetime
import psycopg2
import sys
import time
if sys.version_info[0] < 3:
    from urllib import urlopen
else:
    from urllib.request import urlopen

import backend

TABLE_NAME = "subreddits"


# Get list of entries from url using BeautifulSoup.
def get_entries(reddit_rss_url):
    # Keep trying to read page until we find >0 entries.
    tries = 10
    while tries > 0:
        tries -= 1
        try:
            url_client = urlopen(reddit_rss_url)
            page_html = url_client.read()
            url_client.close()
            page_soup = BeautifulSoup(page_html, "html.parser")
            entries = page_soup.findAll("entry");
            if len(entries) > 0:
                return entries
        except Exception: # Reddit returns 0 entries if scraping too often to avoid bots.
            print("warning: failed to fetch page, retrying in 2 seconds; ", end=" ")
            time.sleep(2)
    return


# main: used to connect to postgres server, scrape, update table, and commit.
def main():
    print(str(datetime.datetime.now()) + '; ', end=" ") # log time.

    reddit_rss_url = "https://reddit.com/.rss"

    # Connect to SQL server.
    try:
        connection = backend.get_connection()
        cursor = connection.cursor()
        print("PostgreSQL connection is opened; ", end=" ")

        # Create table if it doesn't already exists.
        if not backend.is_table_exists(cursor, TABLE_NAME):
            backend.create_table(cursor, TABLE_NAME)

        # Scrape every subreddit of posts that reach front page.
        post_id = ""
        subreddits = backend.get_subreddits(cursor, "top_posts")
        subreddits_counter = 0
        for subreddit in subreddits:
            print(str(subreddits_counter) + ": scraping " + subreddit[0] + ".")
            subreddits_counter += 1
            rank_counter = 0
            # Call function to get entries using rss url.
            entries = get_entries("https://reddit.com/r/" + subreddit[0] + "/.rss")
            # Skip unsuccessful return value, such as /r/FBIOpenUp.
            if entries is None:
                continue
            # Loop through each entry to scrape content.
            for entry in entries:
                author_name = "/u/[deleted]"
                if len(entry.findAll("name")) > 0:
                    author_name = entry.findAll("name")[0].text
                category = entry.findAll("category")[0]['term']
                post_id = entry.findAll("id")[0].text
                link = entry.findAll("link")[0]['href']
                updated = entry.findAll("updated")[0].text
                title = entry.findAll("title")[0].text.replace("'", "''") # this is how you escape the single quote for psycopg2
                content = entry.findAll("content")[0].text.replace("'", "''")

                # --- Debug Block ---
                # print("~~~Entry start~~~~~~~~~~~~~~~~~~~~~")
                # print("author_name = " + author_name)
                # print("category = " + category)
                # print("post_id = " + post_id)
                # print("link = " + link)
                # print("updated = " + updated)
                # print("title = " + title)
                # print("content = " + content)
                # print("~~~Entry end~~~~~~~~~~~~~~~~~~~~~~~\n")

                # Add entry as a record into table.
                backend.modify_record(cursor, TABLE_NAME, post_id, rank_counter+1, category, title, link, author_name, updated, content)
                rank_counter = rank_counter + 1
            # Commit updates to database every 25 subreddits.
            if (subreddits_counter % 25 == 0):
                print("Committing to database now.***************")
                connection.commit()
        # Do a final commit to database after all subreddits.
        print("Committing to database now.***************")
        connection.commit()
    
    except (Exception, psycopg2.Error) as error :
        print("Error while connecting to PostgreSQL; ", error, end=" ")
    finally:
        # Close database connection.
        backend.close_connection(connection)
    print(str(datetime.datetime.now()) + '; ', end=" ") # log time.
    print("Done with scrape;")


if __name__ == '__main__':
    main()

