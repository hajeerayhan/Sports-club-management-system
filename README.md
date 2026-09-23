# Sports Club Management System

A robust Python CLI application integrated with MySQL for managing sports teams, players, fixtures, and performance metrics with full relational database integrity.

---

## Key Features

- **Player Directory**: Full CRUD capabilities for player registration, profiles, team affiliation, and contact details.
- **Match Scheduling**: Schedule, track, and manage upcoming and completed fixtures with date and venue constraints.
- **Performance Analytics**: Log and evaluate individual player stats (scores, fouls, ratings) tied to specific fixtures via foreign keys.
- **Relational Integrity**: Designed with foreign keys and cascading deletes (`ON DELETE CASCADE`) to prevent orphaned data.
- **Secure Configuration**: Uses environment variables for database credentials to safeguard access.

---

## Tech Stack

- **Language**: Python 3.x
- **Database**: MySQL Server
- **Connector**: `mysql-connector-python`

---

## Database Architecture

The system uses three primary tables linked via foreign key relationships:

```text
  +------------------+          +------------------------+
  |     players      |          |        matches         |
  +------------------+          +------------------------+
  | player_id (PK)   |<----+    | match_id (PK)          |<----+
  | name             |     |    | match_name             |     |
  | age              |     |    | sport                  |     |
  | sport            |     |    | match_date             |     |
  | contact          |     |    | match_time             |     |
  | team             |     |    | venue                  |     |
  +------------------+     |    | team1, team2           |     |
                           |    +------------------------+     |
                           |                                   |
                           |    +------------------------+     |
                           |    |      performance       |     |
                           |    +------------------------+     |
                           +----| player_id (FK)         |     |
                                | match_id (FK)  --------+-----+
                                | points_scored          |
                                | assists, fouls         |
                                | rating, remarks        |
                                +------------------------+
