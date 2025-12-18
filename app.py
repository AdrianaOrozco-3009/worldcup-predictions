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
# FIFA World Cup 2026 Matches (example: Group A-D, extend as needed)
# ------------------------
matches = [
    {"match": "A1 Mexico vs South Africa", "team1": "Mexico", "team2": "South Africa"},
    {"match": "A2 South Korea vs Playoff D", "team1": "South Korea", "team2": "Playoff D"},
    {"match": "A3 Mexico vs South Korea", "team1": "Mexico", "team2": "South Korea"},
    {"match": "A4 South Africa vs Playoff D", "team1": "South Africa", "team2": "Playoff D"},
    {"match": "A5 Mexico vs Playoff D", "team1": "Mexico", "team2": "Playoff D"},
    {"match": "A6 South Africa vs South Korea", "team1": "South Africa", "team2": "South Korea"},
    # Add all other groups similarly...
]

# ------------------------
# Load actual results from Google Sheets
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

# Cache results globally
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
        for m in matches:
            score1 = request.form.get(f"{m['match']}_score1")
            score2 = request.form.get(f"{m['match']}_score2")
            pred_sheet.append_row([str(datetime.now()), username, m["match"], m["team1"], m["team2"], score1, score2])
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