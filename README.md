# top_reddit

## TODO:
1. Fix audio to sync with video.
2. Set up cert bot automated renewal
3. Combine subreddits like "https://topreddit.duckdns.org/r/aww+gifs".
4. Create a 404 page for URLs like "https://topreddit.duckdns.org/eawsfnan".
5. Create a read-only user for the database (maybe a user with only SELECT privileges).

## to get started run:
1. sudo apt update
2. sudo apt install -y python python3-pip
3. python3 -m pip install --user bs4 psycopg2-binary
4. python3 top_reddit_scrape.py
5. do something like http://www.javascriptpoint.com/nodejs-postgresql-tutorial-example/ to start node js server
6. start server with "sudo npm start" ctrl+C just to type in password, then start server again with "sudo npm start &" or start server with something like "nodemon server.js"
7. visit https://topreddit.duckdns.org/?top_rank=10
