# Simple Inventory

> A barebones tool for logging the low-volume sale of things in a way that is only maybe a little better than using a spreadsheet (but at least will be more consistent).

I built this for a relative's small medical practice, which needed to replace an old Microsoft Works database. The functionality here is decidedly built-to-purpose, supporting existing, largely paper-based workflows.

## Development

This is built with Python 3, Flask, and Flask-Admin, among other things.

To develop this project:

1. Clone the repository:

    ```python
    git clone https://github.com/gassc/simple-inventory.git
    cd simple-inventory
    ```

2. Create and activate a virtual environment:

    ```python
    python -m venv ENV
    # *nix:
    source env/bin/activate
    # windows
    ENV\Scripts\activate
    ```

3. Install requirements:

    pip install -r requirements.txt

4. Run the application:

    ```
    python run.py
    ```
