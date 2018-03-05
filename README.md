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

    ```python
    python -m venv ENV
    # *nix:
    source env/bin/activate
    # windows
    ENV\Scripts\activate
    ```

3.  Install requirements:

    pip install -r requirements.txt

4.  Run the application:

    ```
    python run.py
    ```
