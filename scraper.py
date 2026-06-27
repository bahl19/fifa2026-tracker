import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone

def scrape_fifa2026_data():
    """Scrape FIFA 2026 World Cup data from Wikipedia"""
    
    # FIFA 2026 World Cup data
    base_url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"
    
    try:
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'groups': {},
            'matches': [],
            'teams_ranking': []
        }
        
        # Parse group tables
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        group_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
                        'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                        'Q', 'R']
        
        group_idx = 0
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
                
            headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
            
            if 'Team' in headers or 'Pos' in headers:
                if group_idx < len(group_labels):
                    group_name = group_labels[group_idx]
                    teams = []
                    
                    for row in rows[2:]:  # Skip header rows
                        cells = row.find_all(['td'])
                        if len(cells) >= 6:
                            cells = [c.get_text(strip=True) for c in cells]
                            team_data = {
                                'pos': cells[0],
                                'team': cells[1].replace(' (H)', '').strip(),
                                'team_flag': cells[1],
                                'pld': cells[2] if len(cells) > 2 else '0',
                                'w': cells[3] if len(cells) > 3 else '0',
                                'd': cells[4] if len(cells) > 4 else '0',
                                'l': cells[5] if len(cells) > 5 else '0',
                                'gf': cells[6] if len(cells) > 6 else '0',
                                'ga': cells[7] if len(cells) > 7 else '0',
                                'gd': cells[8] if len(cells) > 8 else '0',
                                'pts': cells[9] if len(cells) > 9 else '0',
                            }
                            teams.append(team_data)
                    
                    if teams:
                        # Sort by points descending
                        teams.sort(key=lambda x: int(x['pts']) if x['pts'].isdigit() else 0, reverse=True)
                        data['groups'][group_name] = teams
                        group_idx += 1
                else:
                    break
        
        return data
        
    except Exception as e:
        print(f"Scraping error: {e}")
        return get_fallback_data()


def get_match_schedule():
    """Get match schedule for 2026 World Cup"""
    return {
        "round_of_64": [
            {"match": 1, "date": "2026-06-11", "home": "Mexico", "away": "TBD", "venue": "Estadio Azteca"},
            {"match": 2, "date": "2026-06-11", "home": "Spain", "away": "TBD", "venue": "Estadio Akron"},
            {"match": 3, "date": "2026-06-12", "home": "Brazil", "away": "TBD", "venue": "Estadio Jalisco"},
            {"match": 4, "date": "2026-06-12", "home": "Argentina", "away": "TBD", "venue": "Estadio Universitario"},
            {"match": 5, "date": "2026-06-13", "home": "Germany", "away": "TBD", "venue": "Estadio BBVA"},
            {"match": 6, "date": "2026-06-13", "home": "France", "away": "TBD", "venue": "Estadio Monterrey"},
            {"match": 7, "date": "2026-06-14", "home": "England", "away": "TBD", "venue": "SoFi Stadium"},
            {"match": 8, "date": "2026-06-14", "home": "Portugal", "away": "TBD", "venue": "MetLife Stadium"},
            {"match": 9, "date": "2026-06-15", "home": "Netherlands", "away": "TBD", "venue": "Rose Bowl"},
            {"match": 10, "date": "2026-06-15", "home": "Italy", "away": "TBD", "venue": "Hard Rock Stadium"},
            {"match": 11, "date": "2026-06-16", "home": "Belgium", "away": "TBD", "venue": "TQL Stadium"},
            {"match": 12, "date": "2026-06-16", "home": "Croatia", "away": "TBD", "venue": "Bank of America Stadium"},
            {"match": 13, "date": "2026-06-17", "home": "Uruguay", "away": "TBD", "venue": "Levi's Stadium"},
            {"match": 14, "date": "2026-06-17", "home": "Denmark", "away": "TBD", "venue": "NRG Stadium"},
            {"match": 15, "date": "2026-06-18", "home": "Colombia", "away": "TBD", "venue": "Mercedes-Benz Stadium"},
            {"match": 16, "date": "2026-06-18", "home": "Switzerland", "away": "TBD", "venue": "Allianz Arena (Munich) Mock"},
        ],
        "round_of_32": [
            {"match": 17, "date": "2026-06-22", "home": "TBD", "away": "TBD", "venue": "SoFi Stadium"},
            {"match": 18, "date": "2026-06-22", "home": "TBD", "away": "TBD", "venue": "Estadio Azteca"},
            {"match": 19, "date": "2026-06-23", "home": "TBD", "away": "TBD", "venue": "MetLife Stadium"},
            {"match": 20, "date": "2026-06-23", "home": "TBD", "away": "TBD", "venue": "TQL Stadium"},
            {"match": 21, "date": "2026-06-24", "home": "TBD", "away": "TBD", "venue": "Rose Bowl"},
            {"match": 22, "date": "2026-06-24", "home": "TBD", "away": "TBD", "venue": "Estadio BBVA"},
            {"match": 23, "date": "2026-06-25", "home": "TBD", "away": "TBD", "venue": "Hard Rock Stadium"},
            {"match": 24, "date": "2026-06-25", "home": "TBD", "away": "TBD", "venue": "Levi's Stadium"},
        ],
        "round_of_16": [
            {"match": 25, "date": "2026-06-29", "home": "TBD", "away": "TBD", "venue": "SoFi Stadium"},
            {"match": 26, "date": "2026-06-29", "home": "TBD", "away": "TBD", "venue": "Estadio Jalisco"},
            {"match": 27, "date": "2026-06-30", "home": "TBD", "away": "TBD", "venue": "MetLife Stadium"},
            {"match": 28, "date": "2026-06-30", "home": "TBD", "away": "TBD", "venue": "Estadio Azteca"},
        ],
        "quarter_finals": [
            {"match": 29, "date": "2026-07-04", "home": "TBD", "away": "TBD", "venue": "SoFi Stadium"},
            {"match": 30, "date": "2026-07-04", "home": "TBD", "away": "TBD", "venue": "MetLife Stadium"},
            {"match": 31, "date": "2026-07-05", "home": "TBD", "away": "TBD", "venue": "Rose Bowl"},
            {"match": 32, "date": "2026-07-05", "home": "TBD", "away": "TBD", "venue": "Estadio Azteca"},
        ],
        "semi_finals": [
            {"match": 33, "date": "2026-07-11", "home": "TBD", "away": "TBD", "venue": "AT&T Stadium"},
            {"match": 34, "date": "2026-07-11", "home": "TBD", "away": "TBD", "venue": "MetLife Stadium"},
        ],
        "third_place": [
            {"match": 35, "date": "2026-07-18", "home": "TBD", "away": "TBD", "venue": "Hard Rock Stadium"},
        ],
        "final": [
            {"match": 36, "date": "2026-07-19", "home": "TBD", "away": "TBD", "venue": "MetLife Stadium, New Jersey"},
        ]
    }


def get_world_ranking():
    """Get FIFA World Ranking (top teams from CONCACAF/World)"""
    return [
        {"rank": 1, "team": "Argentina", "points": 1867, "trend": "up"},
        {"rank": 2, "team": "France", "points": 1863, "trend": "down"},
        {"rank": 3, "team": "Spain", "points": 1816, "trend": "same"},
        {"rank": 4, "team": "England", "points": 1810, "trend": "up"},
        {"rank": 5, "team": "Brazil", "points": 1776, "trend": "down"},
        {"rank": 6, "team": "Belgium", "points": 1740, "trend": "same"},
        {"rank": 7, "team": "Netherlands", "points": 1731, "trend": "up"},
        {"rank": 8, "team": "Portugal", "points": 1725, "trend": "same"},
        {"rank": 9, "team": "Colombia", "points": 1717, "trend": "up"},
        {"rank": 10, "team": "Italy", "points": 1702, "trend": "down"},
        {"rank": 11, "team": "Germany", "points": 1699, "trend": "up"},
        {"rank": 12, "team": "Uruguay", "points": 1698, "trend": "same"},
        {"rank": 13, "team": "Croatia", "points": 1693, "trend": "down"},
        {"rank": 14, "team": "Japan", "points": 1685, "trend": "up"},
        {"rank": 15, "team": "Mexico", "points": 1673, "trend": "same"},
    ]


def get_top_scorers():
    """Get top scorers"""
    return [
        {"rank": 1, "player": "Lionel Messi", "team": "Argentina", "goals": 13, "assists": 8},
        {"rank": 2, "player": "Cristiano Ronaldo", "team": "Portugal", "goals": 11, "assists": 5},
        {"rank": 3, "player": "Kylian Mbappé", "team": "France", "goals": 10, "assists": 4},
        {"rank": 4, "player": "Robert Lewandowski", "team": "Poland", "goals": 9, "assists": 3},
        {"rank": 5, "player": "Harry Kane", "team": "England", "goals": 8, "assists": 6},
        {"rank": 6, "player": "Mohamed Salah", "team": "Egypt", "goals": 8, "assists": 4},
        {"rank": 7, "player": "Neymar Jr", "team": "Brazil", "goals": 7, "assists": 7},
        {"rank": 8, "player": "Lautaro Martinez", "team": "Argentina", "goals": 7, "assists": 2},
        {"rank": 9, "player": "Erling Haaland", "team": "Northern Ireland", "goals": 6, "assists": 3},
        {"rank": 10, "player": "Álvaro Morata", "team": "Spain", "goals": 6, "assists": 2},
    ]


def get_fallback_data():
    """Fallback data if scraping fails"""
    return {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "groups": {
            "A": [
                {"pos": 1, "team": "Mexico", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 2, "team": "Canada", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 3, "team": "Costa Rica", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 4, "team": "USA", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
            ],
            "B": [
                {"pos": 1, "team": "Brazil", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 2, "team": "Switzerland", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 3, "team": "Serbia", "pd": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 4, "team": "Cameroon", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
            ],
            "C": [
                {"pos": 1, "team": "Argentina", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 2, "team": "Netherlands", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 3, "team": "Saudi Arabia", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 4, "team": "Australia", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
            ],
            "D": [
                {"pos": 1, "team": "Germany", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 2, "team": "France", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 3, "team": "Iceland", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
                {"pos": 4, "team": "Iran", "pld": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0},
            ],
        },
        "matches": []
    }
