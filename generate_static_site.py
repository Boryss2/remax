#!/usr/bin/env python3
"""
Script to generate static HTML site from SQLite database for GitHub Pages deployment.
This script reads the listings from the database and generates a static HTML file.
"""

import sqlite3
import os
from jinja2 import Template

def generate_static_site():
    """Generate static HTML site from database."""
    
    # Connect to SQLite database
    db_path = 'listings.db'
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Fetch listings from the database
    c.execute("SELECT title, PLN, EUR, listing_type, property_type, lot_size, image_src, link_to_offer FROM listings")
    listings = c.fetchall()
    conn.close()
    
    # Convert fetched data into a list of dictionaries
    listings_data = []
    for listing in listings:
        title, PLN, EUR, listing_type, property_type, lot_size, image_src, link_to_offer = listing
        listings_data.append({
            'title': title,
            'PLN': PLN,
            'EUR': EUR,
            'listing_type': listing_type,
            'property_type': property_type,
            'lot_size': lot_size,
            'image_src': image_src,
            'link_to_offer': link_to_offer
        })
    
    # Read the HTML template
    template_path = 'templates/index.html'
    if not os.path.exists(template_path):
        print(f"Template file {template_path} not found!")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create Jinja2 template
    template = Template(template_content)
    
    # Render the template with listings data
    rendered_html = template.render(listings=listings_data)
    
    # Write the rendered HTML to index.html in the root directory
    output_path = 'index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    
    print(f"Static site generated successfully: {output_path}")
    print(f"Number of listings processed: {len(listings_data)}")
    
    return True

if __name__ == '__main__':
    success = generate_static_site()
    if not success:
        exit(1)
