from plumbum import cli
from pyfiglet import Figlet
from questionary import select, text
from win32com.client import GetObject
import requests
import time
import io
import os
import sys

# all the URLs to access the data
player_info_url = "https://www.balldontlie.io/api/v1/players"
player_season_average_url = "https://www.balldontlie.io/api/v1/season_averages"
game_day_stats_url = "https://www.balldontlie.io/api/v1/stats"
game_day_score_url = "https://www.balldontlie.io/api/v1/games" 

def print_welcome(text: str):
    print(Figlet(font='bulbhead').renderText(text))

def generate_choices():
    return select(
        "What NBA info would you like to see?",
        choices=[
            "Player attributes (height, weight, etc.)",
            "Season Averages of a player",
            "Game stats on a specific day"
        ]).ask()

def generate_question_from_choice(choice: str):
    if choice == "Player attributes (height, weight, etc.)":
        nba_player = text("Whose player attributes are you looking for? Enter their first and last name (like LeBron James).").ask()
        print_player_attributes(nba_player)
    elif choice == "Season Averages of a player":
        player = text("Which player's season averages are you looking for? Enter their first and last name (like LeBron James).").ask()
        season = text("Which season do you want to check the season average of this player?").ask()
        print_player_season_average(player, season)
    else:
        date = text("Which game day are you looking for? Type the date as 'YYYY-MM-DD' format.").ask()
        choice_on_date = select("Which stats are you looking for?", 
        choices=["A player's stats on that day",
        "Team scores"
        ]).ask()
        get_stats_on_date(date, choice_on_date)

def print_player_attributes(player: str):
    first_name = player.split()[0].strip()
    last_name = player.split()[1].strip()
    player_info_json = get_player_json(last_name)
    for person in player_info_json['data']:
        if person['first_name'] == first_name and person['last_name'] == last_name:
            print_formatted_attributes(person) 

def print_player_season_average(player, season: str):
    player_id = get_player_id(player)
    player_season_averages_response = requests.get(player_season_average_url + "?season=" + str(season) + "&player_ids[]=" + str(player_id))
    player_season_average_json = player_season_averages_response.json()
    for season_averages in player_season_average_json['data']:
        games_played = season_averages['games_played']
        avg_minutes = season_averages['min']
        avg_rebounds = season_averages['reb']
        avg_assists = season_averages['ast']
        avg_steals = season_averages['stl']
        avg_blocks = season_averages['blk']
        avg_turnovers = season_averages['turnover']
        avg_points = season_averages['pts']
    print("In the " + season + " season, " + player + "'s season averages were:\n" + "Games played: " + str(games_played) + "\nMinutes: " + avg_minutes + 
    "\nRebounds: " + str(avg_rebounds) + "\nAssists: " + str(avg_assists) + "\nSteals: " + str(avg_steals) + "\nBlocks: " + str(avg_blocks) + 
    "\nTurnovers: " + str(avg_turnovers) + "\nPoints: " + str(avg_points))    

def get_stats_on_date(selected_date, selected_topic: str):
    if selected_topic == "A player's stats on that day":
        selected_player = text("Which player are you looking to get stats for on that date? Enter their first and last name (like LeBron James).").ask()
        first_name = selected_player.split()[0].strip()
        last_name = selected_player.split()[1].strip()
        player_id = get_player_id(selected_player)
        game_day_player_stats_response = requests.get(game_day_stats_url + "?dates[]=" + selected_date + "&player_ids[]=" + str(player_id))
        game_day_player_stats_json = game_day_player_stats_response.json()
        print("Fetching " + first_name + " " + last_name + "\'s stats on " + selected_date + "...")
        time.sleep(2)
        for stats in game_day_player_stats_json['data']:
            assists = stats['ast']
            blocks = stats['blk']
            minutes = stats['min']
            points = stats['pts']
            rebounds = stats['reb']
            steals = stats['stl']
        print("Okay, here's what I found:\n" + "Minutes: " + minutes + "\nPoints: " + str(points) + "\nAssists: " + 
            str(assists) + "\nBlocks: " + str(blocks) + "\nRebounds: " + str(rebounds) + "\nSteals: " + str(steals))    
    elif selected_topic == "Team scores":
        selected_team = text("Which team are you looking to get the stats of? Enter the team's full name (such as Golden State Warriors).").ask()
        curr_page = 1
        # I used a for loop here to search through the pages of the games on that date, 
        # but this for loop could be more useful for searching for a specific player or team in a longer list
        game_day_page_response = requests.get(game_day_score_url + "?dates[]=" + selected_date)
        game_day_page_json = game_day_page_response.json()
        total_pages = game_day_page_json['meta']['total_pages']
        while curr_page <= total_pages:
            game_day_score_response = requests.get(game_day_score_url + "?dates[]=" + selected_date + "&page=" + str(curr_page))
            game_day_score_json = game_day_score_response.json()
            for team in game_day_score_json['data']:
                if team['home_team']['full_name'] == selected_team or team['visitor_team']['full_name'] == selected_team:
                    print("Fetching the score from that game...")
                    time.sleep(2)
                    print("In the " + str(team['season']) + " season, the home team, the " + 
                    team['home_team']['full_name'] + ", scored " + str(team['home_team_score']) + 
                    " and the visiting team, the " + team['visitor_team']['full_name'] + ", scored " + str(team['visitor_team_score']) + ".")
                    break                  
                else:
                    curr_page += 1

# Helper methods                    
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

def get_player_json(last_name: str):
    player_info_response = requests.get(player_info_url + "?search=" + last_name + "&per_page=100")
    return player_info_response.json()

def get_player_id(name: str):
    first_name = name.split()[0].strip()
    last_name = name.split()[1].strip()
    player_info_json = get_player_json(last_name)
    for person in player_info_json['data']:
        if person['first_name'] == first_name and person['last_name'] == last_name:
            return person['id']   

class GetNBAInformation(cli.Application):
    VERSION = "1.0"
    leave = cli.Flag(['e', 'exit'], help="Exits command prompt")
    def main(self):
        if self.leave:
            # kills command prompt through windows management instrumentation
            WMI = GetObject('winmgmts:')
            processes = WMI.InstancesOf('Win32_Process')

            for p in WMI.ExecQuery('select * from Win32_Process where Name="cmd.exe"'):
                print("Killing PID:", p.Properties_('ProcessId').Value)
                os.system("taskkill /pid "+str(p.Properties_('ProcessId').Value))
        print_welcome("Welcome to NBA stat finder!")
        choice = generate_choices()
        generate_question_from_choice(choice)
        
if __name__ == "__main__":
    GetNBAInformation()

### TESTS 

def test_print_player_attributes():
    # capture output and restore output stream to what it was before the capture
    captured_output = io.StringIO()
    sys.stdout = captured_output
    print_player_attributes("LeBron James")
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue() == 'Name: James, LeBron\nPosition: F\nHeight: 6\'8\"\nTeam: Los Angeles Lakers (LAL)\nConference: West\nDivision: Pacific\n'

def test_print_player_season_average():
    captured_output = io.StringIO()
    sys.stdout = captured_output
    print_player_season_average("Stephen Curry", "2016")
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue() == 'In the 2016 season, Stephen Curry\'s season averages were:\nGames played: 79\nMinutes: 33:23\nRebounds: 4.47\nAssists: 6.63\nSteals: 1.8\nBlocks: 0.22\nTurnovers: 3.03\nPoints: 25.3\n'

def test_get_player_id():
    player_id = get_player_id("Klay Thompson")
    assert player_id == 443