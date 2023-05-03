
function redirectToPost(event, url) {
    if (event.target.tagName != "BUTTON" && event.target.closest("button") == null) {
        location.href = url;
    }
}
