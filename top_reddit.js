var express = require('express');
var pg = require("pg");
var app = express();
 
var connectionString = "postgres://allen:123123qwer@104.155.165.207:5432/reddit_db";
 
app.get('/', function (req, res, next) {
    pg.connect(connectionString,function(err,client,done) {
        if(err){
            console.log("not able to get connection "+ err);
            res.status(400).send(err);
        } 
        client.query('SELECT * FROM top_posts WHERE top_rank <= $1 ORDER BY time_top_rank_achieved DESC, top_rank ASC', [10], function(err,result) {
            done(); // closing the connection;
            if(err){
                console.log(err);
                res.status(400).send(err);
            }
	    let returnValue = "";
	    for (let post_index = 0; post_index < Math.min(result.rows.length, 500); ++post_index)
	    {
		returnValue += "<li><h3>" + result.rows[post_index].title + "</h3>" + result.rows[post_index].content + "<br /></li>";
	    }
	    res.status(200).send("<ol>" + returnValue + "</ol>");
        });
    });
});
 
app.listen(4000, function () {
    console.log('Server is running.. on Port 4000');
});
