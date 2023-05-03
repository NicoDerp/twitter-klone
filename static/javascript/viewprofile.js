
function showPosts() {
    let postsDiv = document.querySelector("#postsDiv");
    let postsLine = document.querySelector("#postsLine");

    let commentsDiv = document.querySelector("#commentsDiv");
    let commentsLine = document.querySelector("#commentsLine");

    postsDiv.style.display = "block";
    postsLine.style.display = "block";

    commentsDiv.style.display = "none";
    commentsLine.style.display = "none";
}

function showComments() {
    let postsDiv = document.querySelector("#postsDiv");
    let postsLine = document.querySelector("#postsLine");

    let commentsDiv = document.querySelector("#commentsDiv");
    let commentsLine = document.querySelector("#commentsLine");

    postsDiv.style.display = "none";
    postsLine.style.display = "none";

    commentsDiv.style.display = "block";
    commentsLine.style.display = "block";
}

function toggleFollowText(button) {
    profileFollowersCount = document.querySelector("#profileFollowersCount");

    if (button.innerText == "Follow") {
        button.innerText = "Unfollow";
        profileFollowersCount.innerHTML = parseInt(profileFollowersCount.innerHTML) + 1;
    } else {
        button.innerText = "Follow";
        profileFollowersCount.innerHTML = parseInt(profileFollowersCount.innerHTML) - 1;
    }
}
