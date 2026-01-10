# Understanding Relational Databases: IPL Cricket Example

## 📚 Table of Contents
1. [What is a Relational Database?](#what-is-a-relational-database)
2. [Key Concepts](#key-concepts)
3. [Why Use Multiple Tables?](#why-use-multiple-tables)
4. [Designing Your Database](#designing-your-database)
5. [Step-by-Step: From JSON to Database](#step-by-step-from-json-to-database)
6. [Hands-On Practice](#hands-on-practice)

---

## What is a Relational Database?

A **relational database** stores data in **tables** that are **related** to each other.

### Simple Analogy
Think of it like organizing a library:
- One shelf for **books** (title, author, ISBN)
- One shelf for **authors** (name, birth year, country)
- One shelf for **borrowers** (name, ID, phone)
- One shelf for **loans** (who borrowed which book, when)

Instead of writing the author's full information on every book, you just write their ID and look them up when needed.

### Database vs Spreadsheet

**Spreadsheet** (flat data):
```
| Match Date | Team 1 | Team 2 | Winner | Player 1 | Player 2 | Player 3 | ... |
|------------|--------|--------|--------|----------|----------|----------|-----|
| 2008-04-18 | KKR    | RCB    | KKR    | Ganguly  | McCullum | Ponting  | ... |
```

**Problems:**
- Lots of repetition (same player names over and over)
- Hard to update (if you fix a typo, you must fix it everywhere)
- Limited columns (what if a team has 15 players?)
- Can't easily answer "Which teams did Virat Kohli play for?"

**Relational Database** (connected tables):
```
MATCHES table:          PLAYERS table:           MATCH_PLAYERS table:
| match_id | date     | | player_id | name    |  | match_id | player_id |
|----------|----------|  |-----------|---------|  |----------|-----------|
| 1        | 2008-... | | p1        | Ganguly |  | 1        | p1        |
                         | p2        | McCullum|  | 1        | p2        |
                         | p3        | Ponting |  | 1        | p3        |
```

**Benefits:**
✓ Each player stored once
✓ Easy to update
✓ No limit on players per match
✓ Easy to query "all matches for player X"

---

## Key Concepts

### 1. **Primary Key (PK)**
A **unique identifier** for each row in a table.

```sql
CREATE TABLE players (
    player_id TEXT PRIMARY KEY,  -- This is the primary key
    player_name TEXT
);
```

Examples:
- `player_id` for players table
- `match_id` for matches table
- `delivery_id` for deliveries table

**Rules:**
- Must be unique (no duplicates)
- Cannot be NULL (empty)
- Usually a number or code

### 2. **Foreign Key (FK)**
A column that **references** a primary key in another table, creating a relationship.

```sql
CREATE TABLE deliveries (
    delivery_id INTEGER PRIMARY KEY,
    batter_id TEXT,  -- This is a foreign key
    FOREIGN KEY (batter_id) REFERENCES players(player_id)
);
```

This says: "Every `batter_id` in deliveries must exist in the players table"

### 3. **Relationships**

#### One-to-Many (1:M)
One record in Table A relates to many records in Table B.

Example: **One match** has **many deliveries**
```
MATCHES                    DELIVERIES
match_id=1  ─────────┐    match_id=1, delivery_id=1
                     ├───> match_id=1, delivery_id=2
                     ├───> match_id=1, delivery_id=3
                     └───> match_id=1, delivery_id=4
```

#### Many-to-Many (M:M)
Many records in Table A relate to many records in Table B.

Example: **Many matches** have **many players**, and **many players** play in **many matches**

This requires a **junction table**:
```
MATCHES          MATCH_PLAYERS          PLAYERS
match_id=1 ────> match_id=1, player_id=p1 <──── player_id=p1
                 match_id=1, player_id=p2 <──── player_id=p2
match_id=2 ────> match_id=2, player_id=p1 <──┘
                 match_id=2, player_id=p3 <──── player_id=p3
```

### 4. **Normalization**
The process of organizing data to **reduce redundancy** (repetition) and **improve data integrity**.

**Bad (Denormalized):**
```
| match_id | team_name | team_city | team_owner |
|----------|-----------|-----------|------------|
| 1        | KKR       | Kolkata   | Shah Rukh  |
| 2        | KKR       | Kolkata   | Shah Rukh  | ← Repeated data!
| 3        | MI        | Mumbai    | Ambani     |
```

**Good (Normalized):**
```
MATCHES table:               TEAMS table:
| match_id | team_id |       | team_id | name | city    | owner     |
|----------|---------|       |---------|------|---------|-----------|
| 1        | t1      |       | t1      | KKR  | Kolkata | Shah Rukh |
| 2        | t1      | ────> | t2      | MI   | Mumbai  | Ambani    |
| 3        | t2      |
```

Benefits:
- Update team info in ONE place
- No wasted space
- No inconsistencies (e.g., "KKR" vs "Kolkata Knight Riders")

---

## Why Use Multiple Tables?

Let's analyze your IPL JSON data to see why we need multiple tables.

### Your JSON Structure:
```json
{
  "info": {
    "city": "Bangalore",
    "teams": ["RCB", "KKR"],
    "players": {
      "KKR": ["Ganguly", "McCullum", "Ponting"],
      "RCB": ["Dravid", "Kohli", "Kallis"]
    },
    "officials": {
      "umpires": ["Asad Rauf", "RE Koertzen"]
    }
  },
  "innings": [
    {
      "team": "KKR",
      "overs": [
        {
          "deliveries": [
            {
              "batter": "Ganguly",
              "bowler": "P Kumar",
              "runs": {"batter": 0, "total": 1}
            }
          ]
        }
      ]
    }
  ]
}
```

### Problems with Storing This as One Table:

1. **Repetition**: Player names repeated thousands of times
2. **Complexity**: How many columns for players? (teams have different squad sizes)
3. **Updates**: Change player name = update thousands of rows
4. **Queries**: "Find all matches for Virat Kohli" becomes very slow

### Solution: Split into Related Tables

```
┌─────────────┐
│   MATCHES   │  ← Core match info (date, venue, winner)
└──────┬──────┘
       │
       ├──────> TEAMS (team names)
       │
       ├──────> PLAYERS (player names + IDs)
       │
       ├──────> MATCH_PLAYERS (which players in which match)
       │
       ├──────> OFFICIALS (umpire names)
       │
       └──────> INNINGS
                   │
                   └──────> DELIVERIES (ball-by-ball)
                               │
                               └──────> WICKETS
```

---

## Designing Your Database

### Step 1: Identify Entities
**Entities** are the "things" in your data that deserve their own table.

From IPL JSON:
- ✅ **Match** (each game)
- ✅ **Team** (KKR, MI, CSK, etc.)
- ✅ **Player** (Ganguly, Kohli, etc.)
- ✅ **Official** (umpires, referees)
- ✅ **Innings** (each batting turn)
- ✅ **Delivery** (each ball bowled)
- ✅ **Wicket** (each dismissal)

### Step 2: Identify Attributes
**Attributes** are the properties of each entity.

**Match:**
- match_id (PK)
- date
- city
- venue
- winner
- toss_winner
- season

**Player:**
- player_id (PK)
- player_name

**Delivery:**
- delivery_id (PK)
- innings_id (FK)
- batter_id (FK)
- bowler_id (FK)
- runs_batter
- runs_total

### Step 3: Identify Relationships

1. **Match ↔ Team** (Many-to-Many)
   - One match has two teams
   - One team plays in many matches
   - **Junction table**: `match_teams`

2. **Match ↔ Player** (Many-to-Many)
   - One match has many players
   - One player plays in many matches
   - **Junction table**: `match_players`

3. **Match → Innings** (One-to-Many)
   - One match has 1-2 innings
   - One innings belongs to one match

4. **Innings → Deliveries** (One-to-Many)
   - One innings has many deliveries
   - One delivery belongs to one innings

5. **Delivery → Wicket** (One-to-One or One-to-Zero)
   - One delivery may have one wicket
   - One wicket belongs to one delivery

### Step 4: Draw the Schema (ERD)

```
┌──────────────┐         ┌──────────────┐
│   MATCHES    │─────────│ MATCH_TEAMS  │──────┐
│ PK: match_id │         │ FK: match_id │      │
│    date      │         │ FK: team_id  │      │
│    venue     │         └──────────────┘      │
│    winner    │                               │
└──────┬───────┘                               │
       │                                       │
       │ 1:M                              ┌────▼────┐
       │                                  │  TEAMS  │
       ▼                                  │ PK: id  │
┌──────────────┐                          │  name   │
│   INNINGS    │                          └─────────┘
│ PK: id       │
│ FK: match_id │
│ FK: team_id  │
└──────┬───────┘
       │ 1:M
       ▼
┌──────────────┐         ┌──────────────┐
│  DELIVERIES  │────────>│   PLAYERS    │
│ PK: id       │         │ PK: id       │
│ FK: inns_id  │         │    name      │
│ FK: batter   │─────┐   └──────────────┘
│ FK: bowler   │─────┘
│    runs      │
└──────┬───────┘
       │ 1:0..1
       ▼
┌──────────────┐
│   WICKETS    │
│ PK: id       │
│ FK: del_id   │
│ FK: player   │
│    kind      │
└──────────────┘
```

---

## Step-by-Step: From JSON to Database

Let me walk you through how the code transforms your JSON into the database.

### Example: Processing One Match

**Input JSON:**
```json
{
  "info": {
    "city": "Bangalore",
    "venue": "M Chinnaswamy Stadium",
    "dates": ["2008-04-18"],
    "teams": ["KKR", "RCB"],
    "players": {
      "KKR": ["SC Ganguly", "BB McCullum"],
      "RCB": ["R Dravid", "V Kohli"]
    },
    "registry": {
      "people": {
        "SC Ganguly": "725529bc",
        "BB McCullum": "b8a55852"
      }
    }
  },
  "innings": [...]
}
```

### Step 1: Create Match Record

```python
# Extract match info
match_date = info['dates'][0]  # "2008-04-18"
venue = info['venue']           # "M Chinnaswamy Stadium"
city = info['city']             # "Bangalore"

# Insert into matches table
cursor.execute('''
    INSERT INTO matches (match_date, venue, city, ...)
    VALUES (?, ?, ?, ...)
''', (match_date, venue, city, ...))

match_id = cursor.lastrowid  # Get auto-generated ID (e.g., 1)
```

**Result in MATCHES table:**
```
| match_id | match_date | city      | venue                      |
|----------|------------|-----------|----------------------------|
| 1        | 2008-04-18 | Bangalore | M Chinnaswamy Stadium      |
```

### Step 2: Process Teams

```python
for team_name in info['teams']:  # ["KKR", "RCB"]
    # Check if team exists
    cursor.execute('SELECT team_id FROM teams WHERE team_name = ?', (team_name,))
    result = cursor.fetchone()
    
    if result:
        team_id = result[0]  # Team already exists
    else:
        # Create new team
        cursor.execute('INSERT INTO teams (team_name) VALUES (?)', (team_name,))
        team_id = cursor.lastrowid
    
    # Link match to team
    cursor.execute('''
        INSERT INTO match_teams (match_id, team_id)
        VALUES (?, ?)
    ''', (match_id, team_id))
```

**Result in TEAMS table:**
```
| team_id | team_name |
|---------|-----------|
| 1       | KKR       |
| 2       | RCB       |
```

**Result in MATCH_TEAMS table:**
```
| match_id | team_id |
|----------|---------|
| 1        | 1       |  ← Match 1 has team KKR
| 1        | 2       |  ← Match 1 has team RCB
```

### Step 3: Process Players

```python
registry = info['registry']['people']

# Insert all players from registry
for player_name, player_id in registry.items():
    cursor.execute('''
        INSERT OR IGNORE INTO players (player_id, player_name)
        VALUES (?, ?)
    ''', (player_id, player_name))

# Link players to match and team
for team_name, player_names in info['players'].items():
    team_id = get_team_id(team_name)
    
    for player_name in player_names:
        player_id = registry[player_name]
        cursor.execute('''
            INSERT INTO match_players (match_id, player_id, team_id)
            VALUES (?, ?, ?)
        ''', (match_id, player_id, team_id))
```

**Result in PLAYERS table:**
```
| player_id | player_name  |
|-----------|--------------|
| 725529bc  | SC Ganguly   |
| b8a55852  | BB McCullum  |
| 0184dc35  | R Dravid     |
| ba607b88  | V Kohli      |
```

**Result in MATCH_PLAYERS table:**
```
| match_id | player_id | team_id |
|----------|-----------|---------|
| 1        | 725529bc  | 1       |  ← Ganguly played for KKR in match 1
| 1        | b8a55852  | 1       |  ← McCullum played for KKR in match 1
| 1        | 0184dc35  | 2       |  ← Dravid played for RCB in match 1
| 1        | ba607b88  | 2       |  ← Kohli played for RCB in match 1
```

### Step 4: Process Innings

```python
for innings_num, innings_data in enumerate(data['innings'], 1):
    batting_team = innings_data['team']
    team_id = get_team_id(batting_team)
    
    cursor.execute('''
        INSERT INTO innings (match_id, innings_number, batting_team_id)
        VALUES (?, ?, ?)
    ''', (match_id, innings_num, team_id))
    
    innings_id = cursor.lastrowid
```

**Result in INNINGS table:**
```
| innings_id | match_id | innings_number | batting_team_id |
|------------|----------|----------------|-----------------|
| 1          | 1        | 1              | 1               |  ← KKR batting
| 2          | 1        | 2              | 2               |  ← RCB batting
```

### Step 5: Process Deliveries

```python
for over_data in innings_data['overs']:
    over_num = over_data['over']
    
    for ball_num, delivery in enumerate(over_data['deliveries'], 1):
        batter = delivery['batter']
        bowler = delivery['bowler']
        runs = delivery['runs']
        
        batter_id = registry[batter]
        bowler_id = registry[bowler]
        
        cursor.execute('''
            INSERT INTO deliveries (
                innings_id, over_number, ball_number,
                batter_id, bowler_id, runs_batter, runs_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (innings_id, over_num, ball_num, 
              batter_id, bowler_id, runs['batter'], runs['total']))
        
        delivery_id = cursor.lastrowid
```

**Result in DELIVERIES table:**
```
| delivery_id | innings_id | over | ball | batter_id | bowler_id | runs_batter | runs_total |
|-------------|------------|------|------|-----------|-----------|-------------|------------|
| 1           | 1          | 0    | 1    | 725529bc  | e938e1bc  | 0           | 1          |
| 2           | 1          | 0    | 2    | b8a55852  | e938e1bc  | 0           | 0          |
| 3           | 1          | 0    | 3    | b8a55852  | e938e1bc  | 0           | 1          |
```

### Step 6: Process Wickets

```python
if 'wickets' in delivery:
    for wicket in delivery['wickets']:
        player_out = wicket['player_out']
        player_out_id = registry[player_out]
        kind = wicket['kind']
        
        cursor.execute('''
            INSERT INTO wickets (delivery_id, player_out_id, kind)
            VALUES (?, ?, ?)
        ''', (delivery_id, player_out_id, kind))
        
        wicket_id = cursor.lastrowid
        
        # Process fielders
        for fielder in wicket.get('fielders', []):
            fielder_id = registry[fielder['name']]
            cursor.execute('''
                INSERT INTO wicket_fielders (wicket_id, player_id)
                VALUES (?, ?)
            ''', (wicket_id, fielder_id))
```

**Result in WICKETS table:**
```
| wicket_id | delivery_id | player_out_id | kind   |
|-----------|-------------|---------------|--------|
| 1         | 45          | 725529bc      | caught |
```

**Result in WICKET_FIELDERS table:**
```
| wicket_id | player_id |
|-----------|-----------|
| 1         | 86dc8f2e  |  ← Kallis caught Ganguly
```

---

## Hands-On Practice

### Exercise 1: Design a Simple Database

Design a database for a **school**:
- Students (name, ID, grade)
- Teachers (name, ID, subject)
- Classes (subject, time)
- Enrollments (which students in which classes)

**Questions:**
1. Which tables do you need?
2. What are the primary keys?
3. What relationships exist?
4. Draw the schema

<details>
<summary>Click for Solution</summary>

**Tables:**
```sql
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name TEXT,
    grade INTEGER
);

CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY,
    name TEXT,
    subject TEXT
);

CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY,
    subject TEXT,
    time TEXT,
    teacher_id INTEGER,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);

CREATE TABLE enrollments (
    student_id INTEGER,
    class_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    PRIMARY KEY (student_id, class_id)
);
```

**Relationships:**
- Teacher → Classes (1:M) - one teacher teaches many classes
- Class ↔ Students (M:M) - through enrollments junction table
</details>

### Exercise 2: Normalize Bad Data

This table has redundancy:
```
| order_id | customer_name | customer_email   | product    | price |
|----------|---------------|------------------|------------|-------|
| 1        | John Smith    | john@email.com   | Laptop     | 1000  |
| 2        | John Smith    | john@email.com   | Mouse      | 20    |
| 3        | Jane Doe      | jane@email.com   | Keyboard   | 50    |
```

**Task:** Split into normalized tables

<details>
<summary>Click for Solution</summary>

```sql
-- Customers table
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);

-- Products table
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL
);

-- Orders table
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

**Data:**
```
CUSTOMERS:
| customer_id | name       | email            |
|-------------|------------|------------------|
| 1           | John Smith | john@email.com   |
| 2           | Jane Doe   | jane@email.com   |

PRODUCTS:
| product_id | name     | price |
|------------|----------|-------|
| 1          | Laptop   | 1000  |
| 2          | Mouse    | 20    |
| 3          | Keyboard | 50    |

ORDERS:
| order_id | customer_id | product_id |
|----------|-------------|------------|
| 1        | 1           | 1          |
| 2        | 1           | 2          |
| 3        | 2           | 3          |
```
</details>

### Exercise 3: Write Queries

Using the IPL database, write SQL to answer:

1. Count total matches
2. List all teams
3. Find players who played for KKR
4. Calculate total runs scored by a player
5. Find all matches at a specific venue

<details>
<summary>Click for Solutions</summary>

```sql
-- 1. Count total matches
SELECT COUNT(*) FROM matches;

-- 2. List all teams
SELECT team_name FROM teams ORDER BY team_name;

-- 3. Players who played for KKR
SELECT DISTINCT p.player_name
FROM players p
JOIN match_players mp ON p.player_id = mp.player_id
JOIN teams t ON mp.team_id = t.team_id
WHERE t.team_name = 'Kolkata Knight Riders';

-- 4. Total runs by a player
SELECT p.player_name, SUM(d.runs_batter) as total_runs
FROM deliveries d
JOIN players p ON d.batter_id = p.player_id
WHERE p.player_name = 'V Kohli'
GROUP BY p.player_name;

-- 5. Matches at specific venue
SELECT match_date, outcome_winner
FROM matches
WHERE venue = 'M Chinnaswamy Stadium'
ORDER BY match_date;
```
</details>

---

## Summary: Why Relational Databases?

### ✅ Benefits
1. **No Redundancy** - Each piece of data stored once
2. **Data Integrity** - Foreign keys prevent orphan records
3. **Flexibility** - Easy to add new relationships
4. **Performance** - Indexed lookups are fast
5. **Scalability** - Handles millions of records
6. **Easy Updates** - Change data in one place

### ⚖️ Trade-offs
1. **Complexity** - Need to understand JOINs
2. **Setup Time** - More initial design work
3. **Query Performance** - JOINs can be slow on huge datasets

### 🎯 When to Use
- Data has relationships (customers → orders → products)
- Need to avoid duplication
- Data will be updated frequently
- Multiple users/applications access the same data
- Need transaction safety (banking, e-commerce)

### 🚫 When NOT to Use
- Very simple data (just a list)
- No relationships
- Read-only data that never changes
- Need extreme performance (consider NoSQL)

---

## Next Steps

1. ✅ Run the IPL database builder
2. ✅ Explore the tables with `SELECT * FROM table_name`
3. ✅ Try the example queries
4. ✅ Write your own queries
5. ✅ Design a database for your own project
6. ✅ Learn about indexes and optimization
7. ✅ Explore database visualization tools

**Recommended Tools:**
- **DB Browser for SQLite** - Visual database browser
- **DBeaver** - Universal database tool
- **SQLite Online** - Practice in your browser

Happy learning! 🎓📊
