from flask import Flask, render_template
import sqlite3
import os
import uvicorn 

app = Flask(__name__, template_folder='templates')

# Route to render homepage
@app.route('/')
def index():
    # Get the absolute path to the directory where this script resides
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Use the absolute path to the database file
    db_path = os.path.join(base_dir, 'listings.db')

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Fetch listings from the database
    c.execute("SELECT title, PLN, EUR, listing_type, property_type, lot_size, image_src, link_to_offer FROM listings")
    listings = c.fetchall()
    conn.close()

    # Convert fetched data into a list of dictionaries
    listings = [{'title': title, 'PLN': PLN, 'EUR': EUR, 'listing_type': listing_type, 'property_type': property_type, 'lot_size': lot_size, 'image_src': image_src, 'link_to_offer': link_to_offer} for title, PLN, EUR, listing_type, property_type, lot_size, image_src, link_to_offer in listings]

    # Render homepage with listings
    return render_template('index.html', listings=listings)

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8000)

