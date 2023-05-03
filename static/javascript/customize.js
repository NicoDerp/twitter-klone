
let stageInputEl = document.querySelector("#stageInput");
stageInputEl.value = "0";

function nextPrompt(skip = false) {
    let setupInputs = document.querySelectorAll(".inputfield>*"); // array med 3 inputs
    let setupHeader = document.querySelector(".settingsheader");

    let stage = Number(setupHeader.getAttribute("value"));

    let listeOverType = ["text", "file", "textarea", "file", "text"];
    let listeOverIndexer = [0, 1, 2, 1, 0];
    let listeOverNokler = ["displayName", "profileImage", "bio", "bannerImage", "location"];
    let listeOverSprml = ["What do you want to be called?", "What do you want your profile picture to be?", "What do you want your bio to be?", "What do you want your profile banner to be?", "What is your location?"]

    setupInputs[listeOverIndexer[stage]].value = "";

    setupInputs[listeOverIndexer[stage]].style.display = "none";

    stage++;
    let stageInputEl = document.querySelector("#stageInput");
    stageInputEl.value = stage;

    if (stage > 4) {
        // gå til home
        window.location.href = "/viewprofile";
    } else {
        // gå til neste prompt
        setupHeader.setAttribute("value", stage);
        setupHeader.innerHTML = listeOverSprml[stage];

        setupInputs[listeOverIndexer[stage]].style.display = "block";
        setupInputs[listeOverIndexer[stage]].focus();
    }



    /*
    Displayname
    0: What do you want to be called?
    Profile picture
    1: What do you want your profile picture to be?
    Bio
    2: What do you want your bio to be?
    Profile banner
    3: What do you want your profile banner to be?
    location
    4: What is your location?
    */

}

function formSubmit() {
    var callback = function() {
        nextPrompt(skip=false);
        frame.onload = null;
    };

    let frame = document.querySelector("#invisibleIframe");
    let form = document.querySelector("#customizeForm");

    frame.onload = callback;
    //form.submit();
    return true;
}
