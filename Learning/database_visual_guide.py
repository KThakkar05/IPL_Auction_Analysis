"""
IPL Database Structure - Visual Guide
======================================

This file shows the database structure with examples.
"""

# ============================================================
# VISUAL DATABASE SCHEMA
# ============================================================

SCHEMA = """
┌─────────────────────────────────────────────────────────────────────────┐
│                        IPL CRICKET DATABASE                              │
└─────────────────────────────────────────────────────────────────────────┘

                            ┌──────────────────┐
                            │     MATCHES      │
                            │   (Core Info)    │
                            ├──────────────────┤
                            │ PK: match_id     │
                            │     date         │
                            │     venue        │
                            │     city         │
                            │     winner       │
                            │     toss_winner  │
                            │     season       │
                            └────────┬─────────┘
                                     │
            ┌────────────────────────┼─────────────────────────┐
            │                        │                         │
            ▼                        ▼                         ▼
    ┌──────────────┐        ┌──────────────┐         ┌──────────────┐
    │ MATCH_TEAMS  │        │MATCH_PLAYERS │         │MATCH_OFFICIALS│
    │  (Junction)  │        │  (Junction)  │         │  (Junction)  │
    ├──────────────┤        ├──────────────┤         ├──────────────┤
    │FK: match_id  │        │FK: match_id  │         │FK: match_id  │
    │FK: team_id   │        │FK: player_id │         │FK: official  │
    └──────┬───────┘        │FK: team_id   │         │   role       │
           │                └──────┬───────┘         └──────┬───────┘
           │                       │                        │
           ▼                       ▼                        ▼
    ┌──────────────┐        ┌──────────────┐         ┌──────────────┐
    │    TEAMS     │        │   PLAYERS    │         │  OFFICIALS   │
    ├──────────────┤        ├──────────────┤         ├──────────────┤
    │PK: team_id   │        │PK: player_id │         │PK: official  │
    │   name       │        │   name       │         │   name       │
    └──────────────┘        └──────────────┘         └──────────────┘


                            ┌──────────────────┐
                            │     MATCHES      │
                            └────────┬─────────┘
                                     │
                                     │ 1:M (one match, many innings)
                                     │
                                     ▼
                            ┌──────────────────┐
                            │     INNINGS      │
                            ├──────────────────┤
                            │ PK: innings_id   │
                            │ FK: match_id     │
                            │ FK: team_id      │
                            │     innings_num  │
                            │     target_runs  │
                            └────────┬─────────┘
                                     │
                                     │ 1:M (one innings, many deliveries)
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   DELIVERIES     │
                            │  (Ball-by-Ball)  │
                            ├──────────────────┤
                            │ PK: delivery_id  │
                            │ FK: innings_id   │
                            │ FK: batter_id    │───────┐
                            │ FK: bowler_id    │───────┤ (All point to PLAYERS)
                            │ FK: non_striker  │───────┘
                            │     over_number  │
                            │     ball_number  │
                            │     runs_batter  │
                            │     runs_total   │
                            │     is_wicket    │
                            └────────┬─────────┘
                                     │
                                     │ 1:0..1 (delivery may have wicket)
                                     │
                                     ▼
                            ┌──────────────────┐
                            │     WICKETS      │
                            ├──────────────────┤
                            │ PK: wicket_id    │
                            │ FK: delivery_id  │
                            │ FK: player_out   │
                            │     kind         │
                            └────────┬─────────┘
                                     │
                                     │ 1:M (wicket may have fielders)
                                     │
                                     ▼
                            ┌──────────────────┐
                            │ WICKET_FIELDERS  │
                            ├──────────────────┤
                            │ FK: wicket_id    │
                            │ FK: player_id    │
                            └──────────────────┘
"""

# ============================================================
# DATA FLOW EXAMPLE
# ============================================================

DATA_FLOW = """
┌─────────────────────────────────────────────────────────────────────────┐
│              HOW DATA FLOWS FROM JSON TO DATABASE                        │
└─────────────────────────────────────────────────────────────────────────┘

JSON FILE: match_001.json
│
├─ info.date ──────────────────────────────> MATCHES.match_date
├─ info.venue ─────────────────────────────> MATCHES.venue
├─ info.city ──────────────────────────────> MATCHES.city
├─ info.outcome.winner ────────────────────> MATCHES.outcome_winner
│
├─ info.teams[0] ──────────────────────────> TEAMS.team_name
├─ info.teams[1] ──────────────────────────> TEAMS.team_name
│                                             (if not exists, create)
│
├─ info.players.KKR[0] ────────────────────> PLAYERS.player_name
├─ info.players.KKR[1] ────────────────────> PLAYERS.player_name
│  (with registry ID)                        PLAYERS.player_id
│
├─ Link match + team ──────────────────────> MATCH_TEAMS (match_id, team_id)
├─ Link match + player + team ─────────────> MATCH_PLAYERS (match_id, player_id, team_id)
│
├─ innings[0].team ────────────────────────> INNINGS.batting_team_id
│  innings[0].overs ────────────────────────> (process each over)
│     │
│     ├─ deliveries[0].batter ─────────────> DELIVERIES.batter_id
│     ├─ deliveries[0].bowler ─────────────> DELIVERIES.bowler_id
│     ├─ deliveries[0].runs.batter ────────> DELIVERIES.runs_batter
│     ├─ deliveries[0].runs.total ─────────> DELIVERIES.runs_total
│     │
│     └─ deliveries[0].wickets[0] ─────────> WICKETS.player_out_id
│                                             WICKETS.kind
│                                             (if exists)
│
└─ Complete!
"""

# ============================================================
# EXAMPLE WITH REAL DATA
# ============================================================

EXAMPLE = """
┌─────────────────────────────────────────────────────────────────────────┐
│                    EXAMPLE: ONE MATCH IN THE DATABASE                    │
└─────────────────────────────────────────────────────────────────────────┘

JSON:
{
  "info": {
    "date": "2008-04-18",
    "venue": "M Chinnaswamy Stadium",
    "teams": ["KKR", "RCB"],
    "outcome": {"winner": "KKR"},
    "players": {
      "KKR": ["SC Ganguly", "BB McCullum"],
      "RCB": ["R Dravid", "V Kohli"]
    }
  },
  "innings": [{
    "team": "KKR",
    "overs": [{
      "deliveries": [{
        "batter": "SC Ganguly",
        "bowler": "P Kumar",
        "runs": {"batter": 0, "total": 1}
      }]
    }]
  }]
}

BECOMES:

MATCHES:
┌──────────┬────────────┬───────────┬───────────────────────┬──────────┐
│ match_id │ match_date │ city      │ venue                 │ winner   │
├──────────┼────────────┼───────────┼───────────────────────┼──────────┤
│ 1        │ 2008-04-18 │ Bangalore │ M Chinnaswamy Stadium │ KKR      │
└──────────┴────────────┴───────────┴───────────────────────┴──────────┘

TEAMS:
┌─────────┬───────────┐
│ team_id │ team_name │
├─────────┼───────────┤
│ 1       │ KKR       │
│ 2       │ RCB       │
└─────────┴───────────┘

MATCH_TEAMS:
┌──────────┬─────────┐
│ match_id │ team_id │
├──────────┼─────────┤
│ 1        │ 1       │  ← Match 1 involves KKR
│ 1        │ 2       │  ← Match 1 involves RCB
└──────────┴─────────┘

PLAYERS:
┌───────────┬──────────────┐
│ player_id │ player_name  │
├───────────┼──────────────┤
│ 725529bc  │ SC Ganguly   │
│ b8a55852  │ BB McCullum  │
│ 0184dc35  │ R Dravid     │
│ ba607b88  │ V Kohli      │
│ e938e1bc  │ P Kumar      │
└───────────┴──────────────┘

MATCH_PLAYERS:
┌──────────┬───────────┬─────────┐
│ match_id │ player_id │ team_id │
├──────────┼───────────┼─────────┤
│ 1        │ 725529bc  │ 1       │  ← Ganguly (KKR)
│ 1        │ b8a55852  │ 1       │  ← McCullum (KKR)
│ 1        │ 0184dc35  │ 2       │  ← Dravid (RCB)
│ 1        │ ba607b88  │ 2       │  ← Kohli (RCB)
│ 1        │ e938e1bc  │ 2       │  ← P Kumar (RCB)
└──────────┴───────────┴─────────┘

INNINGS:
┌────────────┬──────────┬────────────────┬─────────────────┐
│ innings_id │ match_id │ innings_number │ batting_team_id │
├────────────┼──────────┼────────────────┼─────────────────┤
│ 1          │ 1        │ 1              │ 1               │  ← KKR batting
│ 2          │ 1        │ 2              │ 2               │  ← RCB batting
└────────────┴──────────┴────────────────┴─────────────────┘

DELIVERIES:
┌─────────────┬────────────┬──────┬──────┬───────────┬───────────┬─────────────┬────────────┐
│ delivery_id │ innings_id │ over │ ball │ batter_id │ bowler_id │ runs_batter │ runs_total │
├─────────────┼────────────┼──────┼──────┼───────────┼───────────┼─────────────┼────────────┤
│ 1           │ 1          │ 0    │ 1    │ 725529bc  │ e938e1bc  │ 0           │ 1          │
│ 2           │ 1          │ 0    │ 2    │ b8a55852  │ e938e1bc  │ 0           │ 0          │
│ ...         │ ...        │ ...  │ ...  │ ...       │ ...       │ ...         │ ...        │
└─────────────┴────────────┴──────┴──────┴───────────┴───────────┴─────────────┴────────────┘
"""

# ============================================================
# QUERYING: HOW JOINS WORK
# ============================================================

JOINS = """
┌─────────────────────────────────────────────────────────────────────────┐
│                      HOW JOINS CONNECT TABLES                            │
└─────────────────────────────────────────────────────────────────────────┘

QUERY: "Find all runs scored by V Kohli"

SQL:
    SELECT p.player_name, SUM(d.runs_batter) as total_runs
    FROM deliveries d
    JOIN players p ON d.batter_id = p.player_id
    WHERE p.player_name = 'V Kohli'
    GROUP BY p.player_name;

STEP BY STEP:

1. Start with DELIVERIES table:
   ┌─────────────┬───────────┬─────────────┐
   │ delivery_id │ batter_id │ runs_batter │
   ├─────────────┼───────────┼─────────────┤
   │ 1           │ 725529bc  │ 0           │
   │ 2           │ ba607b88  │ 4           │  ← Kohli's ID
   │ 3           │ ba607b88  │ 6           │  ← Kohli's ID
   │ 4           │ 0184dc35  │ 1           │
   └─────────────┴───────────┴─────────────┘

2. JOIN with PLAYERS table (match batter_id = player_id):
   ┌─────────────┬───────────┬─────────────┬──────────────┐
   │ delivery_id │ batter_id │ runs_batter │ player_name  │
   ├─────────────┼───────────┼─────────────┼──────────────┤
   │ 1           │ 725529bc  │ 0           │ SC Ganguly   │
   │ 2           │ ba607b88  │ 4           │ V Kohli      │  ← Match!
   │ 3           │ ba607b88  │ 6           │ V Kohli      │  ← Match!
   │ 4           │ 0184dc35  │ 1           │ R Dravid     │
   └─────────────┴───────────┴─────────────┴──────────────┘

3. WHERE filters to only V Kohli:
   ┌─────────────┬───────────┬─────────────┬─────────────┐
   │ delivery_id │ batter_id │ runs_batter │ player_name │
   ├─────────────┼───────────┼─────────────┼─────────────┤
   │ 2           │ ba607b88  │ 4           │ V Kohli     │
   │ 3           │ ba607b88  │ 6           │ V Kohli     │
   └─────────────┴───────────┴─────────────┴─────────────┘

4. GROUP BY and SUM:
   ┌─────────────┬────────────┐
   │ player_name │ total_runs │
   ├─────────────┼────────────┤
   │ V Kohli     │ 10         │  (4 + 6)
   └─────────────┴────────────┘

RESULT: V Kohli scored 10 runs
"""

# ============================================================
# COMPLEX QUERY EXAMPLE
# ============================================================

COMPLEX = """
┌─────────────────────────────────────────────────────────────────────────┐
│              COMPLEX QUERY: Top 5 Players in Season 2023                 │
└─────────────────────────────────────────────────────────────────────────┘

QUERY:
    SELECT 
        p.player_name,
        SUM(d.runs_batter) as runs,
        COUNT(DISTINCT i.innings_id) as innings,
        ROUND(SUM(d.runs_batter) * 100.0 / COUNT(*), 2) as strike_rate
    FROM deliveries d
    JOIN players p ON d.batter_id = p.player_id
    JOIN innings i ON d.innings_id = i.innings_id
    JOIN matches m ON i.match_id = m.match_id
    WHERE m.season = '2023'
    GROUP BY p.player_name
    ORDER BY runs DESC
    LIMIT 5;

TABLES INVOLVED:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  DELIVERIES ─────> PLAYERS  (get player name)                │
│      │                                                        │
│      └─────────> INNINGS ─────> MATCHES  (filter by season)  │
│                                                              │
└──────────────────────────────────────────────────────────────┘

RESULT:
┌───────────────┬──────┬─────────┬──────────────┐
│ player_name   │ runs │ innings │ strike_rate  │
├───────────────┼──────┼─────────┼──────────────┤
│ F du Plessis  │ 730  │ 16      │ 153.78       │
│ S Gill        │ 890  │ 17      │ 158.20       │
│ V Kohli       │ 639  │ 15      │ 139.02       │
│ RG Sharma     │ 597  │ 16      │ 130.89       │
│ Q de Kock     │ 594  │ 15      │ 141.00       │
└───────────────┴──────┴─────────┴──────────────┘
"""

# ============================================================
# SUMMARY
# ============================================================

SUMMARY = """
┌─────────────────────────────────────────────────────────────────────────┐
│                         KEY TAKEAWAYS                                    │
└─────────────────────────────────────────────────────────────────────────┘

1. RELATIONAL DATABASE = Connected Tables
   - Each table stores ONE type of thing
   - Tables connect via keys (IDs)

2. PRIMARY KEY (PK) = Unique Identifier
   - Every row has a unique ID
   - Usually auto-incremented (1, 2, 3, ...)

3. FOREIGN KEY (FK) = Reference to Another Table
   - Points to a primary key in another table
   - Creates relationships

4. NORMALIZATION = Avoid Repetition
   - Store each piece of data once
   - Use IDs to reference it

5. JOINS = Connect Tables
   - Combine data from multiple tables
   - Match rows where keys are equal

6. JUNCTION TABLES = Many-to-Many Relationships
   - Connect two tables that both have "many"
   - Example: match_players connects matches ↔ players

┌─────────────────────────────────────────────────────────────────────────┐
│                    WHY THIS IS BETTER THAN JSON                          │
└─────────────────────────────────────────────────────────────────────────┘

❌ JSON (Flat File):
   - Repeat player names 10,000+ times
   - Hard to update player info
   - Slow to search
   - Files get massive

✅ Database:
   - Store each player once
   - Update in one place
   - Fast indexed lookups
   - Efficient storage
   - Can query across all data

┌─────────────────────────────────────────────────────────────────────────┐
│                         NEXT STEPS                                       │
└─────────────────────────────────────────────────────────────────────────┘

1. ✅ Read the tutorial (relational_database_tutorial.md)
2. ✅ Run the database builder
3. ✅ Try simple SELECT queries
4. ✅ Practice JOINs
5. ✅ Write your own queries
6. ✅ Design your own database for a project
"""

if __name__ == "__main__":
    print(SCHEMA)
    print("\n" + "="*80 + "\n")
    print(DATA_FLOW)
    print("\n" + "="*80 + "\n")
    print(EXAMPLE)
    print("\n" + "="*80 + "\n")
    print(JOINS)
    print("\n" + "="*80 + "\n")
    print(COMPLEX)
    print("\n" + "="*80 + "\n")
    print(SUMMARY)
