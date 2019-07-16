let linebreak = document.createElement("br");

let node = document.createElement("li");
let textnode = document.createTextNode("Water");
node.appendChild(textnode);
document.getElementById("list_of_top_posts").appendChild(node);

let node2 = document.createElement("li");
let textnode2 = document.createTextNode("Fire");
node2.appendChild(textnode2);
document.getElementById("list_of_top_posts").appendChild(node2);


function createPost(title, content)
{
  let reddit_post_node = document.createElement("li");
  let h3_node = document.createElement("h3");
  h3_node.innerHTML = title;
  reddit_post_node.appendChild(h3_node);
  let content_node = document.createElement("table");
  content_node.innerHTML = content
  reddit_post_node.appendChild(content_node)
  reddit_post_node.appendChild(linebreak)

  document.getElementById("list_of_top_posts").appendChild(reddit_post_node);
}

createPost("test title", "test content");
createPost("new title", "asd content");
createPost("old title", "zxc content");
createPost("qwe title", "fsghjkasmonqrsh");
