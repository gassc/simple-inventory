
# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import time
import sqlite3
import logging
import operator
import json
import datetime
from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import FetchedValue
from jinja2 import Markup
from wtforms import validators
import petl as etl
from dateutil.parser import parse

import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from flask_admin import BaseView, expose

# ----------------------------------------------------------------------------
# Application Setup
# ----------------------------------------------------------------------------

# Create application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# setup logging for SQLAlchemy
if app.config['SQLALCHEMY_LOGGING']:
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def format_currency(view, context, model, name):
    # print("{0} - {1}".format(name, model.__dict__[name]))
    v = model.__dict__[name]
    # print(v)
    if v is not None:
        return Markup("${:,.2f}".format(v))
    else:
        return Markup("$---")


def format_date(date_string, strf_string='%Y-%m-%d', replace_nonetype_with="00-00-0000"):
    # if date_string is None:
    #     print(date_string, type(date_string))
    #     return replace_nonetype_with
    # else:
    dt = parse(date_string)
    return dt.strftime(strf_string)


def calculate_profit(rec, assume_quantity=1):
    """give a record created from a join of Sales and Product data, return profit.
    If no price information is available, returns zero. If no quantity information is available,
    uses the assume_quantity parameter (default = 1)

    Arguments:
        rec {dict} -- a record created from a join of Sales and Product data
        assume_quantity {int} -- number to use if quantity (from sale) is empty. defaults to 1

    Returns:
        gross profit from the sale, as a float
    """

    # print(rec['id'], rec['quantity'], rec['special_price'],
    #       rec['list_price'], rec['sold_price'])

    # determine quantity
    if not rec['quantity']:
        q = assume_quantity
    else:
        q = rec['quantity']
    # calculate profit
    if rec['special_price']:
        return round(((rec['special_price'] - rec['list_price']) * q), 2)
    elif rec['sold_price']:
        return round(((rec['sold_price'] - rec['list_price']) * q), 2)
    elif 'list_price' in rec:
        return 0
    else:
        return 0

    return 0


def calculate_gross_sales(rec, assume_quantity=1):
    """give a record created from a join of Sales and Product data, return gross sales.
    If no price information is available, returns zero. If no quantity information is available,
    uses the assume_quantity parameter (default = 1)

    Arguments:
        rec {dict} -- a record created from a join of Sales and Product data
        assume_quantity {int} -- number to use if quantity (from sale) is empty. defaults to 1

    Returns:
        gross profit from the sale, as a float
    """

    # print(rec['id'], rec['quantity'], rec['special_price'],
    #       rec['list_price'], rec['sold_price'])
    # determine quantity
    if not rec['quantity']:
        q = assume_quantity
    else:
        q = rec['quantity']
    # calculate profit
    if rec['special_price']:
        return round((rec['special_price'] * q), 2)
    elif rec['sold_price']:
        return round((rec['sold_price'] * q), 2)
    elif 'list_price' in rec:
        return round((rec['list_price'] * q), 2)
    else:
        return 0


def handle_none(v, replace_with=1):
    if v is None:
        return replace_with
    else:
        return v


def export_data(table):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    outpath = os.path.join(dir_path, 'static', 'data', "sales.csv")

    etl.tocsv(table, outpath)


def sales_summary(start_dt=None, end_dt=None, staff_id=None, for_export=False):
    """tally up gross (sale over list) profits
    TODO: tally up net profites (gross profit vs inventory purchase total)

    TODO: Keyword Arguments:
        start_dt {[type]} -- datetime for start of query (default: {None})
        end_dt {[type]} -- datetime for start of query [description] (default: {None})

    Returns:
        [dict] -- various types of sales information, stored in a dictionary.
    """

    # products = db.session.query(Product).all()
    # sales = db.session.query(Sale).all()

    # retrieve existing tables
    products_records = etl.fromdb(db.engine, 'SELECT * FROM product')
    sales_records = etl.fromdb(db.engine, 'SELECT * FROM sale')
    staff_records = etl.fromdb(db.engine, 'SELECT * FROM staff')
    
    # filter by start/end date if provided
    if start_dt and end_dt:
        sales_records = etl\
            .selectnotnone(sales_records, 'date')\
            .select(lambda r: r.date > start_dt and r.date <= end_dt)
    elif start_dt and not end_dt:
        sales_records = etl\
            .selectnotnone(sales_records, 'date')\
            .select(lambda r: r.date > start_dt)
    elif end_dt and not start_dt:
        sales_records = etl\
            .selectnotnone(sales_records, 'date')\
            .select(lambda r: r.date <= end_dt)
    else:
        pass
    
    # filter by staff id if provided
    if staff_id:
        sales_records = etl.select(sales_records, 'staff_id', lambda v: v == staff_id)

    # join product info to sales data
    sales_data = etl\
        .join(
            sales_records,
            products_records,
            lkey='product_id', 
            rkey='id'
        )\
        .leftjoin(
            staff_records,
            lkey='staff_id',
            rkey='id'
        )
            

    # prep joined sales data for tabulation
    sales_data = etl\
        .convert(sales_data, 'date', lambda dt: format_date(dt))\
        .sort('date')\
        .convert('quantity', lambda q: handle_none(q, replace_with=1))\
        .addfield('profit', lambda rec: calculate_profit(rec))\
        .addfield('gross_sales', lambda rec: calculate_gross_sales(rec))
        
    # tabulate some figures
    gross_sales = 0
    profits = 0
    for sale in etl.dicts(sales_data):
        profits += calculate_profit(sale)
        gross_sales += calculate_gross_sales(sale)

    if for_export:
        return {
            'gross_sales': gross_sales,
            'profits': profits, 
            'table': sales_data
        }       

    export_data(sales_data)

    # summarize data into charting-friendly data structures
    chart_count, chart_count_missing_date = etl\
        .fold(sales_data, 'date', operator.add, 'quantity', presorted=True)\
        .rename({'key': 'x', 'value': 'y'})\
        .biselect(lambda rec: rec.x is not None)
        
    # print(chart_count)
    # etl.lookall(chart_count)

    chart_gross, chart_gross_missing_date = etl\
        .fold(sales_data, 'date', operator.add,'gross_sales', presorted=True)\
        .rename({'key': 'x', 'value': 'y'})\
        .biselect(lambda rec: rec.x is not None)

    # print(chart_gross)
    # etl.lookall(chart_gross)

    chart_profit, chart_profit_missing_date = etl\
        .fold(sales_data, 'date', operator.add, 'profit', presorted=True)\
        .rename({'key': 'x', 'value': 'y'})\
        .biselect(lambda rec: rec.x is not None)



    # for i in etl.dicts(chart_count):
    #     print(i)
    # for i in etl.dicts(chart_gross):
    #     print(i)
    
    return {
        'gross_sales': gross_sales,
        'profits': profits,
        'chart_gross': list(etl.dicts(chart_gross)),
        'chart_gross_missing_date': list(etl.dicts(chart_gross_missing_date)),
        'chart_profit': list(etl.dicts(chart_profit)),
        'chart_profit_missing_date': list(etl.dicts(chart_profit_missing_date)),
        'chart_count': list(etl.dicts(chart_count)),
        'chart_count_missing_date': list(etl.dicts(chart_count_missing_date))
    }


# ----------------------------------------------------------------------------
# Models and corresponding custom Flask-Admin view classes
# ----------------------------------------------------------------------------

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    contact = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String)
    notes = db.Column(db.Text)

    def __str__(self):
        return self.name


class SupplierView(ModelView):
    column_searchable_list = ('name', 'contact', 'email', 'phone', 'notes')
    action_disallowed_list = ['delete']
    column_exclude_list = ['notes']
    form_excluded_columns = ['suppliers']
    can_export = True
    can_delete = False


product_tags_table = db.Table(
    'product_tags',
    db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # descriptive fields
    code = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255), unique=True)
    quantity_per_unit = db.Column(db.Integer)
    list_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    description = db.Column(db.Text)
    discontinued = db.Column(db.Boolean())

    # REF: Supplier (brand) table
    supplier_id = db.Column(db.Integer(), db.ForeignKey(Supplier.id))
    supplier = db.relationship(Supplier, backref='suppliers')

    # auto-completed from database trigger (concatentates several fields)
    fullname = db.Column(
        db.String(1000),
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )

    # intial amount; managed in a separate form
    initial_volume = db.Column(db.Integer)

    # REF: tags table
    tags = db.relationship('Tag', secondary=product_tags_table)

    def __str__(self):
        return self.fullname


class ProductView(ModelView):
    column_formatters = {
        'list_price': format_currency,
        'selling_price': format_currency
    }
    column_searchable_list = ('name', Supplier.name,
                              'tags.name', 'fullname', 'code')
    column_exclude_list = ['description', 'initial_volume', 'fullname']
    column_editable_list = ['tags']
    action_disallowed_list = ['delete']
    page_size = 100
    form_excluded_columns = ['products', 'fullname']
    can_export = True
    can_delete = False


'''
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey(Product.id))
    units_purchased = db.Column(db.Integer, default=1)
    use_list_price = db.Column(db.Boolean(), default=False)
    special_price = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    notes = db.Column(db.Text)

    def __str__(self):
        return self.units_purchased


class Inventory(db.Model):
    """Inventory is a table populated by triggers fired in the Order and Sales tables.
    While directly editable, it should only need to be set-up once--for the initial
    inventory--and the triggers will handle the rest. Its primary purpose is to show
    how many items are left in stock
    """
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey(Product.id))
    notes = db.Column(db.Text)

    # in stock = initial volume - volume sold + volume replaced
    # in_stock is used to set an initial volume during table setup
    in_stock = db.Column(
        db.Integer,
        default=0,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )

    # total replaced = *deincremented* from Order table entries
    volume_replaced = db.Column(
        db.Integer,
        default=0,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )

    # total sold = *incremented* from Sale table entries
    volume_sold = db.Column(
        db.Integer,
        default=0,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )

    def __str__(self):
        return self.in_stock
'''


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    def __str__(self):
        return self.name


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __str__(self):
        return self.name


'''
class StaffView(ModelView):
    column_searchable_list = ('name')
    action_disallowed_list = ['delete']
'''


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    special_price = db.Column(db.Float)
    use_list_price = db.Column(db.Boolean(), default=False)
    notes = db.Column(db.Text)
    product_id = db.Column(db.Integer(), db.ForeignKey(Product.id))
    product = db.relationship(Product, backref='products')
    staff_id = db.Column(db.Integer(), db.ForeignKey(Staff.id))
    staff = db.relationship(Staff, backref='staff')
    sold_price = db.Column(db.Float)

    def __str__(self):
        return self.product


class SaleView(ModelView):
    column_formatters = {
        'special_price': format_currency,
        'sold_price': format_currency
    }
    column_searchable_list = (Product.fullname, Product.code, 'date')
    column_exclude_list = ['notes', 'special_price',
                           'fullname', 'use_list_price']
    form_excluded_columns = ['sold_price']
    can_export = True


# ----------------------------------------------------------------------------
# Custom view classes (uses Flask-Admin template but not derived from table)
# ----------------------------------------------------------------------------

class InventoryView(BaseView):
    @expose('/')
    def index(self):
        return self.render('pages/inventory.html')


class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        summary = sales_summary()
        print(summary['chart_gross_missing_date'])
        return self.render(
            'pages/analytics.html',
            summaryChartData=json.dumps(summary),
            gross_sales="${:,.2f}".format(summary['gross_sales']),
            profits="${:,.2f}".format(summary['profits']),
            chart_gross_missing_date=summary['chart_gross_missing_date'][0]['y'],
            chart_profit_missing_date=summary['chart_profit_missing_date'][0]['y'],
            chart_count_missing_date=summary['chart_count_missing_date'][0]['y']
        )

# ----------------------------------------------------------------------------
# Flask Views
# ----------------------------------------------------------------------------

# root route


@app.route('/')
def index():
    # return redirect("/admin/", code=302)
    # return "<h1><a href='/admin/'>View Inventory</a></h1>"
    return render_template('/pages/index.html')


# Create admin
admin = admin.Admin(
    app,
    name="{0} | {1}".format(app.config['ORG_NAME'], app.config['APP_TITLE']),
    template_mode='bootstrap3'
)

# Add model views
admin.add_view(SaleView(Sale, db.session))
admin.add_view(SupplierView(Supplier, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Staff, db.session))
# add custom views
admin.add_view(InventoryView(name='Inventory', endpoint='inventory'))
admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
