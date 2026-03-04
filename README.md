# RE/MAX Astra Warsaw -- Automated Real Estate Listings Website

This project is a fully automated static website for the RE/MAX Astra
real estate office in Warsaw.

The system automatically scrapes live property listings from the
official RE/MAX website, stores them in a database, and generates a
static website that is updated daily.

The goal of the project was to eliminate manual listing updates and
ensure the website always reflects the current inventory of the office.

------------------------------------------------------------------------

## Problem

Small real estate offices often maintain listings on external platforms
while their own websites require manual updates.

This leads to:

-   outdated listings
-   duplicate work
-   human errors
-   slow content updates

------------------------------------------------------------------------

## Solution

This project implements a fully automated pipeline:

1.  Listings are scraped from the official RE/MAX office page.
2.  Data is stored in a SQLite database.
3.  A static website is generated from the database.
4.  The site is automatically deployed using GitHub Actions.

As a result, the website always displays current listings without manual
intervention.

------------------------------------------------------------------------

## Automation pipeline

Nightly GitHub Actions workflow ↓ Scraper (Selenium + headless Chrome) ↓
SQLite database (listings.db) ↓ Static site generator (Jinja2 templates)
↓ Static HTML website deployment

The pipeline runs once per day and updates the website automatically.

------------------------------------------------------------------------

## Scraper

The scraper uses Selenium with a headless Chrome browser to extract
property listings from the official RE/MAX listings page.

For each property it collects:

-   title
-   price (PLN / EUR)
-   listing type
-   property type
-   living area
-   image
-   link to the detailed offer

The scraper also handles:

-   cookie consent dialogs
-   dynamic page loading
-   pagination across multiple result pages

------------------------------------------------------------------------

## Static site generation

A Python script reads the listings from SQLite and generates a static
website using Jinja2 templates.

The generated site includes:

-   property listing cards
-   marketing content for the office
-   a careers page with a GDPR-compliant application form via Formspree

Because the site is static, it can be hosted cheaply on any static
hosting provider.

------------------------------------------------------------------------

## Tech stack

Python\
Selenium (headless Chrome)\
SQLite\
Jinja2 templates\
GitHub Actions (scheduled automation)

Frontend runtime:

HTML / CSS / JavaScript\
Bootstrap and UI plugins

------------------------------------------------------------------------

## Result

The final website updates automatically once per day.

This eliminates manual listing updates while keeping hosting costs
minimal and runtime infrastructure simple.

------------------------------------------------------------------------

## Running locally

Install dependencies:

pip install selenium webdriver-manager jinja2

Run the scraper:

python scrapingscript.py

Generate the static site:

python generate_static_site.py

Preview locally:

python -m http.server 8000

Open:

http://localhost:8000/index.html


