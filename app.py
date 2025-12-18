from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os, json

# ------------------------
# Google Sheets setup
# ------------------------
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]

# Credentials: use env variable on Render, fallback to local file
if 'GOOGLE_CREDS_JSON' in os.environ:
    creds_dict = json.loads(os.environ['GOOGLE_CREDS_JSON'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)

client = gspread.authorize(creds)

# Sheet ID from env variable or fallback to local
SHEET_ID = os.environ.get("SHEET_ID", "1yCf3io3Hywr5dnmu6a_kr2dktAvqoG7CU2CbAiEDbVY")

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
    {"match": "E1 Spain vs Playoff B", "team1": "Spain", "team2": "Playoff B"},
    {"match": "E2 Germany vs Costa Rica", "team1": "Germany", "team2": "Costa Rica"},
    {"match": "E3 Spain vs Germany", "team1": "Spain", "team2": "Germany"},
    {"match": "E4 Playoff B vs Costa Rica", "team1": "Playoff B", "team2": "Costa Rica"},
    {"match": "E5 Spain vs Costa Rica", "team1": "Spain", "team2": "Costa Rica"},
    {"match": "E6 Playoff B vs Germany", "team1": "Playoff B", "team2": "Germany"},

    # Group F
    {"match": "F1 Argentina vs Playoff E", "team1": "Argentina", "team2": "Playoff E"},
    {"match": "F2 France vs Morocco", "team1": "France", "team2": "Morocco"},
    {"match": "F3 Argentina vs France", "team1": "Argentina", "team2": "France"},
    {"match": "F4 Playoff E vs Morocco", "team1": "Playoff E", "team2": "Morocco"},
    {"match": "F5 Argentina vs Morocco", "team1": "Argentina", "team2": "Morocco"},
    {"match": "F6 Playoff E vs France", "team1": "Playoff E", "team2": "France"},

    # Group G
    {"match": "G1 England vs Playoff F", "team1": "England", "team2": "Playoff F"},
    {"match": "G2 Portugal vs Nigeria", "team1": "Portugal", "team2": "Nigeria"},
    {"match": "G3 England vs Portugal", "team1": "England", "team2": "Portugal"},
    {"match": "G4 Playoff F vs Nigeria", "team1": "Playoff F", "team2": "Nigeria"},
    {"match": "G5 England vs Nigeria", "team1": "England", "team2": "Nigeria"},
    {"match": "G6 Playoff F vs Portugal", "team1": "Playoff F", "team2": "Portugal"},

    # Group H
    {"match": "H1 Italy vs Playoff G", "team1": "Italy", "team2": "Playoff G"},
    {"match": "H2 Belgium vs Japan", "team1": "Belgium", "team2": "Japan"},
    {"match": "H3 Italy vs Belgium", "team1": "Italy", "team2": "Belgium"},
    {"match": "H4 Playoff G vs Japan", "team1": "Playoff G", "team2": "Japan"},
    {"match": "H5 Italy vs Japan", "team1": "Italy", "team2": "Japan"},
    {"match": "H6 Playoff G vs Belgium", "team1": "Playoff G", "team2": "Belgium"},

    # Group I
    {"match": "I1 Netherlands vs Playoff H", "team1": "Netherlands", "team2": "Playoff H"},
    {"match": "I2 Senegal vs Ecuador", "team1": "Senegal", "team2": "Ecuador"},
    {"match": "I3 Netherlands vs Senegal", "team1": "Netherlands", "team2": "Senegal"},
    {"match": "I4 Playoff H vs Ecuador", "team1": "Playoff H", "team2": "Ecuador"},
    {"match": "I5 Netherlands vs Ecuador", "team1": "Netherlands", "team2": "Ecuador"},
    {"match": "I6 Playoff H vs Senegal", "team1": "Playoff H", "team2": "Senegal"},

    # Group J
    {"match": "J1 Croatia vs Playoff I", "team1": "Croatia", "team2": "Playoff I"},
    {"match": "J2 Denmark vs Cameroon", "team1": "Denmark", "team2": "Cameroon"},
    {"match": "J3 Croatia vs Denmark", "team1": "Croatia", "team2": "Denmark"},
    {"match": "J4 Playoff I vs Cameroon", "team1": "Playoff I", "team2": "Cameroon"},
    {"match": "J5 Croatia vs Cameroon", "team1": "Croatia", "team2": "Cameroon"},
    {"match": "J6 Playoff I vs Denmark", "team1": "Playoff I", "team2": "Denmark"},

    # Group K
    {"match": "K1 Uruguay vs Playoff J", "team1": "Uruguay", "team2": "Playoff J"},
    {"match": "K2 Poland vs Iran", "team1": "Poland", "team2": "Iran"},
    {"match": "K3 Uruguay vs Poland", "team1": "Uruguay", "team2": "Poland"},
    {"match": "K4 Playoff J vs Iran", "team1": "Playoff J", "team2": "Iran"},
    {"match": "K5 Uruguay vs Iran", "team1": "Uruguay", "team2": "Iran"},
    {"match": "K6 Playoff J vs Poland", "team1": "Playoff J", "team2": "Poland"},

    # Group L
    {"match": "L1 South Korea vs Playoff K", "team1": "South Korea", "team2": "Playoff K"},
    {"match": "L2 Cameroon vs Saudi Arabia", "team1": "Cameroon", "team2": "Saudi Arabia"},
    {"match": "L3 South Korea vs Cameroon", "team1": "South Korea", "team2": "Cameroon"},
    {"match": "L4 Playoff K vs Saudi Arabia", "team1": "Playoff K", "team2": "Saudi Arabia"},
    {"match": "L5 South Korea vs Saudi Arabia", "team1": "South Korea", "team2": "Saudi Arabia"},
    {"match": "L6 Playoff K vs Cameroon", "team1": "Playoff K", "team2": "Cameroon"},
]
# ------------------------
# Load actual results from Google Sheet
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

# Cache actual results
actual_results_cache = load_results()

# Optional route to reload results manually
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
