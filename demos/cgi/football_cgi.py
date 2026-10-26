#!/usr/bin/env python3
import cgi, html, os
print("Content-Type: text/html; charset=utf-8\n")
form = cgi.FieldStorage()
method = os.environ.get("REQUEST_METHOD", "GET")
player = html.escape(form.getfirst("player", "Guest"))
team = html.escape(form.getfirst("team", "Any team"))
print('''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Touchline CGI</title></head><body>
<h1>Touchline Player Lookup</h1>
<form method="GET"><label>Player <input name="player"></label><label>Team <input name="team"></label><button>Search with GET</button></form>
<form method="POST"><label>Player <input name="player"></label><label>Team <input name="team"></label><button>Send with POST</button></form>''')
print(f"<p>Request method: <b>{html.escape(method)}</b></p><p>Player: <b>{player}</b></p><p>Team: <b>{team}</b></p></body></html>")
