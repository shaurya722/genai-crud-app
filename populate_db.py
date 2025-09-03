#!/usr/bin/env python3
"""
Script to populate the test.db database with 10 dummy items.
This script uses the existing models and database configuration.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Set the database URL directly since we can't use .env file
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from models import SessionLocal
from models.items import Item

def populate_database():
    """Populate the database with 10 dummy items."""
    
    # Sample data for dummy items
    dummy_items = [
        {"name": "Laptop", "description": "High-performance gaming laptop with RTX 4080"},
        {"name": "Smartphone", "description": "Latest iPhone with 256GB storage"},
        {"name": "Headphones", "description": "Wireless noise-canceling headphones"},
        {"name": "Coffee Maker", "description": "Automatic coffee machine with timer"},
        {"name": "Backpack", "description": "Waterproof hiking backpack with multiple compartments"},
        {"name": "Watch", "description": "Smartwatch with heart rate monitor"},
        {"name": "Camera", "description": "DSLR camera with 24MP sensor"},
        {"name": "Speaker", "description": "Portable Bluetooth speaker with bass boost"},
        {"name": "Tablet", "description": "10-inch tablet with 128GB storage"},
        {"name": "Gaming Console", "description": "Next-gen gaming console with 4K support"}
    ]
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if items already exist
        existing_count = db.query(Item).count()
        print(f"Found {existing_count} existing items in the database.")
        
        if existing_count > 0:
            print("Database already contains items. Clearing existing data...")
            db.query(Item).delete()
            db.commit()
            print("Existing data cleared.")
        
        # Insert dummy items
        print("Inserting 10 dummy items...")
        for i, item_data in enumerate(dummy_items, 1):
            new_item = Item(
                name=item_data["name"],
                description=item_data["description"]
            )
            db.add(new_item)
            print(f"  {i}. Added: {item_data['name']}")
        
        # Commit all changes
        db.commit()
        print(f"\nSuccessfully inserted {len(dummy_items)} items into the database!")
        
        # Verify the insertion
        total_items = db.query(Item).count()
        print(f"Total items in database: {total_items}")
        
        # Display all items
        print("\nAll items in the database:")
        print("-" * 50)
        items = db.query(Item).all()
        for item in items:
            print(f"ID: {item.id}, Name: {item.name}, Description: {item.description}")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting database population...")
    populate_database()
    print("\nDatabase population completed!") 