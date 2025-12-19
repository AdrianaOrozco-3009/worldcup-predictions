from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# ------------------------
# Google Sheets setup
# ------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Use environment variable on Render, fallback to local JSON
if 'GOOGLE_CREDS_JSON' in os.environ:
    creds_dict = json.loads(os.environ['GOOGLE_CREDS_JSON'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)

client = gspread.authorize(creds)

SHEET_ID = "1yCf3io3Hywr5dnmu6a_kr2dktAvqoG7CU2CbAiEDbVY"
pred_sheet = client.open_by_key(SHEET_ID).worksheet("Predictions")
leaderboard_sheet = client.open_by_key(SHEET_ID).worksheet("Leaderboard")
results_sheet = client.open_by_key(SHEET_ID).worksheet("Results")

# ------------------------
# Flask app
# ------------------------
app = Flask(__name__)

# ------------------------
# FIFA World Cup 2026 Matches (Groups A-L)
# ------------------------
matches = [
    # Group A
    {"match": "A1 Mexico vs South Africa", "team1": "Mexico", "team2": "South Africa"},
    {"match": "A2 South Korea vs Playoff D", "team1": "South Korea", "team2": "Playoff D"},
    {"match": "A3 Mexico vs South Korea", "team1": "Mexico", "team2": "South Korea"},
    {"match": "A4 South Africa vs Playoff D", "team1": "South Africa", "team2": "Playoff D"},
    {"match": "A5 Mexico vs Playoff D", "team1": "Mexico", "team2": "Playoff D"},
    {"match": "A6 South Africa vs South Korea", "team1": "South Africa", "team2": "South Korea"},
    
    # Group B
    {"match": "B1 Canada vs Playoff A", "team1": "Canada", "team2": "Playoff A"},
    {"match": "B2 Qatar vs Switzerland", "team1": "Qatar", "team2": "Switzerland"},
    {"match": "B3 Canada vs Qatar", "team1": "Canada", "team2": "Qatar"},
    {"match": "B4 Switzerland vs Playoff A", "team1": "Switzerland", "team2": "Playoff A"},
    {"match": "B5 Canada vs Switzerland", "team1": "Canada", "team2": "Switzerland"},
    {"match": "B6 Qatar vs Playoff A", "team1": "Qatar", "team2": "Playoff A"},
    
    # Group C
    {"match": "C1 Brazil vs Morocco", "team1": "Brazil", "team2": "Morocco"},
    {"match": "C2 Haiti vs Scotland", "team1": "Haiti", "team2": "Scotland"},
    {"match": "C3 Brazil vs Haiti", "team1": "Brazil", "team2": "Haiti"},
    {"match": "C4 Morocco vs Scotland", "team1": "Morocco", "team2": "Scotland"},
    {"match": "C5 Brazil vs Scotland", "team1": "Brazil", "team2": "Scotland"},
    {"match": "C6 Morocco vs Haiti", "team1": "Morocco", "team2": "Haiti"},
    
    # Group D
    {"match": "D1 USA vs Paraguay", "team1": "USA", "team2": "Paraguay"},
    {"match": "D2 Australia vs Playoff C", "team1": "Australia", "team2": "Playoff C"},
    {"match": "D3 USA vs Australia", "team1": "USA", "team2": "Australia"},
    {"match": "D4 Paraguay vs Playoff C", "team1": "Paraguay", "team2": "Playoff C"},
    {"match": "D5 USA vs Playoff C", "team1": "USA", "team2": "Playoff C"},
    {"match": "D6 Paraguay vs Australia", "team1": "Paraguay", "team2": "Australia"},

    # Group E
    {"match": "E1 Spain vs Costa Rica", "team1": "Spain", "team2": "Costa Rica"},
    {"match": "E2 Germany vs Playoff H", "team1": "Germany", "team2": "Playoff H"},
    {"match": "E3 Spain vs Germany", "team1": "Spain", "team2": "Germany"},
    {"match": "E4 Costa Rica vs Playoff H", "team1": "Costa Rica", "team2": "Playoff H"},
    {"match": "E5 Spain vs Playoff H", "team1": "Spain", "team2": "Playoff H"},
    {"match": "E6 Costa Rica vs Germany", "team1": "Costa Rica", "team2": "Germany"},

    # Group F
    {"match": "F1 France vs Playoff F", "team1": "France", "team2": "Playoff F"},
    {"match": "F2 Belgium vs Tunisia", "team1": "Belgium", "team2": "Tunisia"},
    {"match": "F3 France vs Belgium", "team1": "France", "team2": "Belgium"},
    {"match": "F4 Playoff F vs Tunisia", "team1": "Playoff F", "team2": "Tunisia"},
    {"match": "F5 France vs Tunisia", "team1": "France", "team2": "Tunisia"},
    {"match": "F6 Belgium vs Playoff F", "team1": "Belgium", "team2": "Playoff F"},

    # Group G
    {"match": "G1 Argentina vs Playoff E", "team1": "Argentina", "team2": "Playoff E"},
    {"match": "G2 Netherlands vs Poland", "team1": "Netherlands", "team2": "Poland"},
    {"match": "G3 Argentina vs Netherlands", "team1": "Argentina", "team2": "Netherlands"},
    {"match": "G4 Playoff E vs Poland", "team1": "Playoff E", "team2": "Poland"},
    {"match": "G5 Argentina vs Poland", "team1": "Argentina", "team2": "Poland"},
    {"match": "G6 Netherlands vs Playoff E", "team1": "Netherlands", "team2": "Playoff E"},

    # Group H
    {"match": "H1 Portugal vs Playoff G", "team1": "Portugal", "team2": "Playoff G"},
    {"match": "H2 Italy vs South Africa", "team1": "Italy", "team2": "South Africa"},
    {"match": "H3 Portugal vs Italy", "team1": "Portugal", "team2": "Italy"},
    {"match": "H4 Playoff G vs South Africa", "team1": "Playoff G", "team2": "South Africa"},
    {"match": "H5 Portugal vs South Africa", "team1": "Portugal", "team2": "South Africa"},
    {"match": "H6 Italy vs Playoff G", "team1": "Italy", "team2": "Playoff G"},

    # Group I
    {"match": "I1 England vs Playoff I", "team1": "England", "team2": "Playoff I"},
    {"match": "I2 Senegal vs Mexico", "team1": "Senegal", "team2": "Mexico"},
    {"match": "I3 England vs Senegal", "team1": "England", "team2": "Senegal"},
    {"match": "I4 Playoff I vs Mexico", "team1": "Playoff I", "team2": "Mexico"},
    {"match": "I5 England vs Mexico", "team1": "England", "team2": "Mexico"},
    {"match": "I6 Senegal vs Playoff I", "team1": "Senegal", "team2": "Playoff I"},

    # Group J
    {"match": "J1 Morocco vs Playoff J", "team1": "Morocco", "team2": "Playoff J"},
    {"match": "J2 USA vs Playoff K", "team1": "USA", "team2": "Playoff K"},
    {"match": "J3 Morocco vs USA", "team1": "Morocco", "team2": "USA"},
    {"match": "J4 Playoff J vs Playoff K", "team1": "Playoff J", "team2": "Playoff K"},
    {"match": "J5 Morocco vs Playoff K", "team1": "Morocco", "team2": "Playoff K"},
    {"match": "J6 USA vs Playoff J", "team1": "USA", "team2": "Playoff J"},

    # Group K
    {"match": "K1 Croatia vs Playoff L", "team1": "Croatia", "team2": "Playoff L"},
    {"match": "K2 Denmark vs Iran", "team1": "Denmark", "team2": "Iran"},
    {"match": "K3 Croatia vs Denmark", "team1": "Croatia", "team2": "Denmark"},
    {"match": "K4 Playoff L vs Iran", "team1": "Playoff L", "team2": "Iran"},
    {"match": "K5 Croatia vs Iran", "team1": "Croatia", "team2": "Iran"},
    {"match": "K6 Denmark vs Playoff L", "team1": "Denmark", "team2": "Playoff L"},

    # Group L
    {"match": "L1 Japan vs Ecuador", "team1": "Japan", "team2": "Ecuador"},
    {"match": "L2 South Korea vs Saudi Arabia", "team1": "South Korea", "team2": "Saudi Arabia"},
    {"match": "L3 Japan vs South Korea", "team1": "Japan", "team2": "South Korea"},
    {"match": "L4 Ecuador vs Saudi Arabia", "team1": "Ecuador", "team2": "Saudi Arabia"},
    {"match": "L5 Japan vs Saudi Arabia", "team1": "Japan", "team2": "Saudi Arabia"},
    {"match": "L6 Ecuador vs South Korea", "team1": "Ecuador", "team2": "South Korea"},
]

# ------------------------
# Load actual results
# ------------------------
def load_results():
    actual_results_raw = results_sheet.get_all_records()
    results = {}
    for row in actual_results_raw:
        match = row['Match']
        score1 = int(row['Score1'])
        score2 = int(row['Score2'])
        results[match] = (score1, score2)
    return results

actual_results_cache = load_results()

@app.route("/reload_results")
def reload_results():
    global actual_results_cache
    actual_results_cache = load_results()
    return "Results reloaded successfully!"

# ------------------------
# Routes
# ------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        # Prepare batch for predictions
        new_rows = []
        for m in matches:
            score1 = request.form.get(f"{m['match']}_score1")
            score2 = request.form.get(f"{m['match']}_score2")
            new_rows.append([str(datetime.now()), username, m["match"], m["team1"], m["team2"], score1, score2])
        # Batch append
        pred_sheet.append_rows(new_rows, value_input_option='USER_ENTERED')
        calculate_leaderboard()
        return redirect("/leaderboard")
    return render_template("index.html", matches=matches)

@app.route("/leaderboard")
def leaderboard():
    data = leaderboard_sheet.get_all_records()
    sorted_data = sorted(data, key=lambda x: x['Points'], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_data)

# ------------------------
# Leaderboard calculation (batch update)
# ------------------------
d
