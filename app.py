# required imports
import json
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# loads your habits
def load_habits():
    with open("habits.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

# saves habits
def save_habits(habits):
    with open("habits.json", "w", encoding="utf-8") as file:
        json.dump(habits, file, indent=2)

# creates a new habit
def create_habit(name):
    habits = load_habits()

    if name.strip() == "":
        print("Habit name not defined.")
        return

    next_id = max([habit["id"] for habit in habits], default=0) + 1
    today = date.today().isoformat()

    new_habit = {
        "id": next_id,
        "name": name.strip(),
        "created": today,
        "completions": []
    }

    habits.append(new_habit)
    save_habits(habits)

    return new_habit

# renames a habit
def rename_habit(habit_id, new_name):
    habits = load_habits()

    if new_name.strip() == "":
        print("Habit name not defined.")
        return None

    for habit in habits:
        if habit["id"] == habit_id:
            habit["name"] = new_name.strip()
            save_habits(habits)
            return habit

    return None
# deletes a habit
def delete_habit(habit_id):
    habits = load_habits()

    for habit in habits:
        if habit_id == habit["id"]:
            habits.remove(habit)
            save_habits(habits)
            return True
    
    return False

# logs today's completion of a habit
def complete_habit(habit_id):
    habits = load_habits()

    today = date.today().isoformat()

    for habit in habits:
        if habit["id"] == habit_id:
            if today not in habit["completions"]:
                habit["completions"].append(today)
                save_habits(habits)
            
            return habit
    
    return None

# undoes completion of a habit if a mistake is made
def undo_completion(habit_id):
    habits = load_habits()

    today = date.today().isoformat()

    for habit in habits:
        if habit["id"] == habit_id:
            if today in habit["completions"]:
                habit["completions"].remove(today)
                save_habits(habits)
            
            return habit
    
    return None

# calculates your streak for a habit
def calculate_streak(habit):
    today = date.today()

    if today.isoformat() in habit["completions"]:
        current_day = today
    else:
        current_day = today - timedelta(days=1)

    streak = 0

    while current_day.isoformat() in habit["completions"]:
        streak += 1
        current_day -= timedelta(days=1)

    return streak


# connects app.py to index.html
class HabitHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # Serve the main webpage
        if self.path == "/":
            with open("index.html", "rb") as file:
                page = file.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(page)

        # Return habit data
        elif self.path == "/habits":
            habits = load_habits()
            today = date.today().isoformat()

            for habit in habits:
                habit["streak"] = calculate_streak(habit)
                habit["completed_today"] = today in habit["completions"]

            response = json.dumps(habits).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(response)

        # Anything else doesn't exist
        else:
            self.send_response(404)
            self.end_headers()
    
    def read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def send_json(self, data, status=200):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(response)
    
    def do_POST(self):

        # Create habit
        if self.path == "/habits":
            data = self.read_json_body()
            habit = create_habit(data.get("name", ""))

            if habit is None:
                self.send_json({"error": "Habit name cannot be empty"}, 400)
                return

            self.send_json(habit, 201)
            return

        # Complete habit
        parts = self.path.strip("/").split("/")

        if len(parts) == 3 and parts[0] == "habits" and parts[2] == "complete":
            try:
                habit_id = int(parts[1])
            except ValueError:
                self.send_json({"error": "Invalid habit ID"}, 400)
                return

            habit = complete_habit(habit_id)

            if habit is None:
                self.send_json({"error": "Habit not found"}, 404)
                return

            self.send_json(habit)
            return

        self.send_json({"error": "Not found"}, 404)
    
    def do_PUT(self):

        parts = self.path.strip("/").split("/")

        if len(parts) == 2 and parts[0] == "habits":
            try:
                habit_id = int(parts[1])
            except ValueError:
                self.send_json({"error": "Invalid habit ID"}, 400)
                return

            data = self.read_json_body()

            habit = rename_habit(
                habit_id,
                data.get("name", "")
            )

            if habit is None:
                self.send_json({"error": "Invalid habit or name"}, 400)
                return

            self.send_json(habit)
            return

        self.send_json({"error": "Not found"}, 404)
    
    def do_DELETE(self):

        parts = self.path.strip("/").split("/")

        # Undo today's completion
        if len(parts) == 3 and parts[0] == "habits" and parts[2] == "complete":
            try:
                habit_id = int(parts[1])
            except ValueError:
                self.send_json({"error": "Invalid habit ID"}, 400)
                return

            habit = undo_completion(habit_id)

            if habit is None:
                self.send_json({"error": "Habit not found"}, 404)
                return

            self.send_json(habit)
            return

        # Delete habit
        if len(parts) == 2 and parts[0] == "habits":
            try:
                habit_id = int(parts[1])
            except ValueError:
                self.send_json({"error": "Invalid habit ID"}, 400)
                return

            deleted = delete_habit(habit_id)

            if not deleted:
                self.send_json({"error": "Habit not found"}, 404)
                return

            self.send_json({"deleted": True})
            return

        self.send_json({"error": "Not found"}, 404)



# this has to stay at the very bottom
if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), HabitHandler)

    print("Habit Tracker running at http://localhost:8000")

    server.serve_forever()