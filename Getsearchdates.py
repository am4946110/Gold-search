"""
Get Search Dates from Database
Retrieves all search history dates from search_results.db in human-readable format
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json
import sys


def get_all_dates(database_path="search_results.db"):
    """
    Retrieve all search dates from the database.
    
    Args:
        database_path (str): Path to the SQLite database file
    
    Returns:
        dict: Dictionary with search history and formatted dates
    """
    db_file = Path(database_path)
    
    if not db_file.exists():
        return {
            "ok": False,
            "error": f"Database file not found: {database_path}",
            "dates": []
        }
    
    try:
        connection = sqlite3.connect(str(db_file))
        cursor = connection.cursor()
        
        # Query all searches ordered by most recent first
        cursor.execute("""
            SELECT id, query, search_date, result_count 
            FROM searches 
            ORDER BY search_date DESC
        """)
        
        rows = cursor.fetchall()
        connection.close()
        
        if not rows:
            return {
                "ok": True,
                "message": "No search history found in database",
                "dates": []
            }
        
        # Format each date as human-readable
        dates_list = []
        for row in rows:
            search_id, query, search_date, result_count = row
            
            try:
                # Parse the timestamp and format it
                dt = datetime.fromisoformat(search_date)
                formatted_date = dt.strftime("%b %d, %Y at %I:%M %p")
            except (ValueError, TypeError):
                formatted_date = str(search_date)
            
            dates_list.append({
                "id": search_id,
                "query": query,
                "date": formatted_date,
                "result_count": result_count
            })
        
        return {
            "ok": True,
            "total_searches": len(dates_list),
            "dates": dates_list
        }
    
    except sqlite3.Error as error:
        return {
            "ok": False,
            "error": f"Database error: {str(error)}",
            "dates": []
        }
    except Exception as error:
        return {
            "ok": False,
            "error": f"Unexpected error: {str(error)}",
            "dates": []
        }


def print_formatted_output(result):
    """Print the results in a nice formatted table"""
    if not result.get("ok"):
        print(f"❌ Error: {result.get('error')}")
        return
    
    if not result.get("dates"):
        print("📭 No search history found")
        return
    
    print("\n" + "="*90)
    print(f"📅 Search History - Total Searches: {result['total_searches']}")
    print("="*90)
    
    for idx, item in enumerate(result["dates"], 1):
        print(f"\n{idx}. Search ID: {item['id']}")
        print(f"   Query: {item['query']}")
        print(f"   Date: {item['date']}")
        print(f"   Results: {item['result_count']} found")
    
    print("\n" + "="*90 + "\n")


def main():
    """Main entry point"""
    # Check if a database path was provided as argument
    database_path = sys.argv[1] if len(sys.argv) > 1 else "search_results.db"
    
    result = get_all_dates(database_path)
    
    # Print formatted output
    print_formatted_output(result)
    
    # Also output as JSON if requested
    if "--json" in sys.argv:
        print("\nJSON Output:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()