from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# ------------------------
# Google Sheets setup
# ------------------------
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]

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
# FIFA World Cup 2026 Group-Stage Matches (A-L)
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
    {"match": "F1 France vs Playoff E", "team1": "France", "team2": "Playoff E"},
    {"match": "F2 England vs Japan", "team1": "England", "team2": "Japan"},
    {"match": "F3 France vs England", "team1": "France", "team2": "England"},
    {"match": "F4 Playoff E vs Japan", "team1": "Playoff E", "team2": "Japan"},
    {"match": "F5 France vs Japan", "team1": "France", "team2": "Japan"},
    {"match": "F6 Playoff E vs England", "team1": "Playoff E", "team2": "England"},

    # Group G
    {"match": "G1 Argentina vs Playoff F", "team1": "Argentina", "team2": "Playoff F"},
    {"match": "G2 Netherlands vs Ecuador", "team1": "Netherlands", "team2": "Ecuador"},
    {"match": "G3 Argentina vs Netherlands", "team1": "Argentina", "team2": "Netherlands"},
    {"match": "G4 Playoff F vs Ecuador", "team1": "Playoff F", "team2": "Ecuador"},
    {"match": "G5 Argentina vs Ecuador", "team1": "Argentina", "team2": "Ecuador"},
    {"match": "G6 Playoff F vs Netherlands", "team1": "Playoff F", "team2": "Netherlands"},

    # Group H
    {"match": "H1 Portugal vs Playoff G", "team1": "Portugal", "team2": "Playoff G"},
    {"match": "H2 Italy vs Senegal", "team1": "Italy", "team2": "Senegal"},
    {"match": "H3 Portugal vs Italy", "team1": "Portugal", "team2": "Italy"},
    {"match": "H4 Playoff G vs Senegal", "team1": "Playoff G", "team2": "Senegal"},
    {"match": "H5 Portugal vs Senegal", "team1": "Portugal", "team2": "Senegal"},
    {"match": "H6 Playoff G vs Italy", "team1": "Playoff G", "team2": "Italy"},

    # Group I
    {"match": "I1 Belgium vs Playoff I", "team1": "Belgium", "team2": "Playoff I"},
    {"match": "I2 Croatia vs Cameroon", "team1": "Croatia", "team2": "Cameroon"},
    {"match": "I3 Belgium vs Croatia", "team1": "Belgium", "team2": "Croatia"},
    {"match": "I4 Playoff I vs Cameroon", "team1": "Playoff I", "team2": "Cameroon"},
    {"match": "I5 Belgium vs Cameroon", "team1": "Belgium", "team2": "Cameroon"},
    {"match": "I6 Playoff I vs Croatia", "team1": "Playoff I", "team2": "Croatia"},

    # Group J
    {"match": "J1 Morocco vs Playoff J", "team1": "Morocco", "team2": "Playoff J"},
    {"match": "J2 Denmark vs USA", "team1": "Denmark", "team2": "USA"},
    {"match": "J3 Morocco vs Denmark", "team1": "Morocco", "team2": "Denmark"},
    {"match": "J4 Playoff J vs USA", "team1": "Playoff J", "team2": "USA"},
    {"match": "J5 Morocco vs USA", "team1": "Morocco", "team2": "USA"},
    {"match": "J6 Playoff J vs Denmark", "team1": "Playoff J", "team2": "Denmark"},

    # Group K
    {"match": "K1 Switzerland vs Playoff K", "team1": "Switzerland", "team2": "Playoff K"},
    {"match": "K2 Uruguay vs Tunisia", "team1": "Uruguay", "team2": "Tunisia"},
    {"match": "K3 Switzerland vs Uruguay", "team1": "Switzerland", "team2": "Uruguay"},
    {"match": "K4 Playoff K vs Tunisia", "team1": "Playoff K", "team2": "Tunisia"},
    {"match": "K5 Switzerland vs Tunisia", "team1": "Switzerland", "team2": "Tunisia"},
    {"match": "K6 Playoff K vs Uruguay", "team1": "Playoff K", "team2": "Uruguay"},

    # Group L
    {"match": "L1 Poland vs Playoff L", "team1": "Poland", "team2": "Playoff L"},
    {"match": "L2 South Korea vs Iran", "team1": "South Korea", "team2": "Iran"},
    {"match": "L3 Poland vs South Korea", "team1": "Poland", "team2": "South Korea"},
    {"match": "L4 Playoff L vs Iran", "team1": "Playoff L", "team2": "Iran"},
    {"match": "L5 Poland vs Iran", "team1": "Poland", "team2": "Iran"},
    {"match": "L6 Playoff L vs South Korea", "team1": "Playoff L", "team2": "South Korea"},
]

# ------------------------
# Load actual results once
# ------------------------
def load_results():
    rows = results_sheet.get_all_records()
    results = {}
    for r in rows:
        match = r["Match"]
        score1 = int(r["Score1"])
        score2 = int(r["Score2"])
        results[match] = (score1, score2)
    return results

actual_results_cache = load_results()

@app.route("/reload_results")
def reload_results():
    global actual_results_cache
    actual_results_cache = load_results()
    return "Results reloaded!"

# ------------------------
# Routes
# ------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        new_rows = []
        for m in matches:
            score1 = request.form.get(f"{m['match']}_score1")
            score2 = request.form.get(f"{m['match']}_score2")
            new_rows.append([str(datetime.now()), username, m["match"], m["team1"], m["team2"], score1, score2])
        calculate_leaderboard_from_rows(new_rows)
        pred_sheet.append_rows(new_rows)
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
def calculate_leaderboard_from_rows(new_rows):
    predictions = pred_sheet.get_all_records()
    for row in new_rows:
        predictions.append({
            "Username": row[1],
            "Match": row[2],
            "Score1": row[5],
            "Score2": row[6]
        })

    scores = {}
    for pred in predictions:
        user = pred["Username"]
        match = pred["Match"]
        s1 = int(pred["Score1"])
        s2 = int(pred["Score2"])
        actual = actual_results_cache.get(match)
        if not actual:
            continue
        points, correct_score, correct_result = 0, 0, 0
        if (s1, s2) == actual:
            points = 3
            correct_score = 1
        elif (s1 - s2)*(actual[0]-actual[1]) > 0 or (s1==s2 and actual[0]==actual[1]):
            points = 1
            correct_result = 1
        if user not in scores:
            scores[user] = {"Points":0,"Correct Score":0,"Correct Result":0}
        scores[user]["Points"] += points
        scores[user]["Correct Score"] += correct_score
        scores[user]["Correct Result"] += correct_result

    rows = [["Username","Points","Correct Score","Correct Result"]]
    for user, data in scores.items():
        rows.append([user, data["Points"], data["Correct Score"], data["Correct Result"]])
    leaderboard_sheet.clear()
    leaderboard_sheet.update(rows)

# ------------------------
# Run app
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
