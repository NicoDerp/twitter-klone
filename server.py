#!/usr/bin/python3

from flask import Flask
from flask import render_template, redirect, url_for, request

from flask import session
from flask_session import Session

import traceback
import os
import json
import hashlib
import datetime
import difflib
import heapq

from socket import gethostname



def logError(s):
    tb = traceback.format_exc()
    with open("err.log", "a") as f:
        f.write(f"Error: {s}\nTraceback: {tb}\n")


def logInfo(s):
    with open("info.log", "a") as f:
        f.write(f"[INFO] {s}\n")


app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.update(
    SESSION_PERMANENT=False,
    SESSION_TYPE="filesystem",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SECRET_KEY="83012c07d4bc053fc8028c1d14fc065b65c5feff90e2b44f",
    UPLOAD_FOLDER=os.path.join(os.getcwd(), "static/userpics")
)
Session(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def hashPassword(password):
    return hashlib.sha256(password.encode()).hexdigest()


def getUserFromUsername(username):
    users = getUsers()
    if username in users:
        return users[username]

    return None


def validateUserCredentials(username, password):
    users = getUsers()
    hashed_password = hashPassword(password)
    return username in users and users[username]["hashedPassword"] == hashed_password


def newPost(username, content):
    with open("posts.txt", "r") as f:
        posts = json.load(f)

    postID = str(posts["count"])

    post = {
        "username": username,
        "id": postID,
        "isPost": True,
        "content": content,
        "timePosted": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comments": [],
        "likes": 0,
        "retweets": 10,
        "views": 10,
    }

    posts["posts"][postID] = post
    posts["count"] += 1

    with open("posts.txt", "w") as f:
        json.dump(posts, f, default=str, indent=4)

    users = getUsers()
    users[username]["posts"].append(postID)

    saveUsers(users)

    return postID


def newComment(username, targetPostID, content):
    with open("posts.txt", "r") as f:
        posts = json.load(f)

    commentID = str(posts["count"])

    comment = {
        "username": username,
        "id": commentID,
        "isPost": False,
        "content": content,
        "timePosted": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comments": [],
        "likes": 0,
        "retweets": 10,
        "views": 10,
    }

    posts["posts"][commentID] = comment
    posts["count"] += 1

    posts["posts"][targetPostID]["comments"].append(commentID)

    with open("posts.txt", "w") as f:
        json.dump(posts, f, default=str, indent=4)

    users = getUsers()
    users[username]["comments"].append(commentID)

    saveUsers(users)

    return commentID


def getPosts():
    with open("posts.txt", "r") as f:
        posts = json.load(f)

    posts = posts["posts"]

    currentTime = datetime.datetime.now()
    for postID in posts:
        posts[postID]["timePosted"] = datetime.datetime.strptime(posts[postID]["timePosted"], "%Y-%m-%d %H:%M:%S")
        posts[postID]["timeSincePosted"] = prettyFormatTime(currentTime, posts[postID]["timePosted"])
        #posts[postID]["comments"] = [getCommentFromCommentID(commentID) for commentID in posts[postID]["comments"]]

    return posts


def getPostsForUser(user):
    allposts = getPosts()
    posts = {}

    for postID in user["posts"]:
        posts[postID] = allposts[postID]

    return posts


def getUsers():
    with open("users.txt", "r") as f:
        users = json.load(f)

    return users


def saveUsers(users):
    with open("users.txt", "w") as f:
        json.dump(users, f, indent=4)


def prettyFormatTime(cur, posted):
    time = cur - posted

    if time.days > 7:
        return f"{posted.date()}"

    if time.days > 0:
        return f"{time.days}d"

    hours = time.seconds // 3600
    if hours > 0:
        return f"{hours}h"

    minutes = (time.seconds // 60) % 60
    if minutes > 0:
        return f"{minutes}m"

    # Just now?

    return f"{time.seconds}s"


def newUser(username, password, name):
    users = getUsers()

    # Check for duplicates
    if username in users:
        return False

    hashed_password = hashPassword(password)
    new_user = {"username": username,
                "hashedPassword": hashed_password,
                "name": name,
                "profileImage": "default_pfp.png",
                "bannerImage": "default_banner.png",
                "bannerColor": "#808080",
                "posts": [],
                "comments": [],
                "followers": [],
                "following": [],
                "likedPosts": [],
                "pinnedPost": None,
                "bio": "",
                "status": "Offline",
                "location": "",
                "joined": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                "settings": {
                    "theme": "light",
                    "background-color": "#ffffff",
                    "text-color": "#000000",
                    "font": "Inter",
                    "font-size": "1",
                }}

    users[username] = new_user
    saveUsers(users)

    return True


def getWhoToFollowForUser(user):
    users = getUsers()
    users.pop(user["username"])

    for u in user["following"]:
        users.pop(u)

    whotofollow = []
    for i, username in enumerate(users):
        if i == 20:
            break
        whotofollow.append(users[username])
    return whotofollow


def getFollowingPostsForUser(user):
    users = getUsers()
    users.pop(user["username"])

    allposts = getPosts()
    posts = []
    for un in user["following"]:
        u = users[un]
        for postID in u["posts"]:
            post = allposts[postID]
            post["user"] = u  # TODO only pass items that matter
            posts.append(post)

    return posts


def getAllPostsForUser(user):
    users = getUsers()

    allposts = getPosts()
    posts = []
    for postID in allposts:
        post = allposts[postID]
        if post["username"] != user["username"] and post["isPost"]:
            u = users[post["username"]]
            post["user"] = u  # TODO only pass items that matter
            posts.append(post)

    return posts


def getPostFromPostID(postID):
    posts = getPosts()

    if postID in posts:
        post = posts[postID]
        post["last"] = False
        post["comments"] = [getPostFromPostID(commentID) for commentID in posts[postID]["comments"]]
        if len(post["comments"]) != 0:
            post["comments"][-1]["last"] = True
        return post

    return None


def getCommentUsersForPost(post):
    allUsers = getUsers()
    commentUsers = {}
    for comment in post["comments"]:
        username = comment["username"]
        commentUsers[username] = allUsers[username]
    return commentUsers


# Halveis kopiert av https://stackoverflow.com/a/50872841/9983213
def getMatchesForUserAttribute(search, attr):
    users = getUsers()
    users = [(users[k][attr], users[k]["username"]) for k in users]
    n = 10
    cutoff = 0.5

    result = []
    s = difflib.SequenceMatcher()
    s.set_seq2(search)
    for i, (k, u) in enumerate(users):
        s.set_seq1(k)
        if s.real_quick_ratio() >= cutoff and \
           s.quick_ratio() >= cutoff and \
           s.ratio() >= cutoff:
            result.append((s.ratio(), (k, u)))

    result = heapq.nlargest(n, result)
    return [u for score, (k, u) in result]


def searchForUser(s):
    usernameMatches = getMatchesForUserAttribute(s, "username")
    nameMatches = getMatchesForUserAttribute(s, "name")

    users = getUsers()
    matches = list(set(usernameMatches + nameMatches))
    return [users[k] for k in matches]


@app.get("/favicon.ico")
def favicon():
    try:
        return redirect(url_for("static", filename="favicon.ico"))
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.after_request
def after_request(response):
    #logInfo(f"response {request.url}")
    if "logout" in request.url:
        #response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers['Clear-Site-Data'] = '"cache"'
    return response


@app.get("/")
def index():
    try:
        # If user is not logged in then redirect to login page
        if "username" not in session:
            return redirect("/login")

        # Redirect to home
        return redirect("/home")
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/home", strict_slashes=False)
def home():
    try:
        # If user is not logged in then redirect to login page
        if "username" not in session:
            return redirect("/login")

        username = session["username"]
        user = getUserFromUsername(username)

        if not user:
            return redirect("/login")

        followingPosts = getFollowingPostsForUser(user)  # TODO sort after most recent
        allPosts = getAllPostsForUser(user)
        whotofollow = getWhoToFollowForUser(user)
        return render_template("home.html", user=user, followingPosts=followingPosts, allPosts=allPosts, whotofollow=whotofollow)
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.route("/logout", strict_slashes=False)
def logout():
    session["username"] = None
    return redirect("/login")


@app.get("/login", strict_slashes=False)
def loginGET():
    try:
        return render_template("/login.html")
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/login", strict_slashes=False)
def loginPOST():
    try:
        username = request.form.get("brukernavn")
        password = request.form.get("passord")
        if not username or not password:
            return render_template("login.html", error="Error in form")

        if validateUserCredentials(username, password):
            user = getUserFromUsername(username)
            session["username"] = username
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid credentials")

    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/register", strict_slashes=False)
def registerGET():
    try:
        return render_template("/registrere.html")
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/register", strict_slashes=False)
def registerPOST():
    try:
        username = request.form.get("brukernavn")
        password = request.form.get("passord")
        if not username or not password:
            return render_template("registrere.html", error="Error in form")

        #posts = {
        #   "username": "elonmusk",
        #   "content": "I am a tweet",
        #   "coments": [],
        #   "retweets": 10,
        #   "likes": 10,
        #   "views": 10,
        #}

        # comments follow same structure as posts

        success = newUser(username, password, "")
        if not success:
            logInfo("Username already exists")
            return render_template("registrere.html", error="Username already exists")

        newPost(username, "This is a cool tweet")

        logInfo(f"Successfully registered new user '{username}'")

        session["username"] = username
        return redirect("/customize")
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/viewprofile")
@app.get("/viewprofile/<otherUsername>")
def viewprofile(otherUsername=None):
    try:
        if "username" not in session:
            return redirect("/login")

        username = session["username"]
        user = getUserFromUsername(username)

        if not user:
            return redirect("/login")

        if not otherUsername:
            otherUsername = username

        posts = []
        otherUser = getUserFromUsername(otherUsername)
        if otherUser:
            posts = getPostsForUser(otherUser)
            #comments = getComments()

        whotofollow = getWhoToFollowForUser(user)
        return render_template("viewprofile.html", user=user, whotofollow=whotofollow, otherUser=otherUser, posts=posts)
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/settings")
def settings():
    try:
        if "username" not in session:
            return redirect("/login")

        username = session["username"]
        user = getUserFromUsername(username)

        if not user:
            return redirect("/login")

        whotofollow = getWhoToFollowForUser(user)
        return render_template("settings.html", user=user, whotofollow=whotofollow)
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/customize")
def customize():
    try:
        if "username" not in session:
            return redirect("/login")

        username = session["username"]
        user = getUserFromUsername(username)

        if not user:
            return redirect("/login")

        whotofollow = getWhoToFollowForUser(user)
        return render_template("customize.html", user=user, whotofollow=whotofollow)
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/search")
def search():
    try:
        if "username" not in session:
            return redirect("/login")

        username = session["username"]
        user = getUserFromUsername(username)

        if not user:
            return redirect("/login")

        users = []
        searchfor = request.args.get("v", "")
        if searchfor:
            users = searchForUser(searchfor)

        return render_template("sok.html", user=user, searchfor=searchfor, users=users)
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/follow")
def followPOST():
    try:
        usernameToFollow = request.form.get("username")
        if not usernameToFollow:
            logError("Error in post in followPOST")
            return "a"

        username = session["username"]

        users = getUsers()
        if username not in users:
            return redirect("/login")

        if usernameToFollow in users[username]["following"]:
            logError("User already following")
            return "a"

        users[username]["following"].append(usernameToFollow)
        users[usernameToFollow]["followers"].append(username)

        saveUsers(users)

        return "a"

    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/customizeStep")
def customizeStepPOST():
    try:
        first = request.form.get("first")
        third = request.form.get("third")
        stage = request.form.get("stage")
        #if not first or not second or not third or not stage:
        #    logError("Error in post in customizeStepPOST")
        #    return "a"

        username = session["username"]

        users = getUsers()
        if username not in users:
            return redirect("/login")

        # Name
        if stage == "0":
            users[username]["name"] = first

        # Profile picture
        elif stage == "1":
            logInfo(request.files)
            if "second" not in request.files:
                logError("No file part")
                return "a"

            file = request.files["second"]
            if file.filename == "":
                logError("No file selected")
                return "a"

            if not file or not allowed_file(file.filename):
                logError("File not allowed")

            fn, extension = os.path.splitext(file.filename)
            filename = f"{username}_profileImage{extension}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            users[username]["profileImage"] = filename

        # Bio
        elif stage == "2":
            users[username]["bio"] = third

        # Banner
        elif stage == "3":
            logInfo(request.files)
            if "second" not in request.files:
                logError("No file part")
                return "a"

            file = request.files["second"]
            if file.filename == "":
                logError("No file selected")
                return "a"

            if not file or not allowed_file(file.filename):
                logError("File not allowed")

            fn, extension = os.path.splitext(file.filename)
            filename = f"{username}_bannerImage{extension}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            users[username]["bannerImage"] = filename

        # Location
        elif stage == "4":
            users[username]["location"] = first

        else:
            logError(f"Unknown stage {stage} in customizeStepPOST")
            return "a"

        saveUsers(users)

        return "a"

    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/updateProfile")
def updateProfilePOST():
    try:
        field = request.form.get("field")
        #if not first or not second or not third or not stage:
        #    logError("Error in post in customizeStepPOST")
        #    return "a"

        username = session["username"]

        users = getUsers()
        if username not in users:
            return redirect("/login")

        # Name
        if field == "name":
            name = request.form.get("settingsEditProfileDisplayName")
            if not name:
                logError("No name in form")
                return "a"
            users[username]["name"] = name

        # Banner
        elif field == "profileBanner":
            logInfo(request.files)
            if "settingsEditProfileBanner" not in request.files:
                logError("No file part")
                return "a"

            file = request.files["settingsEditProfileBanner"]
            if file.filename == "":
                logError("No file selected")
                return "a"

            if not file or not allowed_file(file.filename):
                logError("File not allowed")

            fn, extension = os.path.splitext(file.filename)
            filename = f"{username}_bannerImage{extension}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            users[username]["bannerImage"] = filename

        # Profile picture
        elif field == "profilePicture":
            logInfo(request.files)
            if "settingsEditProfilePicture" not in request.files:
                logError("No file part")
                return "a"

            file = request.files["settingsEditProfilePicture"]
            if file.filename == "":
                logError("No file selected")
                return "a"

            if not file or not allowed_file(file.filename):
                logError("File not allowed")

            fn, extension = os.path.splitext(file.filename)
            filename = f"{username}_profileImage{extension}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            users[username]["profileImage"] = filename

        # Bio
        elif field == "bio":
            bio = request.form.get("settingsEditProfileBio")
            if not bio:
                logError("No bio in form")
                return "a"
            users[username]["bio"] = bio

        # Location
        elif field == "location":
            location = request.form.get("settingsEditProfileLocation")
            if not location:
                logError("No location in form")
                return "a"
            users[username]["location"] = location

        # Theme
        elif field == "theme":
            themeType = request.form.get("colorThemeType")
            if not themeType:
                logError("No themeType in form")
                return "a"

            if themeType == "0":
                users[username]["settings"]["theme"] = "light"
            elif themeType == "1":
                users[username]["settings"]["theme"] = "dark"
            elif themeType == "2":
                users[username]["settings"]["theme"] = "custom"
            else:
                logError(f"Unknown themeType {themeType} in updateProfilePOST")
                return "a"

        elif field == "customColors":
            bgColor = request.form.get("bgColor")
            fgColor = request.form.get("fgColor")
            if not bgColor or not fgColor:
                logError("No bgColor or fgColor in form")
                return "a"

            users[username]["settings"]["background-color"] = bgColor
            users[username]["settings"]["text-color"] = fgColor

        elif field == "fontSize":
            fontSize = request.form.get("fontSize")
            if not fontSize:
                logError("No fontSize in form")
                return "a"

            users[username]["settings"]["font-size"] = fontSize

        else:
            logError(f"Unknown field {field} in updateProfilePOST")
            return "a"

        saveUsers(users)

        return "a"

    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/bark", strict_slashes=False)
def bark():
    try:
        # If user is not logged in then redirect to login page
        if "username" not in session:
            return redirect("/login")

        username = session["username"]
        user = getUserFromUsername(username)

        if not user:
            return redirect("/login")

        whotofollow = getWhoToFollowForUser(user)
        return render_template("lagtweet.html", user=user, whotofollow=whotofollow)
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.get("/viewpost", strict_slashes=False)
@app.get("/viewpost/<postID>", strict_slashes=False)
def viewpost(postID=None):
    try:
        # If user is not logged in then redirect to login page
        if "username" not in session:
            return redirect("/login")

        username = session["username"]
        user = getUserFromUsername(username)

        if not user:
            return redirect("/login")

        post = None
        postOwner = None
        commentUsers = None

        if postID:
            post = getPostFromPostID(postID)
            if post:
                postOwner = getUserFromUsername(post['username'])
                commentUsers = getCommentUsersForPost(post)

        whotofollow = getWhoToFollowForUser(user)
        return render_template("viewtweet.html", user=user, whotofollow=whotofollow, post=post, postOwner=postOwner, commentUsers=commentUsers)
    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/toggleLike")
def toggleLike():
    try:
        postID = request.form.get("postID")
        if not postID:
            logError("Error in post in toggleLike")
            return "a"

        if "username" not in session:
            logError("Not logged in")
            return "a"

        username = session["username"]

        users = getUsers()
        if username not in users:
            logError("Not logged in")
            return "a"

        with open("posts.txt", "r") as f:
            posts = json.load(f)

        if postID not in posts["posts"]:
            logError(f"Can't follow post with postID {postID} because the post does not exist")
            return "a"

        if postID in users[username]["likedPosts"]:
            posts["posts"][postID]["likes"] -= 1
            users[username]["likedPosts"].remove(postID)
        else:
            posts["posts"][postID]["likes"] += 1
            users[username]["likedPosts"].append(postID)

        saveUsers(users)

        with open("posts.txt", "w") as f:
            json.dump(posts, f, default=str, indent=4)

        return "a"

    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/reply")
def reply():
    try:
        targetPostID = request.form.get("postID")
        content = request.form.get("content")
        if not targetPostID or not content:
            logError("Error in post in reply")
            return "error"

        if "username" not in session:
            logError("Not logged in")
            return redirect("/login")

        username = session["username"]

        users = getUsers()
        if username not in users:
            logError("Not logged in")
            return redirect("/login")

        #if postID not in posts["posts"]:
        #    logError(f"Can't reply to post with postID {postID} because the post does not exist")
        #    return "a"

        commentID = newComment(username, targetPostID, content)
        users[username]["comments"].append(commentID)

        saveUsers(users)

        return redirect(f"/viewpost/{targetPostID}")

    except Exception as e:
        logError(e)
        return f"Error {e}"


@app.post("/bark")
def barkPOST():
    try:
        content = request.form.get("content")
        if not content:
            logError("Error in post in barkPOST")
            return redirect("/home")

        if "username" not in session:
            logError("Not logged in")
            return redirect("/login")

        username = session["username"]

        users = getUsers()
        if username not in users:
            logError("Not logged in")
            return redirect("/login")

        newPost(username, content)

        return redirect("/home")

    except Exception as e:
        logError(e)
        return f"Error {e}"


if __name__ == '__main__':
    if 'liveconsole' not in gethostname():
        context = ("server.crt", "server.key")
        #app.run(host="127.0.0.1", port=8080, ssl_context=context, debug=True)
        app.run(host="127.0.0.1", port=8080, debug=True)

