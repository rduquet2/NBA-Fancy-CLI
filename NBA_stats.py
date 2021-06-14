from plumbum import cli
from pyfiglet import Figlet
from plumbum.cmd import git
from questionary import select, text
import requests
import json

player_info_response = requests.get("https://www.balldontlie.io/api/v1/players")
player_season_stats_response = requests.get("https://www.balldontlie.io/api/v1/season_averages")
team_info_response = requests.get("https://www.balldontlie.io/api/v1/teams")

def print_welcome(text: str):
    print(Figlet(font='bulbhead').renderText(text))

def generate_choices():
    select(
        "What NBA info would you like to see?",
        choices=[
            "Player attributes (height, weight, etc.)",
            "Player stats",
            "Team information"
        ]).ask()

def generate_question_from_choice(choice: str):
    if choice == "Player attributes":
        answer = text("Whose player attributes are you looking for? Enter their first and last name (like Lebron James).").ask()
    elif choice == "Player stats":
        answer = text("Whose player stats are you looking for? Enter their first and last name (like Lebron James).").ask()
    else:
        answer = text("Which team are you looking for? Enter the team's full name.").ask()

def print_player_attributes(player: str):


def print_formatted_json(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=False, indent=4)
    print(text)


class GetNBAInformation(cli.Application):
    VERSION = "1.0"
    def main(self):
        print_welcome("Welcome to NBA stat finder!")
        choice = generate_choices()
        generate_question_from_choice(choice)
        

if __name__ == "__main__":
    GetNBAInformation()

### TESTS    