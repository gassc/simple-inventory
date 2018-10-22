# Simple Inventory

This is a simple tool for managing a product inventory: record purchased inventory, manage suppliers, view available stock, record sales, view analytics. It uses a bunch of a off-the-shelf software; the result is something that:

* is better than using a spreadsheet;
* is a lot less confusing than building/maintaining an something like an MS Access database;
* provides consistency and promise.

I built this for a relative's small medical practice, which needed to replace an old _Microsoft Works_ database. The functionality here is decidedly built-to-purpose, supporting existing, largely paper-based workflows.

## Software

This is built with Python 3, Python-Flask, and Flask-Admin. The database is SQLite. It uses Twitter Bootstrap v3 for the GUI, and Chart.js for the charts in the analytics view.

## Development Quickstart

To develop this project:

1.  Clone the repository:

    ```python
    git clone https://github.com/gassc/simple-inventory.git
    cd simple-inventory
    ```

2.  Create and activate a virtual environment:

    `python -m venv ENV`

    *bash*
    
    ```sh
    source env/bin/activate
    ```

    
    *windows*
    ```ps
    ENV\Scripts\activate
    ```

3.  Install requirements:

    pip install -r requirements.txt
    
4.  Create the database (initial set-up only)

    `python db_setup.py`

5.  Run the application:

    Using the Flask development server, in browser: `python run.py`
    
    As a PyWebView Desktop application: `python launch.py`


# Deployment (and Disclaimer)

My use case is absurdly simple and probably not useful for most folks: for me this needs to run on one computer used by a couple of people and give the appeareance of a desktop application. It is not exposed to the internet, and so lacks any security features in that regard (logins, protection from CSRF, etc). 

[PyWebView](https://github.com/r0x0r/pywebview) does the trick of making this run as a desktop application.

# To-Do

The [Issues list](https://github.com/gassc/simple-inventory/issues) provides an overview of what's in store for this. Notably, [issue 8](https://github.com/gassc/simple-inventory/issues/8) will provide some important missing functionality for any inventory software.
