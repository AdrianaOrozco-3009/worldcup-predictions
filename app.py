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
# FIFA World Cup 2026 Matches (Group A-L)
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
    {"match": "E2 Germany vs Playoff B", "team1": "Germany", "team2": "Playoff B"},
    {"match": "E3 Spain vs Germany", "team1": "Spain", "team2": "Germany"},
    {"match": "E4 Costa Rica vs Playoff B", "team1": "Costa Rica", "team2": "Playoff B"},
    {"match": "E5 Spain vs Playoff B", "team1": "Spain", "team2": "Playoff B"},
    {"match": "E6 Costa Rica vs Germany", "team1": "Costa Rica", "team2": "Germany"},

    # Group F
    {"match": "F1 Belgium vs Tunisia", "team1": "Belgium", "team2": "Tunisia"},
    {"match": "F2 USA vs Japan", "team1": "USA", "team2": "Japan"},
    {"match": "F3 Belgium vs USA", "team1": "Belgium", "team2": "USA"},
    {"match": "F4 Tunisia vs Japan", "team1": "Tunisia", "team2": "Japan"},
    {"match": "F5 Belgium vs Japan", "team1": "Belgium", "team2": "Japan"},
    {"match": "F6 Tunisia vs USA", "team1": "Tunisia", "team2": "USA"},

    # Group G
    {"match": "G1 France vs Canada", "team1": "France", "team2": "Canada"},
    {"match": "G2 Denmark vs Playoff E", "team1": "Denmark", "team2": "Playoff E"},
    {"match": "G3 France vs Denmark", "team1": "France", "team2": "Denmark"},
    {"match": "G4 Canada vs Playoff E", "team1": "Canada", "team2": "Playoff E"},
    {"match": "G5 France vs Playoff E", "team1": "France", "team2": "Playoff E"},
    {"match": "G6 Canada vs Denmark", "team1": "Canada", "team2": "Denmark"},

    # Group H
    {"match": "H1 England vs Iran", "team1": "England", "team2": "Iran"},
    {"match": "H2 Senegal vs Playoff F", "team1": "Senegal", "team2": "Playoff F"},
    {"match": "H3 England vs Senegal", "team1": "England", "team2": "Senegal"},
    {"match": "H4 Iran vs Playoff F", "team1": "Iran", "team2": "Playoff F"},
    {"match": "H5 England vs Playoff F", "team1": "England", "team2": "Playoff F"},
    {"match": "H6 Iran vs Senegal", "team1": "Iran", "team2": "Senegal"},

    # Group I
    {"match": "I1 Argentina vs Poland", "team1": "Argentina", "team2": "Poland"},
    {"match": "I2 Saudi Arabia vs Mexico", "team1": "Saudi Arabia", "team2": "Mexico"},
    {"match": "I3 Argentina vs Saudi Arabia", "team1": "Argentina", "team2": "Saudi Arabia"},
    {"match": "I4 Poland vs Mexico", "team1": "Poland", "team2": "Mexico"},
    {"match": "I5 Argentina vs Mexico", "team1": "Argentina", "team2": "Mexico"},
    {"match": "I6 Poland vs Saudi Arabia", "team1": "Poland", "team2": "Saudi Arabia"},

    # Group J
    {"match": "J1 Portugal vs Morocco", "team1": "Portugal", "team2": "Morocco"},
    {"match": "J2 Uruguay vs Playoff G", "team1": "Uruguay", "team2": "Playoff G"},
    {"match": "J3 Portugal vs Uruguay", "team1": "Portugal", "team2": "Uruguay"},
    {"match": "J4 Morocco vs Playoff G", "team1": "Morocco", "team2": "Playoff G"},
    {"match": "J5 Portugal vs Playoff G", "team1": "Portugal", "team2": "Playoff G"},
    {"match": "J6 Morocco vs Uruguay", "team1": "Morocco", "team2": "Uruguay"},

    # Group K
    {"match": "K1 Italy vs Cameroon", "team1": "Italy", "team2": "Cameroon"},
    {"match": "K2 Ecuador vs Playoff H", "team1": "Ecuador", "team2": "Playoff H"},
    {"match": "K3 Italy vs Ecuador", "team1": "Italy", "team2": "Ecuador"},
    {"match": "K4 Cameroon vs Playoff H", "team1": "Cameroon", "team2": "Playoff H"},
    {"match": "K5 Italy vs Playoff H", "team1": "Italy", "team2": "Playoff H"},
    {"match": "K6 Cameroon vs Ecuador", "team1": "Cameroon", "team2": "Ecuador"},

    # Group L
    {"match": "L1 Netherlands vs Senegal", "team1": "Netherlands", "team2": "Senegal"},
    {"match": "L2 Iran vs Playoff I", "team1": "Iran", "team2": "Playoff I"},
    {"match": "L3 Netherlands vs Iran", "team1": "Netherlands", "team2": "Iran"},
    {"match": "L4 Senegal vs Playoff I", "team1": "Senegal", "team2": "Playoff I"},
    {"match": "L5 Netherlands vs Playoff I", "team1": "Netherlands", "team2": "Playoff I"},
    {"match": "L6 Senegal vs Iran", "team1": "Senegal", "team2": "Iran"},
]

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
        if new_rows:
            pred_sheet.append_rows(new_rows)  # Batch write
        calculate_leaderboard()
        return redirect("/leaderboard")
    return render_template("index.html", matches=matches)

@app.route("/leaderboard")
def leaderboard():
    data = leaderboard_sheet.get_all_records()
    sorted_data = sorted(data, key=lambda x: x['Points'], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_data)

# ------------------------
# Leaderboard calculation
# ------------------------
def calculate_leaderboard():
    predictions = pred_sheet.get_all_records()
    
    # Load actual results fresh every time
    actual_results_raw = results_sheet.get_all_records()
    actual_results = {}
    for row in actual_results_raw:
        match = row['Match']
        actual_results[match] = (int(row['Score1']), int(row['Score2']))

    scores = {}
    for pred in predictions:
        user = pred["Username"]
        match = pred["Match"]
        s1 = int(pred["Score1"])
        s2 = int(pred["Score2"])
        actual = actual_results.get(match)
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

    leaderboard_sheet.clear()
    leaderboard_sheet.append_row(["Username","Points","Correct Score","Correct Result"])
    leaderboard_sheet.append_rows([[u, d["Points"], d["Correct Score"], d["Correct Result"]] for u,d in scores.items()])

# ------------------------
# Run app
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
