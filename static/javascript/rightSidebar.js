

let fjernQueryKnapp = document.querySelector("#fjernQueryKnapp");
fjernQueryKnapp.addEventListener("click", clearSearch);

function clearSearch() {
    let sokfeltEl = document.querySelector("#sokfelt");
    sokfeltEl.value = "";
    sokfeltEl.focus();
}

function followUser(form) {
    var callback = function() {
        form.parentElement.parentElement.remove();
        frame.onload = null;
    };

    let frame = document.querySelector("#rightSidebarInvisibleIframe");

    frame.onload = callback;
    //form.submit();
    return true;
}

