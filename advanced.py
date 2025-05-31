import http.client
import json
import base
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def get_link(url):
    return request.host_url + url


def post_registration(url='/login', auth_token='6d46da5cb63eb7486ecec390ee122f15baad4ac0e210ea6a20340c86dbe355fc'):
    connection = http.client.HTTPSConnection("lksh-enter.ru")
    reason = ("Имею базовые навыки промышленного программирования – принципы ООП (наследование и т.д.), работа"
              " с Django, REST framework, Flask. Желаю научиться новому и в дальнейшем использовать это при "
              "разработке проектов и т.п..")
    print(reason)
    connection.request("POST", url, body=('{' + f'"reason": "{reason}"' + '}').encode('utf-8'),
                       headers={'Authorization': auth_token})
    return connection.getresponse().read().decode('utf-8')


@app.route('/stats', methods=['GET'])
def stats():
    team_name = request.args.get('team_name')
    if base.is_existing_params(team_name):
        statisitics = base.stats(team_name)
        return (f"{statisitics[0]} {statisitics[1]} "
                f"{('+' + str(statisitics[2])) if statisitics[2] > 0 else statisitics[2]}")
    else:
        return "Неверный запрос!"


@app.route('/versus', methods=['GET'])
def versus():
    player1_id = base.to_int_param(request.args.get('player1_id'))
    player2_id = base.to_int_param(request.args.get('player2_id'))
    if type(player1_id) is int and type(player2_id) is int:
        return str(base.versus(player1_id, player2_id))
    return "Неверный запрос!"


@app.route('/goals', methods=['GET'])
def goals(args=["global"]):
    if "global" in args:
        player_id = base.to_int_param(request.args.get('player_id'))
    else:
        player_id = args[1]
    if type(player_id) is int:
        team_id = base.get_team_id(player_id)
        matches_id = []
        players_goals = []
        if team_id == -1:
            return "Игрока не существует"
        for match in base.matches():
            if match['team1'] == int(team_id) or match['team2'] == int(team_id):
                matches_id.append(match['id'])
        for match_id in matches_id:
            current_goals = base.goals(match_id)
            for goal in current_goals:
                if goal['player'] == player_id:
                    players_goals.append({"match": goal["match"], "time": goal["minute"]})
        if 'local' in args:
            return players_goals
        return jsonify(players_goals)
    return "Неверный запрос!"


@app.route('/front/stats', methods=['GET'])
def front_stats():
    team_name = request.args.get('team_name')
    if base.is_existing_params(team_name):
        back_stats = base.stats(team_name)
        return render_template("stats.html", victories=back_stats[0],
                               defeats=back_stats[1], difference=back_stats[2], club=team_name)
    return "Неверный запрос!"


@app.route('/front/matches', methods=['GET'])
def front_matches():
    team_id = base.to_int_param(request.args.get('team_id'))
    if type(team_id) is int:
        data = []
        club = base.team(team_id)
        for match in base.matches():
            if match["team1"] == team_id:
                rival = base.team(match["team2"])
                data.append([match["id"], rival["name"], match["team1_score"], match["team2_score"],
                             base.is_win(match["team1_score"], match["team2_score"])])
            elif match["team2"] == team_id:
                rival = base.team(match["team1"])
                data.append([match["id"], rival["name"], match["team2_score"], match["team1_score"],
                             base.is_win(match["team2_score"], match["team1_score"])])
        return render_template("matches.html", club=club["name"], data=data)
    return "Неверный запрос!"


@app.route('/front/versus', methods=['GET'])
def front_versus():
    player1_id = base.to_int_param(request.args.get('player1_id'))
    player2_id = base.to_int_param(request.args.get('player2_id'))
    if (type(player1_id) is int) and (type(player2_id) is int):
        # data = [{"title": "Клуб", "columns": ["Manchester", "Barcelona"]}, ...]
        data = []
        player1 = base.player(player1_id)
        player2 = base.player(player2_id)
        club1 = base.team(base.get_team_id(player1_id))
        club2 = base.team(base.get_team_id(player2_id))
        data.append({"title": "ID Клуба", "columns": [club1["id"], club2["id"]]})
        data.append({"title": "Клуб", "columns": [[get_link(f'front/stats?team_name={club1["name"]}'), club1["name"]],
                                                  [get_link(f'front/stats?team_name={club2["name"]}'), club2["name"]]]})
        data.append({"title": "Матчи Клуба", "columns": [get_link(f'front/matches?team_id={club1["id"]}'),
                                                         get_link(f'front/matches?team_id={club2["id"]}')]})
        data.append({"title": "ID Игрока", "columns": [player1_id, player2_id]})
        data.append({"title": "Фамилия", "columns": [player1["surname"], player2["surname"]]})
        data.append({"title": "Имя", "columns": [player1["name"], player2["name"]]})
        data.append({"title": "Номер", "columns": [player1["number"], player2["number"]]})
        data.append({"title": "Голы", "columns": [get_link(f"front/goals?player_id={player1_id}"),
                                                  get_link(f"front/goals?player_id={player2_id}")]})
        full_information = request.args.get("full_information")
        if base.is_existing_params(full_information) and full_information.lower() == "true":
            data.append({"title": "Забитые", "columns": [len(goals(["local", player1_id])),
                                                         len(goals(["local", player2_id]))]})
        return render_template("versus.html", player1_id=player1_id, player2_id=player2_id, data=data,
                               versuses=base.versus(player1_id, player2_id), full=full_information)
    return "Неверный запрос!"


@app.route('/front/goals', methods=['GET'])
def front_goals():
    player_id = base.to_int_param(request.args.get('player_id'))
    if type(player_id) is int:
        all_goals = goals(["local", player_id])
        club = base.get_team_id(player_id)
        data = []
        rivals = {}
        for idx, goal in enumerate(all_goals):
            data.append([idx + 1, goal["match"], None, goal["time"]])
            rivals[goal["match"]] = None
        for match in base.matches():
            if match["id"] in rivals:
                rival = list({match["team1"], match["team2"]} - {club})[0]
                rivals[match["id"]] = base.team(rival)["name"]
        for i in range(len(data)):
            data[i][2] = rivals[data[i][1]]
        return render_template("goals.html",
                               player=base.player(player_id)["name"] + ' ' + base.player(player_id)["surname"],
                               data=data)
    return "Неверный запрос!"


if __name__ == '__main__':
    app.run(debug=False)
