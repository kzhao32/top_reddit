# top_reddit

## TODO:
1. Fix audio to sync with video. In progress: still need to fix audio looping, and multiple videos on page. Try using https://stackoverflow.com/questions/25105414/html5-video-onmuted-and-onloop-event/25106820#25106820
2. Need to add audio control.
3. Set up cert bot automated renewal

## to get started run:
1. sudo apt update
2. sudo apt install -y python python3-pip
3. python3 -m pip install --user bs4 psycopg2-binary
4. python3 top_reddit_scrape.py
5. do something like http://www.javascriptpoint.com/nodejs-postgresql-tutorial-example/ to start node js server
6. start server with "sudo npm start" ctrl+C just to type in password, then start server again with "sudo npm start &" or start server with something like "nodemon server.js"
7. visit https://topreddit.duckdns.org/?top_rank=10
