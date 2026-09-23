import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database configuration: uses environment variable if available, else fallback
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = "sports_db"


class SportsManagementSystem:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect_database(self):
        """Connect to MySQL database or create it if missing"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print("Successfully connected to MySQL database.")
                self.create_tables()
                return True
        except Error as e:
            print(f"Error connecting to database '{DB_NAME}': {e}")
            print("\nAttempting to initialize database...")
            if self.create_database():
                return self.connect_database()
            return False

    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            temp_conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print(f"Database '{DB_NAME}' verified/created successfully.")
            temp_cursor.close()
            temp_conn.close()
            return True
        except Error as e:
            print(f"Error creating database: {e}")
            return False

    def create_tables(self):
        """Create necessary tables with relational integrity"""
        try:
            # Players table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT,
                    sport VARCHAR(50),
                    team VARCHAR(100),
                    contact VARCHAR(15)
                )
            """)

            # Matches table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id INT AUTO_INCREMENT PRIMARY KEY,
                    match_name VARCHAR(100) NOT NULL,
                    sport VARCHAR(50),
                    match_date DATE,
                    match_time TIME,
                    venue VARCHAR(100),
                    team1 VARCHAR(100),
                    team2 VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'Scheduled'
                )
            """)

            # Performance table (Associative table with Foreign Keys)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance (
                    performance_id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT,
                    match_id INT,
                    points_scored INT DEFAULT 0,
                    assists INT DEFAULT 0,
                    fouls INT DEFAULT 0,
                    rating DECIMAL(3, 1),
                    remarks TEXT,
                    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
                    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE
                )
            """)

            self.connection.commit()
            print("Tables verified/created successfully.")
        except Error as e:
            print(f"Error creating tables: {e}")

    def display_menu(self):
        """Display main menu"""
        print("\n" + "=" * 50)
        print("           SPORTS MANAGEMENT SYSTEM")
        print("=" * 50)
        print("\n--- PLAYER REGISTRATION ---")
        print("1. Register New Player")
        print("2. View All Players")
        print("3. Update Player Information")
        print("4. Delete Player")

        print("\n--- MATCH SCHEDULING ---")
        print("5. Schedule New Match")
        print("6. View All Matches")
        print("7. Update Match Details")
        print("8. Delete Match")

        print("\n--- PERFORMANCE TRACKING ---")
        print("9. Add Performance Record")
        print("10. View Player Performance")
        print("11. View Match Performance")
        print("12. Update Performance Record")

        print("\n--- OTHER OPTIONS ---")
        print("13. Search Player by Name")
        print("14. View Upcoming Matches")
        print("0. Exit")
        print("=" * 50)

    # ------------------ PLAYER REGISTRATION FUNCTIONS ------------------
    def register_player(self):
        """Register a new player (player_id is auto-generated)"""
        print("\n--- REGISTER NEW PLAYER ---")
        name = input("Enter player name: ").strip()
        try:
            age = int(input("Enter age: "))
        except ValueError:
            print("Invalid age. Must be a number.")
            return

        sport = input("Enter sport: ").strip()
        team = input("Enter team name: ").strip()
        contact = input("Enter contact number: ").strip()

        try:
            query = """
                INSERT INTO players (name, age, sport, team, contact)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (name, age, sport, team, contact)
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Player '{name}' registered successfully! (Assigned ID: {self.cursor.lastrowid})")
        except Error as e:
            print(f"Error registering player: {e}")
            self.connection.rollback()

    def view_all_players(self):
        """View all registered players(contact before Team)"""
        print("\n--- ALL REGISTERED PLAYERS ---")
        try:
            self.cursor.execute("SELECT player_id, name, age, sport, contact, team FROM players")
            players = self.cursor.fetchall()
            if players:
                print(f"\n{'ID':<5} {'Name':<20} {'Age':<5} {'Sport':<15} {'Contact':<15} {'Team':<20}")
                print("-" * 80)
                for p in players:
                    print(f"{p[0]:<5} {p[1]:<20} {p[2]:<5} {p[3]:<15} {p[4]:<15} {p[5]:<20}")
            else:
                print("No players registered yet.")
        except Error as e:
            print(f"Error fetching players: {e}")

    def update_player(self):
        """Update player details using parameterized queries"""
        try:
            player_id = int(input("\nEnter Player ID to update: "))
            print("\nWhat would you like to update?")
            print("1. Name\n2. Age\n3. Sport\n4. Team\n5. Contact")
            choice = input("Enter choice (1-5): ").strip()

            field_map = {
                '1': ('name', str),
                '2': ('age', int),
                '3': ('sport', str),
                '4': ('team', str),
                '5': ('contact', str)
            }

            if choice in field_map:
                col_name, col_type = field_map[choice]
                raw_val = input(f"Enter new {col_name}: ").strip()
                new_value = col_type(raw_val)

                query = f"UPDATE players SET {col_name} = %s WHERE player_id = %s"
                self.cursor.execute(query, (new_value, player_id))
                self.connection.commit()

                if self.cursor.rowcount > 0:
                    print("Player information updated successfully!")
                else:
                    print("No player found with that ID.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input format.")
        except Error as e:
            print(f"Error updating player: {e}")
            self.connection.rollback()

    def delete_player(self):
        """Delete player and cascade linked performances"""
        try:
            player_id = int(input("\nEnter Player ID to delete: "))
            confirm = input("Are you sure? This will delete linked performance records (yes/no): ").lower().strip()

            if confirm == 'yes':
                self.cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
                self.connection.commit()
                if self.cursor.rowcount > 0:
                    print("Player deleted successfully!")
                else:
                    print("No player found with that ID.")
        except ValueError:
            print("Invalid ID format.")
        except Error as e:
            print(f"Error deleting player: {e}")
            self.connection.rollback()

    # ------------------ MATCH SCHEDULING FUNCTIONS ------------------
    def schedule_match(self):
        """Schedule a new match"""
        print("\n--- SCHEDULE NEW MATCH ---")
        match_name = input("Enter match name: ").strip()
        sport = input("Enter sport: ").strip()
        match_date = input("Enter match date (YYYY-MM-DD): ").strip()
        match_time = input("Enter match time (HH:MM:SS): ").strip()
        venue = input("Enter venue: ").strip()
        team1 = input("Enter team 1 name: ").strip()
        team2 = input("Enter team 2 name: ").strip()

        try:
            query = """
                INSERT INTO matches (match_name, sport, match_date, match_time, venue, team1, team2)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (match_name, sport, match_date, match_time, venue, team1, team2)
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Match scheduled successfully! (ID: {self.cursor.lastrowid})")
        except Error as e:
            print(f"Error scheduling match: {e}")
            self.connection.rollback()

    def view_all_matches(self):
        """View all matches"""
        print("\n--- ALL SCHEDULED MATCHES ---")
        try:
            self.cursor.execute("SELECT * FROM matches")
            matches = self.cursor.fetchall()
            if matches:
                print(f"\n{'ID':<5} {'Match Name':<25} {'Sport':<15} {'Date':<12} {'Time':<10} {'Venue':<20} {'Status':<12}")
                print("-" * 105)
                for m in matches:
                    print(f"{m[0]:<5} {m[1]:<25} {m[2]:<15} {str(m[3]):<12} {str(m[4]):<10} {m[5]:<20} {m[8]:<12}")
                    print(f"      Teams: {m[6]} vs {m[7]}")
            else:
                print("No matches scheduled yet.")
        except Error as e:
            print(f"Error fetching matches: {e}")

    def update_match(self):
        """Update match status or details"""
        try:
            match_id = int(input("\nEnter Match ID to update: "))
            print("\nWhat would you like to update?")
            print("1. Match Name\n2. Match Date\n3. Match Time\n4. Venue\n5. Status")
            choice = input("Enter choice (1-5): ").strip()

            field_map = {
                '1': 'match_name',
                '2': 'match_date',
                '3': 'match_time',
                '4': 'venue',
                '5': 'status'
            }

            if choice in field_map:
                col_name = field_map[choice]
                new_value = input(f"Enter new {col_name}: ").strip()

                query = f"UPDATE matches SET {col_name} = %s WHERE match_id = %s"
                self.cursor.execute(query, (new_value, match_id))
                self.connection.commit()

                if self.cursor.rowcount > 0:
                    print("Match information updated successfully!")
                else:
                    print("No match found with that ID.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input format.")
        except Error as e:
            print(f"Error updating match: {e}")
            self.connection.rollback()

    def delete_match(self):
        """Delete a scheduled match"""
        try:
            match_id = int(input("\nEnter Match ID to delete: "))
            confirm = input("Are you sure? (yes/no): ").lower().strip()
            if confirm == 'yes':
                self.cursor.execute("DELETE FROM matches WHERE match_id = %s", (match_id,))
                self.connection.commit()
                if self.cursor.rowcount > 0:
                    print("Match deleted successfully!")
                else:
                    print("No match found with that ID.")
        except ValueError:
            print("Invalid ID format.")
        except Error as e:
            print(f"Error deleting match: {e}")
            self.connection.rollback()

    # ------------------ PERFORMANCE TRACKING FUNCTIONS ------------------
    def add_performance(self):
        """Add individual player match statistics"""
        print("\n--- ADD PERFORMANCE RECORD ---")
        try:
            player_id = int(input("Enter Player ID: "))
            match_id = int(input("Enter Match ID: "))
            points = int(input("Enter points scored: "))
            assists = int(input("Enter assists: "))
            fouls = int(input("Enter fouls: "))
            rating = float(input("Enter rating (0.0 - 10.0): "))
            remarks = input("Enter remarks: ").strip()

            query = """
                INSERT INTO performance (player_id, match_id, points_scored, assists, fouls, rating, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (player_id, match_id, points, assists, fouls, rating, remarks)
            self.cursor.execute(query, values)
            self.connection.commit()
            print("Performance record added successfully!")
        except ValueError:
            print("Invalid numeric input. Please check numbers/ratings.")
        except Error as e:
            print(f"Error adding performance: {e}")
            self.connection.rollback()

    def view_player_performance(self):
        """View complete stats for a specific player using SQL JOIN"""
        try:
            player_id = int(input("\nEnter Player ID: "))
            query = """
                SELECT p.name, m.match_name, m.match_date, 
                       perf.points_scored, perf.assists, perf.fouls, perf.rating, perf.remarks
                FROM performance perf
                JOIN players p ON perf.player_id = p.player_id
                JOIN matches m ON perf.match_id = m.match_id
                WHERE perf.player_id = %s
                ORDER BY m.match_date DESC
            """
            self.cursor.execute(query, (player_id,))
            records = self.cursor.fetchall()

            if records:
                print(f"\n--- PERFORMANCE RECORDS FOR {records[0][0].upper()} ---")
                for r in records:
                    print(f"Match: {r[1]} | Date: {r[2]}")
                    print(f"Points: {r[3]} | Assists: {r[4]} | Fouls: {r[5]} | Rating: {r[6]}")
                    print(f"Remarks: {r[7]}")
                    print("-" * 40)
            else:
                print("No performance records found for this player.")
        except ValueError:
            print("Invalid Player ID format.")
        except Error as e:
            print(f"Error fetching performance: {e}")

    def view_match_performance(self):
        """View all player stats in a given match using SQL JOIN"""
        try:
            match_id = int(input("\nEnter Match ID: "))
            query = """
                SELECT p.name, perf.points_scored, perf.assists, perf.fouls, perf.rating, perf.remarks
                FROM performance perf
                JOIN players p ON perf.player_id = p.player_id
                WHERE perf.match_id = %s
            """
            self.cursor.execute(query, (match_id,))
            records = self.cursor.fetchall()

            if records:
                print(f"\n{'Player':<20} {'Points':<8} {'Assists':<8} {'Fouls':<8} {'Rating':<8} {'Remarks':<20}")
                print("-" * 75)
                for r in records:
                    print(f"{r[0]:<20} {r[1]:<8} {r[2]:<8} {r[3]:<8} {r[4]:<8} {r[5]:<20}")
            else:
                print("No performance records found for this match.")
        except ValueError:
            print("Invalid Match ID format.")
        except Error as e:
            print(f"Error fetching match performance: {e}")

    def update_performance(self):
        """Update a specific performance row"""
        try:
            perf_id = int(input("\nEnter Performance ID to update: "))
            print("\nWhat would you like to update?")
            print("1. Points Scored\n2. Assists\n3. Fouls\n4. Rating\n5. Remarks")
            choice = input("Enter choice (1-5): ").strip()

            field_map = {
                '1': ('points_scored', int),
                '2': ('assists', int),
                '3': ('fouls', int),
                '4': ('rating', float),
                '5': ('remarks', str)
            }

            if choice in field_map:
                col_name, col_type = field_map[choice]
                raw_val = input(f"Enter new {col_name}: ").strip()
                new_value = col_type(raw_val)

                query = f"UPDATE performance SET {col_name} = %s WHERE performance_id = %s"
                self.cursor.execute(query, (new_value, perf_id))
                self.connection.commit()

                if self.cursor.rowcount > 0:
                    print("Performance record updated successfully!")
                else:
                    print("No record found with that Performance ID.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid numeric input.")
        except Error as e:
            print(f"Error updating performance: {e}")
            self.connection.rollback()

    # ------------------ UTILITY / SEARCH FUNCTIONS ------------------
    def search_player(self):
        """Search player by substring using SQL LIKE"""
        name = input("\nEnter player name to search: ").strip()
        try:
            query = "SELECT player_id, name, age, sport, team FROM players WHERE name LIKE %s"
            self.cursor.execute(query, (f"%{name}%",))
            players = self.cursor.fetchall()

            if players:
                print(f"\n{'ID':<5} {'Name':<20} {'Age':<5} {'Sport':<15} {'Team':<15}")
                print("-" * 65)
                for p in players:
                    print(f"{p[0]:<5} {p[1]:<20} {p[2]:<5} {p[3]:<15} {p[4]:<15}")
            else:
                print("No players found matching that name.")
        except Error as e:
            print(f"Error searching player: {e}")

    def view_upcoming_matches(self):
        """Fetch matches occurring on or after current date"""
        try:
            query = """
                SELECT match_id, match_name, sport, match_date, match_time, venue, team1, team2 
                FROM matches 
                WHERE match_date >= CURDATE() 
                ORDER BY match_date, match_time
            """
            self.cursor.execute(query)
            matches = self.cursor.fetchall()

            if matches:
                print("\n--- UPCOMING MATCHES ---")
                for m in matches:
                    print(f"Match [{m[0]}]: {m[1]} ({m[2]})")
                    print(f"Date: {m[3]} | Time: {m[4]} | Venue: {m[5]}")
                    print(f"Teams: {m[6]} vs {m[7]}")
                    print("-" * 40)
            else:
                print("No upcoming matches scheduled.")
        except Error as e:
            print(f"Error fetching upcoming matches: {e}")

    def close_connection(self):
        """Close cursor and database connection safely"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("\nDatabase connection closed.")


def main():
    print("Starting Sports Management System...")
    system = SportsManagementSystem()
    if not system.connect_database():
        print("Failed to initialize database. Exiting.")
        return

    while True:
        try:
            system.display_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == '1':
                system.register_player()
            elif choice == '2':
                system.view_all_players()
            elif choice == '3':
                system.update_player()
            elif choice == '4':
                system.delete_player()
            elif choice == '5':
                system.schedule_match()
            elif choice == '6':
                system.view_all_matches()
            elif choice == '7':
                system.update_match()
            elif choice == '8':
                system.delete_match()
            elif choice == '9':
                system.add_performance()
            elif choice == '10':
                system.view_player_performance()
            elif choice == '11':
                system.view_match_performance()
            elif choice == '12':
                system.update_performance()
            elif choice == '13':
                system.search_player()
            elif choice == '14':
                system.view_upcoming_matches()
            elif choice == '0':
                print("\nExiting system...")
                system.close_connection()
                print("Thank you for using Sports Management System!")
                break
            else:
                print("Invalid choice! Please enter a number between 0 and 14.")
        except KeyboardInterrupt:
            print("\nSession interrupted. Closing...")
            system.close_connection()
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()