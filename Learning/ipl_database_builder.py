import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

class IPLDatabaseBuilder:
    def __init__(self, db_path='ipl_cricket.db'):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create all necessary tables for the IPL database"""
        
        # Matches table - core match information
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_number INTEGER,
                event_name TEXT,
                season TEXT,
                match_type TEXT,
                gender TEXT,
                city TEXT,
                venue TEXT,
                match_date DATE,
                balls_per_over INTEGER,
                overs INTEGER,
                toss_winner TEXT,
                toss_decision TEXT,
                outcome_winner TEXT,
                outcome_by_runs INTEGER,
                outcome_by_wickets INTEGER,
                created_date DATE,
                data_version TEXT
            )
        ''')
        
        # Teams table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT UNIQUE
            )
        ''')
        
        # Match teams junction table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_teams (
                match_id INTEGER,
                team_id INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches(match_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id),
                PRIMARY KEY (match_id, team_id)
            )
        ''')
        
        # Players table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                player_name TEXT UNIQUE
            )
        ''')
        
        # Match players junction table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_players (
                match_id INTEGER,
                player_id TEXT,
                team_id INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches(match_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id),
                PRIMARY KEY (match_id, player_id)
            )
        ''')
        
        # Player of match
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_of_match (
                match_id INTEGER,
                player_id TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(match_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                PRIMARY KEY (match_id, player_id)
            )
        ''')
        
        # Officials table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS officials (
                official_id INTEGER PRIMARY KEY AUTOINCREMENT,
                official_name TEXT UNIQUE
            )
        ''')
        
        # Match officials junction table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_officials (
                match_id INTEGER,
                official_id INTEGER,
                role TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(match_id),
                FOREIGN KEY (official_id) REFERENCES officials(official_id),
                PRIMARY KEY (match_id, official_id, role)
            )
        ''')
        
        # Innings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS innings (
                innings_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                innings_number INTEGER,
                batting_team_id INTEGER,
                target_runs INTEGER,
                target_overs INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches(match_id),
                FOREIGN KEY (batting_team_id) REFERENCES teams(team_id)
            )
        ''')
        
        # Deliveries table (ball-by-ball data)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                innings_id INTEGER,
                over_number INTEGER,
                ball_number INTEGER,
                batter_id TEXT,
                bowler_id TEXT,
                non_striker_id TEXT,
                runs_batter INTEGER,
                runs_extras INTEGER,
                runs_total INTEGER,
                extras_type TEXT,
                extras_amount INTEGER,
                is_wicket BOOLEAN,
                FOREIGN KEY (innings_id) REFERENCES innings(innings_id),
                FOREIGN KEY (batter_id) REFERENCES players(player_id),
                FOREIGN KEY (bowler_id) REFERENCES players(player_id),
                FOREIGN KEY (non_striker_id) REFERENCES players(player_id)
            )
        ''')
        
        # Wickets table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wickets (
                wicket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                delivery_id INTEGER,
                player_out_id TEXT,
                kind TEXT,
                FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id),
                FOREIGN KEY (player_out_id) REFERENCES players(player_id)
            )
        ''')
        
        # Fielders table (for wickets)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wicket_fielders (
                wicket_id INTEGER,
                player_id TEXT,
                FOREIGN KEY (wicket_id) REFERENCES wickets(wicket_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        ''')
        
        self.conn.commit()
        print("✓ Database tables created successfully!")
        
    def get_or_create_team(self, team_name):
        """Get team_id or create new team"""
        self.cursor.execute('SELECT team_id FROM teams WHERE team_name = ?', (team_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            self.cursor.execute('INSERT INTO teams (team_name) VALUES (?)', (team_name,))
            return self.cursor.lastrowid
            
    def get_or_create_official(self, official_name):
        """Get official_id or create new official"""
        self.cursor.execute('SELECT official_id FROM officials WHERE official_name = ?', (official_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            self.cursor.execute('INSERT INTO officials (official_name) VALUES (?)', (official_name,))
            return self.cursor.lastrowid
    
    def insert_player(self, player_name, player_id):
        """Insert player if not exists"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO players (player_id, player_name) 
            VALUES (?, ?)
        ''', (player_id, player_name))
        
    def import_match(self, json_file_path):
        """Import a single match from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            info = data['info']
            meta = data.get('meta', {})
            
            # Insert match
            match_date = info['dates'][0] if info.get('dates') else None
            
            outcome = info.get('outcome', {})
            outcome_by = outcome.get('by', {})
            
            self.cursor.execute('''
                INSERT INTO matches (
                    match_number, event_name, season, match_type, gender,
                    city, venue, match_date, balls_per_over, overs,
                    toss_winner, toss_decision, outcome_winner,
                    outcome_by_runs, outcome_by_wickets,
                    created_date, data_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                info.get('event', {}).get('match_number'),
                info.get('event', {}).get('name'),
                info.get('season'),
                info.get('match_type'),
                info.get('gender'),
                info.get('city'),
                info.get('venue'),
                match_date,
                info.get('balls_per_over'),
                info.get('overs'),
                info.get('toss', {}).get('winner'),
                info.get('toss', {}).get('decision'),
                outcome.get('winner'),
                outcome_by.get('runs'),
                outcome_by.get('wickets'),
                meta.get('created'),
                meta.get('data_version')
            ))
            
            match_id = self.cursor.lastrowid
            
            # Insert teams
            for team_name in info.get('teams', []):
                team_id = self.get_or_create_team(team_name)
                self.cursor.execute('''
                    INSERT OR IGNORE INTO match_teams (match_id, team_id)
                    VALUES (?, ?)
                ''', (match_id, team_id))
            
            # Insert players from registry
            registry = info.get('registry', {}).get('people', {})
            for player_name, player_id in registry.items():
                self.insert_player(player_name, player_id)
            
            # Insert match players
            for team_name, player_names in info.get('players', {}).items():
                team_id = self.get_or_create_team(team_name)
                for player_name in player_names:
                    player_id = registry.get(player_name)
                    if player_id:
                        self.cursor.execute('''
                            INSERT OR IGNORE INTO match_players (match_id, player_id, team_id)
                            VALUES (?, ?, ?)
                        ''', (match_id, player_id, team_id))
            
            # Insert player of match
            for player_name in info.get('player_of_match', []):
                player_id = registry.get(player_name)
                if player_id:
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO player_of_match (match_id, player_id)
                        VALUES (?, ?)
                    ''', (match_id, player_id))
            
            # Insert officials
            officials = info.get('officials', {})
            for role, names in officials.items():
                for name in names:
                    official_id = self.get_or_create_official(name)
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO match_officials (match_id, official_id, role)
                        VALUES (?, ?, ?)
                    ''', (match_id, official_id, role))
            
            # Insert innings and deliveries
            for innings_num, innings_data in enumerate(data.get('innings', []), 1):
                batting_team = innings_data.get('team')
                team_id = self.get_or_create_team(batting_team)
                
                target = innings_data.get('target', {})
                
                self.cursor.execute('''
                    INSERT INTO innings (match_id, innings_number, batting_team_id, target_runs, target_overs)
                    VALUES (?, ?, ?, ?, ?)
                ''', (match_id, innings_num, team_id, target.get('runs'), target.get('overs')))
                
                innings_id = self.cursor.lastrowid
                
                # Insert deliveries
                for over_data in innings_data.get('overs', []):
                    over_num = over_data.get('over')
                    
                    for ball_num, delivery in enumerate(over_data.get('deliveries', []), 1):
                        batter = delivery.get('batter')
                        bowler = delivery.get('bowler')
                        non_striker = delivery.get('non_striker')
                        
                        batter_id = registry.get(batter)
                        bowler_id = registry.get(bowler)
                        non_striker_id = registry.get(non_striker)
                        
                        runs = delivery.get('runs', {})
                        extras = delivery.get('extras', {})
                        
                        # Determine extras type and amount
                        extras_type = None
                        extras_amount = None
                        if extras:
                            extras_type = list(extras.keys())[0]
                            extras_amount = extras[extras_type]
                        
                        is_wicket = 'wickets' in delivery
                        
                        self.cursor.execute('''
                            INSERT INTO deliveries (
                                innings_id, over_number, ball_number,
                                batter_id, bowler_id, non_striker_id,
                                runs_batter, runs_extras, runs_total,
                                extras_type, extras_amount, is_wicket
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            innings_id, over_num, ball_num,
                            batter_id, bowler_id, non_striker_id,
                            runs.get('batter', 0), runs.get('extras', 0), runs.get('total', 0),
                            extras_type, extras_amount, is_wicket
                        ))
                        
                        delivery_id = self.cursor.lastrowid
                        
                        # Insert wickets if any
                        for wicket in delivery.get('wickets', []):
                            player_out = wicket.get('player_out')
                            player_out_id = registry.get(player_out)
                            kind = wicket.get('kind')
                            
                            self.cursor.execute('''
                                INSERT INTO wickets (delivery_id, player_out_id, kind)
                                VALUES (?, ?, ?)
                            ''', (delivery_id, player_out_id, kind))
                            
                            wicket_id = self.cursor.lastrowid
                            
                            # Insert fielders
                            for fielder in wicket.get('fielders', []):
                                fielder_name = fielder.get('name')
                                fielder_id = registry.get(fielder_name)
                                if fielder_id:
                                    self.cursor.execute('''
                                        INSERT INTO wicket_fielders (wicket_id, player_id)
                                        VALUES (?, ?)
                                    ''', (wicket_id, fielder_id))
            
            self.conn.commit()
            return match_id
            
        except Exception as e:
            print(f"Error importing {json_file_path}: {e}")
            self.conn.rollback()
            return None
    
    def import_all_matches(self, json_directory):
        """Import all JSON files from a directory"""
        json_files = list(Path(json_directory).glob('*.json'))
        total_files = len(json_files)
        
        print(f"\nFound {total_files} JSON files to import...")
        
        successful = 0
        failed = 0
        
        for i, json_file in enumerate(json_files, 1):
            if i % 50 == 0 or i == 1:
                print(f"Processing: {i}/{total_files} files...")
            
            match_id = self.import_match(json_file)
            if match_id:
                successful += 1
            else:
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"Import Complete!")
        print(f"{'='*50}")
        print(f"✓ Successfully imported: {successful} matches")
        if failed > 0:
            print(f"✗ Failed to import: {failed} matches")
        
        self.print_statistics()
    
    def print_statistics(self):
        """Print database statistics"""
        print(f"\n{'='*50}")
        print("DATABASE STATISTICS")
        print(f"{'='*50}")
        
        self.cursor.execute('SELECT COUNT(*) FROM matches')
        print(f"Total Matches: {self.cursor.fetchone()[0]}")
        
        self.cursor.execute('SELECT COUNT(*) FROM teams')
        print(f"Total Teams: {self.cursor.fetchone()[0]}")
        
        self.cursor.execute('SELECT COUNT(*) FROM players')
        print(f"Total Players: {self.cursor.fetchone()[0]}")
        
        self.cursor.execute('SELECT COUNT(*) FROM deliveries')
        print(f"Total Deliveries: {self.cursor.fetchone()[0]}")
        
        self.cursor.execute('SELECT COUNT(*) FROM wickets')
        print(f"Total Wickets: {self.cursor.fetchone()[0]}")
        
        print(f"{'='*50}\n")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("Database connection closed.")


# Example usage
if __name__ == "__main__":
    # Initialize the database builder
    db = IPLDatabaseBuilder('ipl_cricket.db')
    
    # Specify your JSON files directory
    # Change this to the path where your JSON files are located
    json_directory = input("Enter the path to your JSON files directory: ").strip()
    
    if os.path.exists(json_directory):
        db.import_all_matches(json_directory)
        db.close()
        print("\n✓ Database created successfully: ipl_cricket.db")
    else:
        print(f"Error: Directory '{json_directory}' not found!")
        db.close()
