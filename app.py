from flask import Flask, render_template, jsonify, request
from markupsafe import escape
import threading
import time
from scraper import (
    scrape_fifa2026_data, get_match_schedule, get_world_ranking,
    get_top_scorers, get_upcoming_matches
)
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fifa2026-secret-key')

# Cached data
cached_data = {
    'standings': None,
    'schedule': None,
    'ranking': None,
    'scorers': None,
    'last_updated': None
}

# FIFA 2026 participating teams with flags
TEAM_FLAGS = {
    'Argentina': '🇦🇷', 'Brazil': '🇧🇷', 'France': '🇫🇷', 'Germany': '🇩🇪',
    'Spain': '🇪🇸', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Italy': '🇮🇹', 'Netherlands': '🇳🇱',
    'Portugal': '🇵🇹', 'Belgium': '🇧🇪', 'Croatia': '🇭🇷', 'Uruguay': '🇺🇾',
    'Colombia': '🇨🇴', 'USA': '🇺🇸', 'Mexico': '🇲🇽', 'Canada': '🇨🇦',
    'Costa Rica': '🇨🇷', 'Saudi Arabia': '🇸🇦', 'Japan': '🇯🇵', 'South Korea': '🇰🇷',
    'Australia': '🇦🇺', 'Serbia': '🇷🇸', 'Cameroon': '🇨🇲', 'Ghana': '🇬🇭',
    'Iran': '🇮🇷', 'Poland': '🇵🇱', 'Denmark': '🇩🇰', 'Switzerland': '🇨🇭',
    'Sweden': '🇸🇪', 'Senegal': '🇸🇳', 'Morocco': '🇲🇦', 'Tunisia': '🇹🇳',
    'Egypt': '🇪🇬', 'Nigeria': '🇳🇬', 'Chile': '🇨🇱', 'Peru': '🇵🇪',
    'Ecuador': '🇪🇨', 'Wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'Türkiye': '🇹🇷', 'Romania': '🇷🇴', 'Hungary': '🇭🇺', 'Austria': '🇦🇹',
    'Czechia': '🇨🇿', 'Ukraine': '🇺🇦', 'Greece': '🇬🇷', 'Norway': '🇳🇴',
    'Finland': '🇫🇮', 'Iceland': '🇮🇸', 'Haiti': '🇭🇹', 'Curaçao': '🇨🇼',
    'Cape Verde': '🇨🇻', 'New Zealand': '🇳🇿', 'Bosnia-Herz': '🇧🇦', 'Qatar': '🇶🇦',
    'Paraguay': '🇵🇾', 'Egypt': '🇪🇬', 'Ivory Coast': '🇨🇮', 'Jordan': '🇯🇴',
    'Algeria': '🇩🇿', 'Congo DR': '🇨🇩', 'Uzbekistan': '🇺🇿', 'Panama': '🇵🇦',
    'Iraq': '🇮🇶', 'South Africa': '🇿🇦', 'TBD': '❓'
}

PLAYER_DB = {
    'lionel messi': {'team': 'Argentina', 'position': 'Forward', 'age': 39, 'world_cups': 6, 'goals': 5, 'assists': 2, 'bio': '2022 World Cup winner. Currently leading 2026 World Cup scoring charts with 5 goals. The GOAT defies age.'},
    'cristiano ronaldo': {'team': 'Portugal', 'position': 'Forward', 'age': 41, 'world_cups': 6, 'goals': 2, 'assists': 1, 'bio': 'All-time international goal scoring record holder. Playing in his 6th World Cup for Portugal.'},
    'kylian mbappe': {'team': 'France', 'position': 'Forward', 'age': 27, 'world_cups': 3, 'goals': 4, 'assists': 2, 'bio': '2018 World Cup winner. Hat-trick in 2022 Final. 4 goals in 2026 so far. France\'s talisman.'},
    'vinicius jr': {'team': 'Brazil', 'position': 'Forward', 'age': 26, 'world_cups': 2, 'goals': 4, 'assists': 2, 'bio': 'Real Madrid star. Brazil\'s explosive winger leading their attack with 4 goals in 2026.'},
    'erling haaland': {'team': 'Norway', 'position': 'Forward', 'age': 26, 'world_cups': 1, 'goals': 4, 'assists': 1, 'bio': 'Manchester City phenom. Norway qualified for first WC since 1998. Haaland scoring 4 goals.'},
    'jude bellingham': {'team': 'England', 'position': 'Midfielder', 'age': 23, 'world_cups': 2, 'goals': 2, 'assists': 1, 'bio': 'Real Madrid star. One of the most exciting young midfielders. 2 goals in 2026.'},
    'kevin de bruyne': {'team': 'Belgium', 'position': 'Midfielder', 'age': 35, 'world_cups': 3, 'goals': 2, 'assists': 3, 'bio': 'Belgium\'s creative maestro. Manchester City legend. 2 goals, 3 assists in 2026.'},
    'matheus cunha': {'team': 'Brazil', 'position': 'Forward', 'age': 29, 'world_cups': 1, 'goals': 3, 'assists': 2, 'bio': 'Wolfsburg forward. Creative force for Brazil with 3 goals in 2026 World Cup.'},
    'jonathan david': {'team': 'Canada', 'position': 'Forward', 'age': 36, 'world_cups': 2, 'goals': 3, 'assists': 1, 'bio': 'Lille striker. Belgium-born Canadian hero. 3 goals keeping Canada\'s hopes alive.'},
    'ismael saibari': {'team': 'Morocco', 'position': 'Midfielder', 'age': 29, 'world_cups': 2, 'goals': 3, 'assists': 1, 'bio': 'PSG midfielder. Key figure for Morocco with 3 goals in 2026 World Cup.'},
    'johann manzambi': {'team': 'Switzerland', 'position': 'Forward', 'age': 26, 'world_cups': 1, 'goals': 3, 'assists': 0, 'bio': 'St. Gallen forward. Switzerland\'s top scorer in their last two Group A matches runs.'},
    'brian brobbey': {'team': 'Netherlands', 'position': 'Forward', 'age': 26, 'world_cups': 1, 'goals': 3, 'assists': 1, 'bio': 'Ajax homegrown talent. Oranje dynamic striker in the 2026 Group F.'},
    'deniz undav': {'team': 'Germany', 'position': 'Midfielder', 'age': 29, 'world_cups': 1, 'goals': 3, 'assists': 2, 'bio': 'Belgian-born German attacking mid. Currently ranked 11 in Group I.'},
}

TEAM_INFO = {
    'Argentina': {'flag': '🇦🇷', 'confederation': 'CONMEBOL', 'manager': 'Lionel Scaloni', 'world_cups_won': 3, 'ranking': 1},
    'Brazil': {'flag': '🇧🇷', 'confederation': 'CONMEBOL', 'manager': 'Dorival Júnior', 'world_cups_won': 5, 'ranking': 5},
    'France': {'flag': '🇫🇷', 'confederation': 'UEFA', 'manager': 'Didier Deschamps', 'world_cups_won': 2, 'ranking': 2},
    'Germany': {'flag': '🇩🇪', 'confederation': 'UEFA', 'manager': 'Julian Nagelsmann', 'world_cups_won': 4, 'ranking': 11},
    'Spain': {'flag': '🇪🇸', 'confederation': 'UEFA', 'manager': 'Luis de la Fuente', 'world_cups_won': 1, 'ranking': 3},
    'England': {'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'confederation': 'UEFA', 'manager': 'Thomas Tuchel', 'world_cups_won': 1, 'ranking': 4},
    'Netherlands': {'flag': '🇳🇱', 'confederation': 'UEFA', 'manager': 'Ronald Koeman', 'world_cups_won': 0, 'ranking': 7},
    'Portugal': {'flag': '🇵🇹', 'confederation': 'UEFA', 'manager': 'Roberto Martínez', 'world_cups_won': 0, 'ranking': 8},
    'Belgium': {'flag': '🇧🇪', 'confederation': 'UEFA', 'manager': 'Rudi Garcia', 'world_cups_won': 0, 'ranking': 6},
    'Colombia': {'flag': '🇨🇴', 'confederation': 'CONMEBOL', 'manager': 'Néstor Lorenzo', 'world_cups_won': 0, 'ranking': 9},
    'Mexico': {'flag': '🇲🇽', 'confederation': 'CONCACAF', 'manager': 'Javier Aguirre', 'world_cups_won': 0, 'ranking': 15},
    'USA': {'flag': '🇺🇸', 'confederation': 'CONCACAF', 'manager': 'Mauricio Pochettino', 'world_cups_won': 0, 'ranking': 14},
    'Switzerland': {'flag': '🇨🇭', 'confederation': 'UEFA', 'manager': 'Murat Yakin', 'world_cups_won': 0, 'ranking': 17},
    'Japan': {'flag': '🇯🇵', 'confederation': 'AFC', 'manager': 'Hajime Moriyasu', 'world_cups_won': 0, 'ranking': 16},
    'Morocco': {'flag': '🇲🇦', 'confederation': 'CAF', 'manager': 'Walid Regragui', 'world_cups_won': 0, 'ranking': 14},
    'Senegal': {'flag': '🇸🇳', 'confederation': 'CAF', 'manager': 'Pape Matar Cissé', 'world_cups_won': 0, 'ranking': 19},
    'Norway': {'flag': '🇳🇴', 'confederation': 'UEFA', 'manager': 'Ståle Solbakken', 'world_cups_won': 0, 'ranking': 36},
    'Türkiye': {'flag': '🇹🇷', 'confederation': 'UEFA', 'manager': 'Vincenzo Montella', 'world_cups_won': 0, 'ranking': 28},
    'Egypt': {'flag': '🇪🇬', 'confederation': 'CAF', 'manager': 'Hassan Shehata', 'world_cups_won': 0, 'ranking': 35},
    'Cape Verde': {'flag': '🇨🇻', 'confederation': 'CAF', 'manager': 'Bubista', 'world_cups_won': 0, 'ranking': 59},
    'Uruguay': {'flag': '🇺🇾', 'confederation': 'CONMEBOL', 'manager': 'Marcelo Bielsa', 'world_cups_won': 2, 'ranking': 12},
    'Canada': {'flag': '🇨🇦', 'confederation': 'CONCACAF', 'manager': 'Jesse Marsch', 'world_cups_won': 0, 'ranking': 31},
    'Costa Rica': {'flag': '🇨🇷', 'confederation': 'CONCACAF', 'manager': 'Gustavo Alfaro', 'world_cups_won': 0, 'ranking': 40},
    'Saudi Arabia': {'flag': '🇸🇦', 'confederation': 'AFC', 'manager': 'Roberto Mancini', 'world_cups_won': 0, 'ranking': 49},
    'Australia': {'flag': '🇦🇺', 'confederation': 'AFC', 'manager': 'Tony Popovic', 'world_cups_won': 0, 'ranking': 25},
    'Scotland': {'flag': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'confederation': 'UEFA', 'manager': 'Steve Clarke', 'world_cups_won': 0, 'ranking': 39},
    'Ivory Coast': {'flag': '🇨🇮', 'confederation': 'CAF', 'manager': 'Emerse Fae', 'world_cups_won': 0, 'ranking': 37},
    'Haiti': {'flag': '🇭🇹', 'confederation': 'CONCACAF', 'manager': 'Wilfried Jean-Baptiste', 'world_cups_won': 0, 'ranking': 90},
    'Congo DR': {'flag': '🇨🇩', 'confederation': 'CAF', 'manager': 'Sébastien Desabre', 'world_cups_won': 0, 'ranking': 64},
    'Iran': {'flag': '🇮🇷', 'confederation': 'AFC', 'manager': 'Amir Ghalenoei', 'world_cups_won': 0, 'ranking': 18},
    'Egypt': {'flag': '🇪🇬', 'confederation': 'CAF', 'manager': 'Hassan Shehata', 'world_cups_won': 0, 'ranking': 35},
    'TBD': {'flag': '❓', 'confederation': '-', 'manager': '-', 'world_cups_won': 0, 'ranking': '-'},
}


def update_data():
    """Update cached data from sources"""
    global cached_data
    try:
        standings = scrape_fifa2026_data()
        cached_data['standings'] = standings
        cached_data['schedule'] = get_match_schedule()
        cached_data['ranking'] = get_world_ranking()
        cached_data['scorers'] = get_top_scorers()
        cached_data['last_updated'] = standings.get('last_updated')
        print(f"Data updated at {cached_data['last_updated']}")
    except Exception as e:
        print(f"Error updating data: {e}")
        # Use fallback
        cached_data['standings'] = scrape_fifa2026_data()


def scrape_periodically():
    """Background thread to scrape data periodically"""
    while True:
        update_data()
        time.sleep(300)  # Update every 5 minutes


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/standings')
def api_standings():
    if not cached_data['standings']:
        update_data()
    # Include upcoming matches in standings response
    upcoming = get_upcoming_matches(limit=15)
    standings = dict(cached_data['standings'])
    standings['upcoming_matches'] = upcoming['upcoming']
    standings['live_matches'] = upcoming['live']
    standings['today'] = upcoming['today']
    return jsonify(standings)


@app.route('/api/schedule')
def api_schedule():
    if not cached_data['schedule']:
        update_data()
    return jsonify(cached_data['schedule'])


@app.route('/api/ranking')
def api_ranking():
    if not cached_data['ranking']:
        update_data()
    return jsonify(cached_data['ranking'])


@app.route('/api/scorers')
def api_scorers():
    if not cached_data['scorers']:
        update_data()
    return jsonify(cached_data['scorers'])


@app.route('/api/team/<team_name>')
def api_team(team_name):
    name = escape(team_name)
    team = TEAM_INFO.get(name)
    return jsonify(team or {'error': 'Team not found'})


@app.route('/api/player/<player_name>')
def api_player(player_name):
    name = escape(player_name).lower()
    
    # Search in player DB
    for key, player in PLAYER_DB.items():
        if name in key or key in name:
            return jsonify({'name': key.title(), **player})
    
    # Fuzzy search
    matches = []
    for key, player in PLAYER_DB.items():
        score = sum(1 for word in name.split() if word in key)
        if score > 0:
            matches.append({'name': key.title(), **player})
    
    if matches:
        return jsonify(matches[0])
    return jsonify({'error': 'Player not found'})


@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'last_updated': cached_data['last_updated'],
        'next_match': '2026-06-11 - Mexico vs TBD',
        'venue': 'Estadio Azteca, Mexico City'
    })


@app.route('/api/chat', methods=['POST'])
def chat_bot():
    """Simple chat bot for match/player queries"""
    data = request.get_json()
    user_message = escape(data.get('message', '')).lower().strip()
    
    response = generate_chat_response(user_message)
    return jsonify({'response': response})


def generate_chat_response(message):
    """Generate a response based on user message"""
    
    # Greeting
    if any(word in message for word in ['hello', 'hi', 'hey', 'hola', 'sup']):
        return "👋 Hey there! I'm your FIFA 2026 World Cup assistant. Ask me about teams, players, standings, match schedules, or rankings!"
    
    # Help
    if 'help' in message or 'what can you do' in message:
        return "🤖 I can help you with:\n• Team information (e.g., 'Tell me about Brazil')\n• Player stats (e.g., 'Messi stats')\n• Match schedules (e.g., 'When is the next match?')\n• Standings (e.g., 'Group A standings')\n• Rankings (e.g., 'Top 10 rankings')\n• Top scorers (e.g., 'Who is the top scorer?')\n\nJust ask naturally!"
    
    # Search for team names
    for team_name, info in TEAM_INFO.items():
        if team_name.lower() in message:
            flag = info.get('flag', '')
            return (
                f"{flag} **{team_name}**\n\n"
                f"🏆 World Cups Won: {info['world_cups_won']}\n"
                f"📊 FIFA Ranking: #{info['ranking']}\n"
                f"👨‍💼 Manager: {info['manager']}\n"
                f"🌍 Confederation: {info['confederation']}\n\n"
                f"Hosting the 2026 World Cup across USA, Canada, and Mexico!"
            )
    
    # Search for player names
    for key, player in PLAYER_DB.items():
        if len(message.split()) >= 1:
            words = message.split()
            for word in words:
                if len(word) > 3 and word in key:
                    return (
                        f"⚽ **{key.title()}** ({player['team']})\n\n"
                        f"📍 Position: {player['position']}\n"
                        f"🎂 Age: {player['age']}\n"
                        f"🏆 World Cups: {player['world_cups']}\n"
                        f"🥅 Goals: {player['goals']}\n"
                        f"🅰️ Assists: {player['assists']}\n\n"
                        f"📝 {player['bio']}"
                    )
    
    # Specific queries
    if any(word in message for word in ['schedule', 'next match', 'when']):
        return "📅 **FIFA 2026 Schedule**\n\nThe tournament kicks off on **June 11, 2026** at the iconic **Estadio Azteca** in Mexico City!\n\n• Group Stage: June 11-30\n• Round of 32: July 1-5\n• Round of 16: July 9-13\n• Quarter Finals: July 17-19\n• Semi Finals: July 25-27\n• Third Place: August 1\n• **FINAL: August 3, 2026 at MetLife Stadium (New Jersey)**\n\nUse the Schedule tab to see all matches!"
    
    if any(word in message for word in ['standings', 'table', 'who is leading']):
        return "📊 **Current Standings**\n\nThe tournament hasn't started yet! Group standings will appear here once matches begin. Check the Standings tab for the full group tables!"
    
    if any(word in message for word in ['ranking', 'top teams', 'best teams']):
        return "🏆 **FIFA World Rankings (Top 5)**\n\n1. 🇦🇷 Argentina - 1867 pts\n2. 🇫🇷 France - 1863 pts\n3. 🇪🇸 Spain - 1816 pts\n4. 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England - 1810 pts\n5. 🇧🇷 Brazil - 1776 pts\n\nSee the Leaderboard tab for the full ranking!"
    
    if any(word in message for word in ['scorer', 'top scorer', 'goals', 'who is top']):
        return "🥅 **Top Scorers All Time (WC Qualifiers + Finals)**\n\n1. 🇦🇷 Lionel Messi - 13 goals\n2. 🇵🇹 Cristiano Ronaldo - 11 goals\n3. 🇫🇷 Kylian Mbappé - 10 goals\n4. 🇵🇱 Robert Lewandowski - 9 goals\n5. 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Harry Kane - 8 goals\n\nMore stats in the Leaderboard tab!"
    
    if any(word in message for word in ['final', 'where is final', 'venue']):
        return "🏟️ **2026 World Cup Final**\n\n📅 Date: August 3, 2026\n📍 Venue: **MetLife Stadium**, New York/New Jersey\n🏟️ Capacity: 82,500\n\nThis will be the first World Cup Final ever held in the United States!"
    
    if 'winner' in message or 'who will win' in message:
        return "🔮 **Prediction?**\n\nIt's too early to tell! But the favorites are:\n• 🇦🇷 Argentina (defending champions)\n• 🇫🇷 France (2018 winners)\n• 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (strong young squad)\n• 🇪🇸 Spain (Euro 2024 winners)\n• 🇧🇷 Brazil (5-time champions)\n\nWho are YOU rooting for? 🤔"
    
    if 'host' in message or 'where' in message:
        return "🌎 **FIFA 2026 Host Countries**\n\nFor the first time ever, the World Cup is hosted by THREE nations:\n\n• 🇺🇸 **United States** - 11 host cities (NY/LA/Miami/SF/Seattle/Dallas/Houston/Atlanta/Philadelphia/Boston/KC)\n• 🇲🇽 **Mexico** - 3 host cities (Mexico City/Guadalajara/Monterrey)\n• 🇨🇦 **Canada** - 2 host cities (Toronto/Vancouver)\n\nAlso the first World Cup with 48 teams! 🎉"
    
    # Default response
    return "🤔 I'm not sure about that. Try asking me about:\n• A team (e.g., 'Brazil', 'France')\n• A player (e.g., 'Messi', 'Mbappe')\n• Match schedule\n• Standings\n• Rankings\n• Top scorers\n• The final\n\nType 'help' for more options!"


# Initialize data on first request
update_data()

# Start background scraping thread
scraper_thread = threading.Thread(target=scrape_periodically, daemon=True)
scraper_thread.start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
