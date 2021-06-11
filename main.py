import os, json, uuid
from replit import db
from flask import Flask, redirect, url_for, render_template, request, Response
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized

if not db.get("groups"):
  db["groups"] = dict()

app = Flask(__name__)

app.secret_key = b"bruh"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = os.environ["client_id"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["client_secret"]
app.config[
    "DISCORD_REDIRECT_URI"] = "https://ur-late.ssebastianoo.repl.co/callback"
app.config["DISCORD_BOT_TOKEN"] = ""

discord = DiscordOAuth2Session(app)

@app.route("/login/")
def login():
    return discord.create_session(scope=["identify"])

@app.route("/callback/")
def callback():
    discord.callback()
    return redirect("/")

@app.route("/")
@requires_authorization
def index():
    user = discord.fetch_user()
    groups = {
        g: db["groups"][g]
        for g in db["groups"] if user.id in db["groups"][g]["access"]
    }
    if len(groups) == 0:
        groups = None
    return render_template("index.html", groups=groups)

@app.route("/api/v1/groups/create/", methods=["POST"])
def create_group():
    "create a new group"

    u_id = uuid.uuid1().int
    user = discord.fetch_user()
    name = request.form["name"]
    db["groups"][u_id] = {"name": name, "members": {}, "access": [user.id]}
    return redirect(url_for("index"))

@app.route("/api/v1/groups/delete/", methods=["POST"])
def delete_group():
    "delete a group"

    group_id = request.form["group_id"]
    del db["groups"][group_id]
    return redirect(url_for("index"))

@app.route("/api/v1/lates/create/", methods=["POST"])
def add_late():
    "add a late to a member"
  
    data = request.form
    db["groups"][data["group_id"]]["members"][data["member"]][uuid.uuid1().int] = {"date": data["date"], "late": data["late"]}
    return redirect(url_for("index"))

@app.route("/api/v1/lates/delete/", methods=["POST"])
def remove_late():
    "remove a late to a member"
  
    data = request.form
    del db["groups"][data["group_id"]]["members"][data["member"]][data["late"]]

    return redirect(url_for("index"))

@app.route("/api/v1/members/create/", methods=["POST"])
def add_member():
    "add a member to a group"

    data = request.form
    db["groups"][data["group_id"]]["members"][data["member"]] = {}
    return redirect(url_for("index"))

@app.route("/api/v1/members/delete/", methods=["POST"])
def delete_member():
    "delete a member from a group"

    data = request.form
    del db["groups"][data["group_id"]]["members"][data["member"]]
    return redirect(url_for("index"))

@app.route("/api/v1/groups/display/", methods=["GET"])
def groups():
    "Get a user's groups"
    user = discord.fetch_user()
    groups = dict()
    for group in db["groups"]:
      if user.id in db["groups"][group]["access"]:
        g_ = dict()
        for value in db["groups"][group]:
          if value == "members":
              g_[value] = dict()
              for member in db["groups"][group][value]:
                  g_[value][member] = dict()
                  for date_id in db["groups"][group][value][member]:
                    dates = dict()
                    for x in db["groups"][group][value][member][date_id]:
                      dates[x] = db["groups"][group][value][member][date_id][x]
                    g_[value][member][date_id] = dates
          elif value == "access":
                  g_[value] = list()
                  for access in db["groups"][group][value]:
                      g_[value].append(access)

          else:
              g_[value] = db["groups"][group][value]
          groups[group] = g_
    if len(groups) == 0:
        groups = Response(response="No groups", status=404)
    else:
        groups = Response(response=json.dumps(groups),
                          status=200,
                          mimetype='application/json')
    return groups

@app.route("/main")
def main():
  return render_template("main.html")

@app.route("/layout")
def layout():
  return render_template("layout.html")

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return render_template("main.html")

@app.route("/me/")
@requires_authorization
def me():
    user = discord.fetch_user()
    return f"""
    <html>
        <head>
            <title>{user.name}</title>
        </head>
        <body>
            <img src='{user.avatar_url}' />
        </body>
    </html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)