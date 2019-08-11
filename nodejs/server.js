var express = require('express');
var pg = require("pg");
const pug = require('pug');
var app = express();

// Constants
const WEBSITE_URL = "https://topreddit.duckdns.org";
const PORT = 4000;

const CONNECTION_STRING = "postgres://read_only:123123qwer" +
    "@104.155.165.207:5432/reddit_db";
const DEFAULT_CONFIG = new Map([
    ["num_posts", 25],
    ["top_rank", 10],
    ["top_rank_subreddit", 25],
    ["count", 0],
    ["after", null]
]);

// Set the directory containing files.
app.use(express.static(__dirname));

// Route paths
app.get('/r', function(req, res, next) {
    res.redirect("/r/popular");
});

app.get('/r/:subreddit', function(req, res, next) {
    var subreddit = req.params.subreddit;
    if (subreddit === "popular" || subreddit === "nsfw") {
        get_subreddit(req, res, next, subreddit);
    }
    else {
        if (subreddit.split('+').includes("popular")) {
            subreddit = subreddit.split('+');
            subreddit.splice(subreddit.indexOf("popular"), 1);
            subreddit = subreddit.join('+');
            res.redirect("/r/" + subreddit);
        }
        else {
            get_subreddit(req, res, next, subreddit);
        }
    }
});

app.get('/', function(req, res, next) {
    get_subreddit(req, res, next, "popular")
    
});

// Starts the HTTP server listening for connections.
app.listen(PORT, function() {
    console.log(`Server is running.. on Port ${PORT}`);
});

function get_subreddit(req, res, next, subreddit) {
    pg.connect(CONNECTION_STRING, function(err, client, done) {
        check_error(res, err);

        [ table_name, num_posts, top_rank, count, after, after_sql ] = get_query_parameters(req, subreddit);

        client.query("\
            SELECT * \
                FROM " + table_name + " \
                WHERE top_rank <= " + top_rank + " " +
		    (subreddit === "popular" || subreddit === "nsfw" ?
                        "" : 
                        "AND category IN ('" + subreddit.split('+').join("', '") + "') ") + 
		    after_sql + "\
                ORDER BY time_top_rank_achieved DESC, top_rank ASC, updated DESC",
            function(err, result) {
                get_HTML(done, err, result, res, subreddit, table_name, num_posts, top_rank, count, after, after_sql);
            }
        );
    });
}

function check_error(res, err) {
    if (err) {
        console.log(err);
        res.status(400).send(err);
    }
}

function get_query_parameters(req, subreddit) {
    // Query parameters
    let table_name = subreddit === "popular" ? "top_posts" : (subreddit === "nsfw" ? "nsfw_subreddits" : "subreddits");
    let num_posts = req.query.num_posts;
    if (num_posts == null || num_posts < 1) {
        num_posts = DEFAULT_CONFIG.get("num_posts");
    }
    let top_rank = req.query.top_rank;
    if (top_rank == null || top_rank < 1) {
        top_rank = DEFAULT_CONFIG.get(
            subreddit === "popular" ? "top_rank" : "top_rank_subreddit"
        );
    }
    let count = req.query.count;
    if (count == null || count < 1) {
        count = DEFAULT_CONFIG.get("count");
    }
    let after = req.query.after;
    let after_sql = "";
    if (after != null && after != "undefined") {
        // filter posts to older time_top_rank_achieved, lower top_rank, or older updated
	after_sql = "\
            AND (time_top_rank_achieved < (\
		SELECT time_top_rank_achieved \
		    FROM " + table_name + " WHERE post_id = '" + after + "') \
                OR (time_top_rank_achieved = (\
		    SELECT time_top_rank_achieved \
			FROM " + table_name + " WHERE post_id = '" + after + "') \
			AND top_rank > (\
			    SELECT top_rank FROM " + table_name + " \
			    WHERE post_id = '" + after + "'))\
		OR (time_top_rank_achieved = (\
		    SELECT time_top_rank_achieved \
			FROM " + table_name + " WHERE post_id = '" + after + "') \
			AND top_rank = (\
			    SELECT top_rank FROM " + table_name + " \
			    WHERE post_id = '" + after + "')\
			AND updated < (\
			    SELECT updated FROM " + table_name + " \
			    WHERE post_id = '" + after + "')\
		)\
	    ) ";
    }
    return [ table_name, num_posts, top_rank, count, after, after_sql ];
}

function get_HTML(done, err, result, res, subreddit, table_name, num_posts, top_rank, count, after, after_sql) {
    done(); // closing the connection;
    check_error(err);

    // Initialize HTML
    let return_value = "";
    return_value += get_HTML_header();
    return_value += get_HTML_dropdown_boxes(subreddit, num_posts, top_rank, count, after);
    [ HTML_posts, post_index ] = get_HTML_posts(subreddit, count, result, num_posts);
    return_value += HTML_posts;
    return_value += get_HTML_next_page_link(post_index, result, num_posts, subreddit, top_rank, count);
    res.status(200).send(return_value);
}

function get_HTML_header() {
    return "\
        <meta charset='UTF-8' />\
        <meta name='viewport' content='width=device-width, initial-scale=1' />\
        <title>Top Reddit Posts</title>\
        <link rel='stylesheet' type='text/css' href='" + WEBSITE_URL + "/server.css' />\
    ";
}

function get_HTML_dropdown_boxes(subreddit, num_posts, top_rank, count, after) {
    return "\
        <div>\
            <div class='dropdown'>\
                <button class='dropbtn'>num_posts</button>\
                <div class='dropdown-content'>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" +   1 + "&top_rank=" + top_rank + "&count=" + count + "&after=" + after + "'>  1</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" +  10 + "&top_rank=" + top_rank + "&count=" + count + "&after=" + after + "'> 10</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" +  25 + "&top_rank=" + top_rank + "&count=" + count + "&after=" + after + "'> 25</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" + 100 + "&top_rank=" + top_rank + "&count=" + count + "&after=" + after + "'>100</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" + 500 + "&top_rank=" + top_rank + "&count=" + count + "&after=" + after + "'>500</a>\
                </div>\
            </div>\
            <div class='dropdown'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>\
            <div class='dropdown'>\
                <button class='dropbtn'>&nbsp;&nbsp;top_rank&nbsp;&nbsp;</button>\
                <div class='dropdown-content'>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" + num_posts + "&top_rank=" +   1 + "&count=" + count + "&after=" + after + "'>  1</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" + num_posts + "&top_rank=" +   5 + "&count=" + count + "&after=" + after + "'>  5</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" + num_posts + "&top_rank=" +  10 + "&count=" + count + "&after=" + after + "'> 10</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" + num_posts + "&top_rank=" +  25 + "&count=" + count + "&after=" + after + "'> 25</a>\
                    <a href='" + WEBSITE_URL + "/r/" + subreddit + "/?num_posts=" + num_posts + "&top_rank=" + 100 + "&count=" + count + "&after=" + after + "'>100</a>\
                </div>\
            </div>\
            <br />\
        </div>\
        <div>\
    ";
}

function get_HTML_posts(subreddit, count, result, num_posts) {
    return_value = "\
        <div>\
            <ol start='" + (parseInt(count) + 1) + "'>";
    let re = /"https?:\/\/(i\.redd\.it|v\.redd\.it|i\.imgur\.com|gfycat\.com)\/[^"]*"/;
    let match = "";
    let media_tag = "";
    let imageEnds = [".jpg\"", ".jpeg\"", ".gif\"", ".png\""];
    let post_index = 0; // need post_index after for loop for 'next_page' link
    for ( ; post_index < Math.min(result.rows.length, num_posts); ++post_index) {
        media_tag = "";
        post_content = result.rows[post_index].content;
        match = post_content.match(re);
        if (match != null && match.length > 0) {
            // media tag depends on whether it's an image, gfycat gif, or reddit video
            if (imageEnds.includes(match[0].slice(match[0].lastIndexOf(".")))) { // images
                media_tag = "<img src=" + match[0] + " />";
            } else if (match[0].includes("gfycat.com")) { // gfycat gifs
                if (match[0].indexOf("-") > 0) { // need to omit anything after hyphen for ifr gfycat
                    match[0] = match[0].substr(0, match[0].indexOf("-")) + "\"";
                }
                media_tag = "<iframe src=" + match[0].replace("gfycat.com", "gfycat.com/ifr") + " frameborder='0' allowfullscreen></iframe>"
            } else if (match[0].includes("v.redd.it")) { // reddit videos
                post_id = result.rows[post_index].post_id;
		media_tag = "\
                    <video id=\"" + post_id + "_video\" autoplay controls muted loop type=\"video/mp4\">\
                        <source src=" + match[0].replace(/\"$/, "/DASH_720\"") + " />\
                        <source src=" + match[0].replace(/\"$/, "/DASH_480\"") + " />\
                        <source src=" + match[0].replace(/\"$/, "/DASH_240\"") + " />\
                        <source src=" + match[0].replace(/\"$/,  "/DASH_96\"") + " />\
			<audio id=\"" + post_id + "_audio\" controls loop>\
			    <source src=" + match[0].replace(/\"$/, "/audio\"") + " type=\"audio/mp4\" />\
			</audio>\
                    </video>\
		    <script>\
			//console.log(\"testing, should show in web browser console\");\n\
			var " + post_id + "_video = document.getElementById(\"" + post_id + "_video\");\n\
			var " + post_id + "_audio = document.getElementById(\"" + post_id + "_audio\");\n\
			var change_time_state = true;\n\
\n\
			" + post_id + "_video.onplay = function(){\n\
			    " + post_id + "_audio.play();\n\
			    if(change_time_state){\n\
				" + post_id + "_audio.currentTime = " + post_id + "_video.currentTime;\n\
				change_time_state = false;\n\
			    }\n\
			}\n\
\n\
			" + post_id + "_video.onpause = function(){\n\
			    " + post_id + "_audio.pause();\n\
			    change_time_state = true;\n\
			}\n\
		    </script>";
            }
        }
        if (media_tag !== "") {
            post_content = post_content.replace(/<img[^>]+>/, "");
	    media_tag += "<br />";
        }
        // generate custom post content
        post_updated = result.rows[post_index].updated.toISOString().replace("T", " ");
        category = result.rows[post_index].category;
	// add media
	post_content = post_content.replace("&#32; submitted by &#32; ", media_tag + "&#32; submitted by &#32; ");
        // add subreddit
	if (subreddit !== "popular") {
	    post_content = post_content.replace("<br/>", " to <a href=\"https://www.reddit.com/r/" + category + "/\"> r/" + category + " </a><br/>");
	}
	// add date
        post_content = post_content.replace("<br/>", " on " + post_updated.substring(0, post_updated.lastIndexOf(":")) + "<br/>");
        // redirect subreddit to topreddit.duckdns.org instead of reddit.com
	if (subreddit !== "nsfw") {
	    post_content = post_content.replace("<a href=\"https://www.reddit.com/r/" + category + "/\">", "<a href=\"" + WEBSITE_URL + "/r/" + category + "/\">");
        }
	// add top_rank
	post_content = post_content.replace("[comments]</a></span>", "[comments]</a></span> &#32; <span>[top_rank=" + result.rows[post_index].top_rank + "]</span>");
	return_value += "\
            <li>\
                <a href='" + result.rows[post_index].link + "'>\
                    <h2>" + result.rows[post_index].title + "</h2>\
                </a>" + post_content + "\
            </li>";
    }
    return_value += "\
            </ol>\
        </div>";
    return [ return_value, post_index ];
}

function get_HTML_next_page_link(post_index, result, num_posts, subreddit, top_rank, count) {
    return_value = "";
    // return_value += "<input type=\"text\"><button type=\"button\">Start Scraping Subreddit</button>" + '<form action="/team_name_url/" method="post"> <label for="team_name">Enter name: </label>        <input id="team_name" type="text" name="name_field" value="Default name for team.">            <input type="submit" value="OK">        </form>' + " next count = " + (parseInt(count) + post_index) + " and next after = " + result.rows[post_index-1].post_id;
    // Next page anchor tag
    if (post_index > 0) {
        if (result.rows.length < num_posts) {
            return_value += "\
            <div>\
                No additional posts found.\
            </div>";
        }
        else {
            return_value += "\
                <div>\
                    <a class='next_page' href='" + WEBSITE_URL + "/r/" + subreddit + "/" + "?num_posts=" + num_posts + "&top_rank=" + top_rank + "&count=" + (parseInt(count) + post_index) + "&after=" + result.rows[post_index-1].post_id + "'>Next Page</a>\
                </div>";
        }
    }
    else {
        return_value += "<div>Sorry, no posts found</div>";
    }
    return return_value;
}

// Handle 404
app.use(function(req, res) {
    res.status(400).send("404. Page not found!"); // 400 = bad request
});

