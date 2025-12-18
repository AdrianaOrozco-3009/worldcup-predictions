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

SHEET_ID = "1yCf3io3Hywr5dnmu6a_kr2dktAvqoG7CU2CbAiEDbVY"  # Replace with your Google Sheet ID
pred_sheet = client.open_by_key(SHEET_ID).worksheet("Predictions")
leaderboard_sheet = client.open_by_key(SHEET_ID).worksheet("Leaderboard")
results_sheet = client.open_by_key(SHEET_ID).worksheet("Results")  # actual match results

# ------------------------
# Flask app
# ------------------------
app = Flask(__name__)

# ------------------------
# FIFA World Cup 2026 Group-Stage Matches
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
    {"match": "E1 Spain vs Playoff H", "team1": "Spain", "team2": "Playoff H"},
    {"match": "E2 Germany vs Japan", "team1": "Germany", "team2": "Japan"},
    {"match": "E3 Spain vs Germany", "team1": "Spain", "team2": "Germany"},
    {"match": "E4 Playoff H vs Japan", "team1": "Playoff H", "team2": "Japan"},
    {"match": "E5 Spain vs Japan", "team1": "Spain", "team2": "Japan"},
    {"match": "E6 Playoff H vs Germany", "team1": "Playoff H", "team2": "Germany"},

    # Group F
    {"match": "F1 Argentina vs Poland", "team1": "Argentina", "team2": "Poland"},
    {"match": "F2 France vs Playoff G", "team1": "France", "team2": "Playoff G"},
    {"match": "F3 Argentina vs France", "team1": "Argentina", "team2": "France"},
    {"match": "F4 Poland vs Playoff G", "team1": "Poland", "team2": "Playoff G"},
    {"match": "F5 Argentina vs Playoff G", "team1": "Argentina", "team2": "Playoff G"},
    {"match": "F6 Poland vs France", "team1": "Poland", "team2": "France"},

    # Group G
    {"match": "G1 England vs Playoff K", "team1": "England", "team2": "Playoff K"},
    {"match": "G2 Senegal vs Croatia", "team1": "Senegal", "team2": "Croatia"},
    {"match": "G3 England vs Senegal", "team1": "England", "team2": "Senegal"},
    {"match": "G4 Playoff K vs Croatia", "team1": "Playoff K", "team2": "Croatia"},
    {"match": "G5 England vs Croatia", "team1": "England", "team2": "Croatia"},
    {"match": "G6 Playoff K vs Senegal", "team1": "Playoff K", "team2": "Senegal"},

    # Group H
    {"match": "H1 Portugal vs Playoff I", "team1": "Portugal", "team2": "Playoff I"},
    {"match": "H2 Italy vs Uruguay", "team1": "Italy", "team2": "Uruguay"},
    {"match": "H3 Portugal vs Italy", "team1": "Portugal", "team2": "Italy"},
    {"match": "H4 Playoff I vs Uruguay", "team1": "Playoff I", "team2": "Uruguay"},
    {"match": "H5 Portugal vs Uruguay", "team1": "Portugal", "team2": "Uruguay"},
    {"match": "H6 Playoff I vs Italy", "team1": "Playoff I", "team2": "Italy"},

    # Group I
    {"match": "I1 Belgium vs Playoff J", "team1": "Belgium", "team2": "Playoff J"},
    {"match": "I2 Netherlands vs Ecuador", "team1": "Netherlands", "team2": "Ecuador"},
    {"match": "I3 Belgium vs Netherlands", "team1": "Belgium", "team2": "Netherlands"},
    {"match": "I4 Playoff J vs Ecuador", "team1": "Playoff J", "team2": "Ecuador"},
    {"match": "I5 Belgium vs Ecuador", "team1": "Belgium", "team2": "Ecuador"},
    {"match": "I6 Playoff J vs Netherlands", "team1": "Playoff J", "team2": "Netherlands"},

    # Group J
    {"match": "J1 Morocco vs Playoff L", "team1": "Morocco", "team2": "Playoff L"},
    {"match": "J2 USA vs Switzerland", "team1": "USA", "team2": "Switzerland"},
    {"match": "J3 Morocco vs USA", "team1": "Morocco", "team2": "USA"},
    {"match": "J4 Playoff L vs Switzerland", "team1": "Playoff L", "team2": "Switzerland"},
    {"match": "J5 Morocco vs Switzerland", "team1": "Morocco", "team2": "Switzerland"},
    {"match": "J6 Playoff L vs USA", "team1": "Playoff L", "team2": "USA"},

    # Group K
    {"match": "K1 Cameroon vs South Korea", "team1": "Cameroon", "team2": "South Korea"},
    {"match": "K2 Japan vs Croatia", "team1": "Japan", "team2": "Croatia"},
    {"match": "K3 Cameroon vs Japan", "team1": "Cameroon", "team2": "Japan"},
    {"match": "K4 South Korea vs Croatia", "team1": "South Korea", "team2": "Croatia"},
    {"match": "K5 Cameroon vs Croatia", "team1": "Cameroon", "team2": "Croatia"},
    {"match": "K6 South Korea vs Japan", "team1": "South Korea", "team2": "Japan"},

    # Group L
    {"match": "L1 Ghana vs Playoff M", "team1": "Ghana", "team2": "Playoff M"},
    {"match": "L2 Poland vs Mexico", "team1": "Poland", "team2": "Mexico"},
    {"match": "L3 Ghana vs Poland", "team1": "Ghana", "team2": "Poland"},
    {"match": "L4 Playoff M vs Mexico", "team1": "Playoff M", "team2": "Mexico"},
    {"match": "L5 Ghana vs Mexico", "team1": "Ghana", "team2": "Mexico"},
    {"match": "L6 Playoff M vs Poland", "team1": "Playoff M", "team2": "Poland"},
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

# Optional route to reload results manually
@app.route("/reload_results")
def reload_results():
    global actual_results_cache
    actual_results_cache = load_results()
    return "Results reloaded successfully!"

# ------------------------
# Index route
# ------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    print("🚀 Serving index page")
    if request.method == "POST":
        username = request.form["username"]
        rows_to_append = []

        # Collect all rows for this user
        for m in matches:
            try:
                score1 = int(request.form.get(f"{m['match']}_score1") or 0)
                score2 = int(request.form.get(f"{m['match']}_score2") or 0)
            except ValueError:
                score1 = 0
                score2 = 0

            rows_to_append.append([
                str(datetime.now()), username, m["match"], m["team1"], m["team2"], score1, score2
            ])

        # Single write to Google Sheets
        try:
            pred_sheet.append_rows(rows_to_append)
        except Exception as e:
            print("Error writing to Google Sheet:", e)

        # Reload results and calculate leaderboard
        global actual_results_cache
        actual_results_cache = load_results()
        calculate_leaderboard()

        return redirect("/leaderboard")

    return render_template("index.html", matches=matches)

# ------------------------
# Leaderboard route
# ------------------------
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

    leaderboard_sheet.clear()
    leaderboard_sheet.append_row(["Username","Points","Correct Score","Correct Result"])
    for user, data in scores.items():
        leaderboard_sheet.append_row([user, data["Points"], data["Correct Score"], data["Correct Result"]])

# ------------------------
# Run app
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
