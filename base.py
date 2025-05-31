import http.client
import json


def get(url, auth_token='6d46da5cb63eb7486ecec390ee122f15baad4ac0e210ea6a20340c86dbe355fc'):
    connection = http.client.HTTPSConnection("lksh-enter.ru")
    connection.request("GET", url, headers={'Authorization': auth_token})
    result = connection.getresponse()
    while result.reason.lower() == "too many requests":
        connection.request("GET", url, headers={'Authorization': auth_token})
        result = connection.getresponse()
    if result.reason == 'OK':
        return json.loads(result.read().decode('utf-8'))
    raise Exception(result.reason)


def matches():
    return get(f"/matches")


def all_teams():
    return get(f"/teams")


def team(team_id):
    return get(f"/teams/{team_id}")


def player(player_id):
    return get(f"/players/{player_id}")


def get_team_id(player_id):
    team_id = -1
    for current_team in all_teams():
        if player_id in current_team["players"]:
            team_id = current_team["id"]
    return team_id


def all_players():
    players_id = []
    for current_team in all_teams():
        players_id.extend(current_team["players"])
    players_id = list(set(players_id))
    players_of_all_teams = []
    for player_id in players_id:
        current_player = player(player_id)
        players_of_all_teams.append([current_player['name'], current_player['surname']])
        print(player_id)
    return sorted(players_of_all_teams, key=lambda x: x[0])


def stats(team_name):
    team_id = -1
    is_real_team = False
    for team in all_teams():
        current_team_id = team["id"]
        if team["name"] == team_name:
            team_id = current_team_id
            is_real_team = True
            break
    if not is_real_team:
        return 0, 0, 0
    victories, defeats, scored, missed = 0, 0, 0, 0
    for match in matches():
        if match["team1"] == team_id:
            scored += match["team1_score"]
            missed += match["team2_score"]
            victories += int(match["team1_score"] > match["team2_score"])
            defeats += int(match["team2_score"] > match["team1_score"])
        elif match["team2"] == team_id:
            scored += match["team2_score"]
            missed += match["team1_score"]
            victories += int(match["team2_score"] > match["team1_score"])
            defeats += int(match["team1_score"] > match["team2_score"])
    return victories, defeats, scored - missed


def is_win(score1, score2):
    score1 = int(score1)
    score2 = int(score2)
    if score1 > score2:
        return "Win"
    elif score1 == score2:
        return "Draw"
    return "Lose"


def versus(player1_id, player2_id):
    team1_id, team2_id = get_team_id(player1_id), get_team_id(player2_id)
    if team1_id == -1 or team2_id == -1:
        return 0
    versus_counter = 0
    for current_match in matches():
        if {team1_id, team2_id} == {current_match["team1"], current_match["team2"]}:
            versus_counter += 1
    return versus_counter


def goals(match_id):
    return get(f"/goals?match_id={match_id}")


def main():
    print('\n'.join([' '.join(current_player) for current_player in all_players()]))
    user_request = input()
    while user_request != '':
        comand, data = user_request.split('?')
        data = data[1:]
        if comand == "stats":
            answer = stats(data[1:-1])
            print(*answer[:-1], end=' ')
            if answer[-1] > 0:
                print('+', answer[-1], sep='')
            else:
                print(answer[-1])
        if comand == "versus":
            print(versus(*map(int, data.split())))
        user_request = input()


def is_existing_params(*params):
    for param in params:
        if not (param and param != ""):
            return False
    return True


def to_int_param(param):
    if is_existing_params(param) and param.isdigit():
        return int(param)
    return param


if __name__ == "__main__":
    main()