import http.client
import json
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

headers = {
    "X-API-KEY": "25eebc1810a1c4c92ad09dd1d5ef7499ca216576",
    "Content-Type": "application/json"
}

# Database configuration
DB_PATH = "search_results.db"


class SearchDatabase:
    """SQLite database manager for search results"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create searches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result_count INTEGER
                )
            ''')
            
            # Create results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER NOT NULL,
                    title TEXT,
                    link TEXT UNIQUE,
                    snippet TEXT,
                    rank INTEGER,
                    FOREIGN KEY (search_id) REFERENCES searches(id) ON DELETE CASCADE
                )
            ''')
            
            # Create index for faster searches
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_query 
                ON searches(query)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_title 
                ON results(title)
            ''')
            
            conn.commit()
    
    def save_search(self, query, results):
        """Save search query and results to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert search query
            cursor.execute('''
                INSERT INTO searches (query, result_count)
                VALUES (?, ?)
            ''', (query, len(results)))
            
            search_id = cursor.lastrowid
            
            # Insert results
            for rank, result in enumerate(results, start=1):
                try:
                    cursor.execute('''
                        INSERT INTO results (search_id, title, link, snippet, rank)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        search_id,
                        result.get("title", ""),
                        result.get("link", ""),
                        result.get("snippet", ""),
                        rank
                    ))
                except sqlite3.IntegrityError:
                    # Skip duplicate links
                    pass
            
            conn.commit()
            return search_id
    
    def search_database(self, query, search_type="title"):
        """Search stored results in database
        
        Args:
            query: Search term
            search_type: 'title', 'snippet', or 'all'
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if search_type == "title":
                cursor.execute('''
                    SELECT results.*, searches.query as original_query
                    FROM results
                    JOIN searches ON results.search_id = searches.id
                    WHERE results.title LIKE ?
                    ORDER BY results.rank
                ''', (f"%{query}%",))
            
            elif search_type == "snippet":
                cursor.execute('''
                    SELECT results.*, searches.query as original_query
                    FROM results
                    JOIN searches ON results.search_id = searches.id
                    WHERE results.snippet LIKE ?
                    ORDER BY results.rank
                ''', (f"%{query}%",))
            
            else:  # search_type == "all"
                cursor.execute('''
                    SELECT results.*, searches.query as original_query
                    FROM results
                    JOIN searches ON results.search_id = searches.id
                    WHERE results.title LIKE ? OR results.snippet LIKE ?
                    ORDER BY results.rank
                ''', (f"%{query}%", f"%{query}%"))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_search_history(self, limit=20):
        """Get recent searches"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, query, search_date, result_count
                FROM searches
                ORDER BY search_date DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self):
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM searches")
            total_searches = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM results")
            total_results = cursor.fetchone()[0]
            
            return {
                "total_searches": total_searches,
                "total_results": total_results
            }


def search_google(query):
    """Search using Google Serper API"""
    connection = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query,
        "gl": "eg"
    })

    connection.request("POST", "/search", payload, headers)
    response = connection.getresponse()
    data = response.read().decode("utf-8")
    connection.close()

    return response.status, data


def shorten(text, width):
    """Shorten text to specified width"""
    text = " ".join(str(text or "").split())
    if len(text) <= width:
        return text.ljust(width)
    return text[:width - 3] + "..."


def print_table(results):
    """Print results in table format"""
    columns = [
        ("#", 3),
        ("Title", 35),
        ("Link", 45),
        ("Snippet", 55),
    ]
    separator = "+".join("-" * (width + 2) for _, width in columns)
    header = "|".join(f" {name.ljust(width)} " for name, width in columns)

    print(separator)
    print(header)
    print(separator)

    for index, result in enumerate(results, start=1):
        row = [
            str(index),
            result.get("title", ""),
            result.get("link", ""),
            result.get("snippet", ""),
        ]
        print("|".join(f" {shorten(value, width)} " for value, (_, width) in zip(row, columns)))

    print(separator)


def format_results(data):
    """Extract organic results from API response"""
    results = json.loads(data)
    return results.get("organic", [])


def run_search(query, db, as_json=False):
    """Execute Google search and save to database"""
    status, data = search_google(query)

    if status != 200:
        if as_json:
            print(json.dumps({
                "ok": False,
                "status": status,
                "error": data,
                "results": [],
            }))
        else:
            print(f"Error: HTTP {status}")
            print(data)
        return 1

    organic_results = format_results(data)
    
    # Save to database
    db.save_search(query, organic_results)

    if as_json:
        print(json.dumps({
            "ok": True,
            "status": status,
            "query": query,
            "results": organic_results,
        }))
        return 0

    if not organic_results:
        print("No results found.")
        return 0

    print_table(organic_results)
    return 0


def show_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("SEARCH APPLICATION WITH DATABASE")
    print("="*60)
    print("1. Search Google (and save to database)")
    print("2. Search Database by Title")
    print("3. Search Database by Snippet")
    print("4. Search Database (Title + Snippet)")
    print("5. View Search History")
    print("6. View Database Statistics")
    print("7. Exit")
    print("="*60)


def search_db_menu(db):
    """Interactive database search menu"""
    while True:
        show_menu()
        choice = input("Select option (1-7): ").strip()

        if choice == "1":
            query = input("Enter search query: ").strip().lstrip("\ufeff")
            if query:
                run_search(query, db)

        elif choice == "2":
            query = input("Enter title search: ").strip().lstrip("\ufeff")
            if query:
                results = db.search_database(query, search_type="title")
                if results:
                    print(f"\nFound {len(results)} results:")
                    print_table(results)
                else:
                    print("No results found.")

        elif choice == "3":
            query = input("Enter snippet search: ").strip().lstrip("\ufeff")
            if query:
                results = db.search_database(query, search_type="snippet")
                if results:
                    print(f"\nFound {len(results)} results:")
                    print_table(results)
                else:
                    print("No results found.")

        elif choice == "4":
            query = input("Enter search term: ").strip().lstrip("\ufeff")
            if query:
                results = db.search_database(query, search_type="all")
                if results:
                    print(f"\nFound {len(results)} results:")
                    print_table(results)
                else:
                    print("No results found.")

        elif choice == "5":
            history = db.get_search_history(limit=20)
            if history:
                print("\n" + "="*80)
                print(f"{'ID':<5} {'Query':<30} {'Date':<20} {'Results':<10}")
                print("="*80)
                for record in history:
                    print(f"{record['id']:<5} {record['query']:<30} {record['search_date']:<20} {record['result_count']:<10}")
                print("="*80)
            else:
                print("No search history found.")

        elif choice == "6":
            stats = db.get_stats()
            print("\n" + "="*60)
            print("DATABASE STATISTICS")
            print("="*60)
            print(f"Total Searches: {stats['total_searches']}")
            print(f"Total Stored Results: {stats['total_results']}")
            print(f"Database File: {DB_PATH}")
            print("="*60)

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")


def main():
    """Main entry point"""
    db = SearchDatabase()
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip().lstrip("\ufeff")
        return run_search(query, db, as_json=True)

    search_db_menu(db)


if __name__ == "__main__":
    raise SystemExit(main())