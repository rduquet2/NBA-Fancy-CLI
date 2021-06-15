from plumbum import cli
from pyfiglet import Figlet
from plumbum.cmd import git
from questionary import select, text, prompt
import requests
import json

player_info_url = "https://www.balldontlie.io/api/v1/players"

player_season_stats_response = requests.get("https://www.balldontlie.io/api/v1/season_averages")
team_info_response = requests.get("https://www.balldontlie.io/api/v1/teams")

def print_welcome(text: str):
    print(Figlet(font='bulbhead').renderText(text))

def generate_choices():
    return select(
        "What NBA info would you like to see?",
        choices=[
            "Player attributes (height, weight, etc.)",
            "Player stats",
            "Game stats on a specific day"
        ]).ask()

def generate_question_from_choice(choice: str):
    print(choice)
    if choice == "Player attributes (height, weight, etc.)":
        nba_player = text("Whose player attributes are you looking for? Enter their first and last name (like LeBron James).").ask()
        print_player_attributes(nba_player)
    elif choice == "Player stats":
        answer = text("Whose player stats are you looking for? Enter their first and last name (like LeBron James).").ask()
    else:
        date = text("Which game day are you looking for? Type the date as 'YYYY-MM-DD' format.").ask()

def print_player_attributes(player: str):
    first_name = player.split()[0].strip()
    last_name = player.split()[1].strip()
    player_info_response = requests.get(player_info_url + "?search=" + last_name + "&per_page=1000")
    player_info_json = player_info_response.json()
    for person in player_info_json['data']:
        if person['first_name'] == first_name and person['last_name'] == last_name:
            print_formatted_attributes(person) 

#def print_player_stats(player: str):  

#def print_team_infor(team: str):

def print_formatted_attributes(obj):
    # create a formatted string of the Python JSON object displaying the players characteristics
    name = obj['last_name'] + ", " + obj['first_name']
    if obj['position'] is not None:
        position = obj['position']
    else:
        position = "Not found"    
    if obj['height_feet'] is not None and obj['height_inches'] is not None:
        height = str(obj['height_feet']) + "\'" + str(obj['height_inches']) + "\""
    else:
        height = "Not found"    
    team = obj['team']['full_name'] + " (" + obj['team']['abbreviation'] + ")"
    conference = obj['team']['conference']
    division = obj['team']['division']
    print("Name: " + name + "\nPosition: " + position + "\nHeight: " + height + "\nTeam: " + team + "\nConference: " + conference + "\nDivision: " + division)

class GetNBAInformation(cli.Application):
    VERSION = "1.0"
    def main(self):
        print_welcome("Welcome to NBA stat finder!")
        choice = generate_choices()
        generate_question_from_choice(choice)
        

if __name__ == "__main__":
    GetNBAInformation()

### TESTS    