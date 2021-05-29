import os
from replit import db
from flask import Flask, redirect, url_for, render_template
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized

app = Flask(__name__)

app.secret_key = b"random bytes representing flask secret key"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.

app.config["DISCORD_CLIENT_ID"] = os.environ["client_id"]    # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = os.environ["client_secret"]
app.config["DISCORD_REDIRECT_URI"] = "https://you-are-late.ssebastianoo.repl.co/callback"                 # URL to your callback endpoint.
app.config["DISCORD_BOT_TOKEN"] = ""                    # Required to access BOT resources.

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
  groups = [g for g in db if user.id in db[g]["members"]]
  if len(groups) == 0:
    groups = None
  return render_template("index.html", groups=groups)

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

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