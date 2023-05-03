
function showFollowingPosts() {
    followingFeed = document.querySelector("#followingFeed");
    followingLine = document.querySelector("#followingLine");

    allFeed = document.querySelector("#allFeed");
    allLine = document.querySelector("#allLine");

    followingFeed.style.display = "block";
    followingLine.style.display = "block";

    allFeed.style.display = "none";
    allLine.style.display = "none";
}

function showAllPosts() {
    followingFeed = document.querySelector("#followingFeed");
    followingLine = document.querySelector("#followingLine");

    allFeed = document.querySelector("#allFeed");
    allLine = document.querySelector("#allLine");

    followingFeed.style.display = "none";
    followingLine.style.display = "none";

    allFeed.style.display = "block";
    allLine.style.display = "block";
}
