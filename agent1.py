import re

class UserProfileAgent:
    def __init__(self):
        self.profile = {
            "age": None,
            "gender": None,
            "weight": None,
            "height": None,
            "activity_level": None,
            "goal": None
        }

    def extract_from_text(self, text):
        text = text.lower()

        def find(pattern):
            match = re.search(pattern, text)
            return float(match.group(1)) if match else None

        age = find(r'(\d+)\s*(year|years|yo)')
        weight = find(r'(\d+)\s*(kg)')
        height = find(r'(\d+)\s*(cm)')

        if age:
            self.profile["age"] = int(age)
        if weight:
            self.profile["weight"] = float(weight)
        if height:
            self.profile["height"] = float(height)

        if "male" in text or "man" in text:
            self.profile["gender"] = "male"
        elif "female" in text or "woman" in text:
            self.profile["gender"] = "female"

        if any(w in text for w in ["lose", "fat", "cut"]):
            self.profile["goal"] = "lose_weight"
        elif any(w in text for w in ["gain", "muscle", "bulk"]):
            self.profile["goal"] = "muscle_gain"
        elif "maintain" in text:
            self.profile["goal"] = "maintain"

    def safe_input(self, prompt, cast=str):
        while True:
            val = input(prompt)
            try:
                return cast(val)
            except:
                print("Invalid input, try again.")

    def ask_missing(self):
        if self.profile["age"] is None:
            self.profile["age"] = self.safe_input("Enter age: ", int)
        if self.profile["gender"] is None:
            self.profile["gender"] = self.safe_input("Gender (male/female): ")
        if self.profile["weight"] is None:
            self.profile["weight"] = self.safe_input("Weight (kg): ", float)
        if self.profile["height"] is None:
            self.profile["height"] = self.safe_input("Height (cm): ", float)
        if self.profile["activity_level"] is None:
            print("Activity levels: low / moderate / high")
            self.profile["activity_level"] = self.safe_input("Activity level: ")
        if self.profile["goal"] is None:
            print("Goals: lose_weight / muscle_gain / maintain")
            self.profile["goal"] = self.safe_input("Goal: ")

    def validate(self):
        if not (10 <= self.profile["age"] <= 100):
            raise ValueError("Invalid age")
        if not (30 <= self.profile["weight"] <= 300):
            raise ValueError("Invalid weight")
        if not (100 <= self.profile["height"] <= 250):
            raise ValueError("Invalid height")

    def run(self):
        print("Describe yourself (optional):")
        text = input("> ")
        if text.strip():
            self.extract_from_text(text)
        self.ask_missing()
        self.validate()
        return self.profile


def agent2_stub(profile):
    print("\nAgent 2 received profile:")
    print(profile)


if __name__ == "__main__":
    agent1 = UserProfileAgent()
    profile = agent1.run()
    agent2_stub(profile)
