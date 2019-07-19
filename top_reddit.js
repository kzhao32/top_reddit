var express = require('express');
var pg = require("pg");
var app = express();

var connectionString = "postgres://allen:123123qwer@104.155.165.207:5432/reddit_db";

app.use(express.static(__dirname));

app.get('/', function(req, res, next) {
    pg.connect(connectionString, function(err, client, done) {
        if (err) {
            console.log("not able to get connection " + err);
            res.status(400).send(err);
        }
	let top_rank = req.query.top_rank;
	if (top_rank == null || top_rank < 1) {
		top_rank = 10;
	}
        client.query('SELECT * FROM top_posts WHERE top_rank <= $1 ORDER BY time_top_rank_achieved DESC, top_rank ASC', [top_rank], function(err, result) {
            done(); // closing the connection;
            if (err) {
                console.log(err);
                res.status(400).send(err);
            }
	    // Initialize HTML
            let returnValue = "<meta charset='UTF-8' /><meta name='viewport' content='width=device-width, initial-scale=1' /><title>Top Reddit Posts</title><link rel='stylesheet' href='server.css' /><ol>";
            let re = /"https?:\/\/(i\.redd\.it|v\.redd\.it|i\.imgur\.com|gfycat\.com)\/[^"]*"/;
            let match = "";
	    let mediaTag = "";
	    let imageEnds = [".jpg\"", ".jpeg\"", ".gif\"", ".png\""];
            for (let post_index = 0; post_index < Math.min(result.rows.length, 50); ++post_index) {
                mediaTag = "";
		match = result.rows[post_index].content.match(re);
		if (match != null && match.length > 0) {
		    if (imageEnds.includes(match[0].slice(match[0].lastIndexOf(".")))) {
		        mediaTag = "<img src=" + match[0] + " />";
		    }
		    else {
		        mediaTag = "<video autoplay controls muted loop><source src=" + match[0].replace(".gifv", ".mp4") + " type='video/mp4' /></video>";
		    }
		}
		// Concatenate to HTML
                returnValue += "<li><a href='" + result.rows[post_index].link + "'><h3>" + result.rows[post_index].title + "</h3></a>" + result.rows[post_index].content + mediaTag + "<br /></li>";
            }
            res.status(200).send(returnValue + "</ol>");
        });
    });
});

app.listen(4000, function() {
    console.log('Server is running.. on Port 4000');
});
