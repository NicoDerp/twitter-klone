
function updateWordCount(textarea) {
    let characterCount = document.querySelector("#characterIndicator");
    let count = textarea.value.length;
    characterCount.innerText = count + "/250";
    if (count > 250) {
        characterCount.classList.add("invalidCharacterIndicator");
    } else {
        characterCount.classList.remove("invalidCharacterIndicator");
    }
}

function submitBark() {
    let textarea = document.querySelector("#tweetTextArea");
    let count = textarea.value.length;

    if (count > 250) {
        let errorMessage = document.querySelector("#errorMessage");
        errorMessage.innerHTML = "Bark exceeds word limit of 250 words!";
        errorMessage.style.display = "block";
        setTimeout(function() {
            errorMessage.style.display = "none";
        }, 6000);
        return false;
    }

    return true;
}
