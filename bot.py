"""
FIFA 2026 World Cup Telegram Bot
Dedicated bot for match alerts, standings, and player updates.
Runs as a separate web service on Render or alongside the Flask app.
"""

import logging
import os
import time
import requests

# Bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
FIFA_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')  # Channel/chat ID for broadcast

# Base URL for the local Flask app (external URL on Render)
LOCAL_API = os.environ.get('LOCAL_API_URL', 'https://fifa2026-tracker.onrender.com')

# All teams + flags
TEAMS = {
    'Argentina': '🇦🇷', 'Brazil': '🇧🇷', 'France': '🇫🇷', 'Germany': '🇩🇪',
    'Spain': '🇪🇸', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Italy': '🇮🇹', 'Netherlands': '🇳🇱',
    'Portugal': '🇵🇹', 'Belgium': '🇧🇪', 'Croatia': '🇭🇷', 'Uruguay': '🇺🇾',
    'Colombia': '🇨🇴', 'Mexico': '🇲🇽', 'USA': '🇺🇸', 'Canada': '🇨🇦',
    'Costa Rica': '🇨🇷', 'Saudi Arabia': '🇸🇦', 'Japan': '🇯🇵', 'South Korea': '🇰🇷',
    'Australia': '🇦🇺', 'Serbia': '🇷🇸', 'Cameroon': '🇨🇲', 'Ghana': '🇬🇭',
    'Iran': '🇮🇷', 'Poland': '🇵🇱', 'Denmark': '🇩🇰', 'Switzerland': '🇨🇭',
    'Sweden': '🇸🇪', 'Senegal': '🇸🇳', 'Morocco': '🇲🇦', 'Tunisia': '🇹🇳',
    'Egypt': '🇪🇬', 'Nigeria': '🇳🇬', 'Chile': '🇨🇱', 'Peru': '🇵🇪',
    'Ecuador': '🇪🇨', 'Wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'Türkiye': '🇹🇷', 'Romania': '🇷🇴', 'Hungary': '🇭🇺', 'Austria': '🇦🇹',
    'Czechia': '🇨🇿', 'Ukraine': '🇺🇦', 'Greece': '🇬🇷', 'Norway': '🇳🇴',
    'Cape Verde': '🇨🇻', 'New Zealand': '🇳🇿', 'Qatar': '🇶🇦', 'TBD': '❓',
    'Panama': '🇵🇦', 'Iraq': '🇮🇶', 'South Africa': '🇿🇦'
}

PLAYERS = {
    'lionel messi': {'team': '🇦🇷 Argentina', 'position': 'Forward', 'goals': 5},
    'cristiano ronaldo': {'team': '🇵🇹 Portugal', 'position': 'Forward', 'goals': 2},
    'kylian mbappe': {'team': '🇫🇷 France', 'position': 'Forward', 'goals': 4},
    'vinicius jr': {'team': '🇧🇷 Brazil', 'position': 'Forward', 'goals': 4},
    'erling haaland': {'team': '🇳🇴 Norway', 'position': 'Forward', 'goals': 4},
    'jude bellingham': {'team': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 England', 'position': 'Midfielder', 'goals': 2},
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_api_data(endpoint):
    """Fetch data from the Flask API"""
    try:
        r = requests.get(f"{LOCAL_API}{endpoint}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        logger.warning(f"API call {endpoint} failed: {e}")
    return None


def escape_md(text):
    """Escape special chars for Telegram MarkdownV2"""
    special = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for ch in special:
        text = text.replace(ch, f'\\{ch}')
    return text


def send_message(chat_id, text, parse_mode='MarkdownV2'):
    """Send a message via Telegram Bot API"""
    if not TELEGRAM_BOT_TOKEN:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send msg: {e}")
        return False


def cmd_start():
    """Welcome message"""
    return (
        "🏆 *FIFA 2026 World Cup Tracker Bot*\n\n"
        "I'll keep you updated with:\n"
        "• 🔴 Live match alerts\n"
        "• ⚽ Goal notifications\n"
        "• 📊 Final scores\n"
        "• 📅 Upcoming matches\n\n"
        "*Commands:*\n"
        "/standings \\- Current standings\n"
        "/today \\- Today's matches\n"
        "/schedule \\- Full schedule\n"
        "/scorers \\- Top scorers\n"
        "/team <name> \\- Team info\n"
        "/player <name> \\- Player stats\n"
        "/follow <team> \\- Get alerts for a team\n"
        "/stop \\- Stop following a team\n\n"
        "Or just ask me anything\\!"
    )


def cmd_standings():
    data = get_api_data('/api/standings')
    if not data:
        return "❌ Could not fetch standings\\. Try again later\\."
    
    standings = data.get('standings', data.get('groups', {}))
    if not standings:
        return "📊 No standings available yet\\."
    
    msg = "🏆 *FIFA 2026 Standings*\\n\\n"
    for group in sorted(standings.keys())[:12]:
        teams = standings[group]
        if teams and isinstance(teams, list):
            msg += f"*{escape_md(group)}*\\n"
            for t in teams[:4]:
                msg += f"  {t['pos']}\\. {escape_md(t['team'])}: {t['pts']}pts ({t['pld']}P {t['w']}W {t['d']}D {t['l']}L)\\n"
            msg += "\\n"
    
    return msg


def cmd_today():
    data = get_api_data('/api/standings')
    if not data:
        return "❌ Could not fetch data"
    
    upcoming = data.get('upcoming_matches', [])
    today_str = data.get('today', '')
    today_matches = [m for m in upcoming if m.get('date') == today_str]
    
    if not today_matches:
        if upcoming:
            msg = f"📅 *Next Matches*\\n\\n"
            for m in upcoming[:5]:
                date_str = m['date']
                time_str = f" ⏰ {m.get('time_et', '')} / {m.get('time_ist', '')}" if m.get('time_et') else ''
                msg += f"📆 *{escape_md(date_str)}*\\n"
                msg += f"  {escape_md(m['home'])} vs {escape_md(m['away'])}\\n"
                msg += f"  🏟 {escape_md(m.get('venue', 'TBD'))}{time_str}\\n\\n"
            return msg
        else:
            return "📅 No matches scheduled today\\."

    msg = f"🗓 *Today's Matches ({escape_md(today_str)})*\\n\\n"
    for m in today_matches:
        status = "🔴 LIVE" if 'LIVE' in str(m.get('status', '')) else m.get('status', 'Scheduled')
        score = f" *{m['home_score']} : {m['away_score']}*" if m.get('home_score') is not None else " VS "
        time_str = f" ⏰ {m.get('time_et', '')} / {m.get('time_ist', '')}" if m.get('time_et') else ''
        msg += f"⚽ {escape_md(m['home'])} {score} {escape_md(m['away'])}\\n"
        msg += f"  🏟 {escape_md(m.get('venue', 'TBD'))} \\| {escape_md(status)}{time_str}\\n\\n"

    return msg


def cmd_schedule():
    data = get_api_data('/api/schedule')
    if not data:
        return "❌ Could not fetch schedule"
    
    msg = "📅 *FIFA 2026 Match Schedule*\\n"
    stages = {
        'group_stage': 'Group Stage',
        'round_of_32': 'Round of 32',
        'round_of_16': 'Round of 16',
        'quarter_finals': 'Quarter Finals',
        'semi_finals': 'Semi Finals',
        'final': 'Grand Final'
    }
    
    for key, label in stages.items():
        matches = data.get(key, [])
        if matches:
            msg += f"\\n*{escape_md(label)}* ({len(matches)} matches)\\n"
            for m in matches[:3]:
                time_str = f" ({m.get('time_et', '')})" if m.get('time_et') else ''
                msg += f"  {escape_md(m['date'])}: {escape_md(m['home'])} vs {escape_md(m['away'])}{time_str}\\n"
            if len(matches) > 3:
                msg += f"  \\.\\.\\. and {len(matches)-3} more\\n"
    
    return msg


def cmd_scorers():
    data = get_api_data('/api/scorers')
    if not data:
        return "❌ Could not fetch scorers"
    
    msg = "🥅 *Top Scorers*\\n\\n"
    for s in data[:10]:
        try:
            msg += f"{s['rank']}\\. *{escape_md(s['player'])}* ({escape_md(s['team'])}) \\- {s['goals']} goals\\n"
        except (KeyError, IndexError):
            continue
    return msg


def cmd_team(name):
    """Get team info"""
    name_lower = name.lower().strip()
    flag = '🏳️'
    for team, f in TEAMS.items():
        if team.lower() in name_lower or name_lower in team.lower():
            flag = f
            break
    return (
        f"{flag} *{escape_md(name)}*\n\n"
        f"🌍 FIFA 2026 World Cup Participant\n\n"
        f"Track this team on the web app for full stats, fixtures and results\\!"
    )


def cmd_player(name):
    """Get player info"""
    name_lower = name.lower().strip()
    for player, info in PLAYERS.items():
        words = name_lower.split()
        if any(w in player for w in words if len(w) > 3):
            return (
                f"⚽ *{escape_md(player.title())}* {info['team']}\n\n"
                f"📍 Position: {info['position']}\n"
                f"🥅 Goals: {info['goals']}\n\n"
                f"Ask about any player via the web app for more details\\!"
            )
    return f"❌ Player not found\\. Try Messi, Mbappe, Ronaldo, Haaland, etc\\."


def process_command(text, chat_id):
    """Process incoming message and return response text"""
    if not text:
        return None
    
    parts = text.strip().split()
    cmd = parts[0].lower() if parts else ''
    args = ' '.join(parts[1:]) if len(parts) > 1 else ''
    
    if cmd == '/start':
        return escape_md(cmd_start())
    elif cmd == '/standings':
        return cmd_standings()
    elif cmd in ('/today', '/matches'):
        return cmd_today()
    elif cmd == '/schedule':
        return cmd_schedule()
    elif cmd == '/scorers':
        return cmd_scorers()
    elif cmd == '/team' and args:
        return cmd_team(args)
    elif cmd == '/player' and args:
        return cmd_player(args)
    else:
        # Natural language
        return process_natural(text)


def process_natural(text):
    """Handle natural language queries"""
    text_lower = text.lower().strip()
    
    # Team queries
    for team, flag in TEAMS.items():
        if team.lower() in text_lower:
            return f"{flag} *{escape_md(team)}*\\n\\nUse /team {escape_md(team)} for details, or /follow {escape_md(team)} for match alerts\\!"
    
    # Player queries
    for player, info in PLAYERS.items():
        words = text_lower.split()
        if any(w in player for w in words if len(w) > 3):
            return (
                f"*{escape_md(player.title())}* {info['team']}\\n"
                f"Position: {info['position']}\\n"
                f"Goals: {info['goals']}\\n"
            )
    
    # Greetings
    if any(w in text_lower for w in ['hi', 'hello', 'hey']):
        return "👋 Hey\\! I'm the FIFA 2026 Bot\\.\nType /start to see what I can do, or just ask about a team \\(e.g., 'Argentina'\\) or player \\(e.g., 'Messi'\\)\\!"
    
    return "🤔 I'm not sure about that\\.\nUse /start to see available commands, or ask about a specific team/player\\. Example: 'Brazil' or 'Mbappe'"


class FifaTelegramBot:
    """FIFA 2026 Telegram Bot using long polling"""
    
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.offset = 0
        self.running = True
        self.last_match_states = {}  # Track match states for goal alerts
    
    def _api(self, method, **kwargs):
        """Call Telegram Bot API"""
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        try:
            if 'data' in kwargs:
                r = requests.post(url, json=kwargs['data'], timeout=30)
            elif 'params' in kwargs:
                r = requests.get(url, params=kwargs['params'], timeout=30)
            else:
                r = requests.post(url, json=kwargs, timeout=30)
            return r.json() if r.status_code == 200 else None
        except Exception as e:
            logger.error(f"API error {method}: {e}")
            return None
    
    def send(self, chat_id, text):
        """Send message"""
        return self._api('sendMessage', data={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'MarkdownV2'
        })
    
    def process_update(self, update):
        """Process a single update"""
        msg = update.get('message', {})
        if not msg:
            return
        
        chat_id = msg['chat']['id']
        text = msg.get('text', '')
        if not text:
            return
        
        # Handle commands
        response = process_command(text, chat_id)
        if response:
            self.send(chat_id, response)
    
    def poll_once(self):
        """Single poll for updates (for webhook/serverless mode)"""
        result = self._api('getUpdates', params={
            'offset': self.offset,
            'timeout': 30,
            'allowed_updates': ['message']
        })
        
        if result and result.get('ok'):
            updates = result.get('result', [])
            for update in updates:
                self.offset = update['update_id'] + 1
                self.process_update(update)
    
    def run_forever(self):
        """Long polling loop (standalone mode)"""
        logger.info("Bot: Starting polling loop")
        
        # Clear pending updates
        self._api('getUpdates', params={'offset': 0, 'timeout': 5})
        
        while self.running:
            try:
                self.poll_once()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Poll error: {e}")
                time.sleep(5)


def run_bot():
    """Run bot standalone"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    bot = FifaTelegramBot()
    bot.run_forever()


if __name__ == '__main__':
    run_bot()
