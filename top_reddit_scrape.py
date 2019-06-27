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

import top_reddit_backend

# get list of entries from url using BeautifulSoup.
def get_entries(reddit_rss_url):
    # keep trying to read page until we find >0 entries.
    while True:
        try:
            url_client = urlopen(reddit_rss_url)
            page_html = url_client.read()
            url_client.close()
            page_soup = BeautifulSoup(page_html, "html.parser")
            entries = page_soup.findAll("entry");
            if len(entries) > 0:
                return entries
        except Exception: # reddit returns 0 entries if scraping too often to avoid bots.
            print("warning: failed to fetch page, retrying in 2 seconds; ", end=" ")
            time.sleep(2)

# main, used to connect to postgres server, scrape, update table, and commit.
def main():
    num_entries_remaining_to_scrape = 100 # decrease if want only higher quality; increase if want to scrape low quality or r/new.
    print(str(datetime.datetime.now()) + '; ', end=" ") # log time.
    reddit_rss_url = "https://reddit.com/.rss"

    # Connect to SQL server.
    try:
        connection = psycopg2.connect(user = "allen",
                                    password = "123123qwer",
                                    host = "104.155.165.207",
                                    port = "5432",
                                    database = "reddit_db")
        cursor = connection.cursor()
        print("PostgreSQL connection is opened; ", end=" ")

        # create table if it doesn't already exists.
        if not top_reddit_backend.is_table_exists(cursor):
            top_reddit_backend.create_table(cursor)

        # loop to scrap reddit entries
        post_id = ""
        rank_counter = 0
        while num_entries_remaining_to_scrape > 0:
            # call function to get entries using rss url
            if rank_counter == 0:
                entries = get_entries(reddit_rss_url)
            else:
                # if we need to go the next page, then append '?after=' + post_id of last entry of this page
                entries = get_entries(reddit_rss_url + '?after=' + post_id)
            # loop through each entry to scrap content
            for entry in entries:
                author_name = entry.findAll("name")[0].text
                category = entry.findAll("category")[0]['term']
                post_id = entry.findAll("id")[0].text
                link = entry.findAll("link")[0]['href']
                updated = entry.findAll("updated")[0].text
                title = entry.findAll("title")[0].text.replace("'", "''") # this is how you escape the single quote for psycopg2
                content = entry.findAll("content")[0].text.replace("'", "''")

                # debug block
                # print("~~~Entry start~~~~~~~~~~~~~~~~~~~~~")
                # print("author_name = " + author_name)
                # print("category = " + category)
                # print("post_id = " + post_id)
                # print("link = " + link)
                # print("updated = " + updated)
                # print("title = " + title)
                # print("content = " + content)
                # print("~~~Entry end~~~~~~~~~~~~~~~~~~~~~~~\n")

                # add record into table
                top_reddit_backend.modify_record(cursor, post_id, rank_counter+1, category, title, link, author_name, updated, content)
                rank_counter = rank_counter + 1
            num_entries_remaining_to_scrape = num_entries_remaining_to_scrape - len(entries)

        connection.commit() # commit update to sql database
    
    except (Exception, psycopg2.Error) as error :
        print("Error while connecting to PostgreSQL; ", error, end=" ")
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed; ", end=" ")
    print("Done with scrape;")


if __name__ == '__main__':
    main()

