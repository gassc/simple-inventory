
# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import time
import sqlite3
import logging
import operator
import json
from flask import Flask, redirect, render_template
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
    #print("{0} - {1}".format(name, model.__dict__[name]))
    v = model.__dict__[name]
    print(v)
    if v is not None:
        return Markup("${:,.2f}".format(v))
    else:
        return Markup("$---")

def format_date(date_string, strf_string='%Y-%m-%d'):
    dt = parse(date_string)
    return dt.strftime(strf_string)

def calculate_profit(rec):
    if rec['special_price']:
        return round(((rec['special_price'] - rec['list_price']) * rec['quantity']),2)
    elif rec['sold_price']:
        return round(((rec['sold_price'] - rec['list_price']) * rec['quantity']),2)
    elif 'list_price' in rec:
        return round((rec['list_price'] * rec['quantity']),2)
    else:
        return 0

def sales_summary():
    """tally up gross (sale over list) and net (gross vs purchased) profits
    """
    # products = db.session.query(Product).all()
    # sales = db.session.query(Sale).all()

    # process the existing tables
    products_records = etl.fromdb(db.engine,'SELECT * FROM product')
    sales_records = etl.fromdb(db.engine,'SELECT * FROM sale')
    sales_data = etl.join(sales_records, products_records, lkey='product_id', rkey='id')
    sales_data = etl.convert(sales_data, 'date', lambda dt: format_date(dt))
    sales_data = etl.addfield(sales_data, 'gross_profit', lambda rec: calculate_profit(rec))
    sales_data = etl.sort(sales_data, 'date')

    # summarize data
    chart_count = etl.fold(sales_data, 'date', operator.add, 'quantity', presorted=True)
    chart_count = etl.rename(chart_count, {
        'key': 'x', 'value': 'y'
    })
    # print(chart_count)
    chart_gross = etl.fold(sales_data, 'date', operator.add, 'gross_profit', presorted=True)
    chart_gross = etl.rename(chart_gross, {
        'key': 'x', 'value': 'y'
    })
    # print(chart_gross)

    gross_sales = 0
    for sale in etl.dicts(sales_data):
        gross_sales += calculate_profit(sale)
        # if special price
        # if sale['special_price']:
        #     gross_sales += (sale['special_price'] - sale['list_price']) * sale['quantity']
        # elif sale['sold_price']:
        #     gross_sales += (sale['sold_price'] - sale['list_price']) * sale['quantity']
        # else:
        #     gross_sales += sale['list_price'] * sale['quantity']
    
    return {
        'gross_sales': gross_sales, 
        'chart_gross': list(etl.dicts(chart_gross)), 
        'chart_count': list(etl.dicts(chart_count))
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

# Create M2M table
product_tags_table = db.Table(
    'product_tags',
    db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

# Create models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # descriptive fields
    code = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255), unique=True)
    quantity_per_unit = db.Column(db.Integer)
    list_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    description = db.Column(db.Text)

    # REF: Supplier (brand) table
    supplier_id = db.Column(db.Integer(), db.ForeignKey(Supplier.id))
    supplier = db.relationship(Supplier, backref='suppliers')

    # auto-completed from database trigger (concatentates several fields)
    fullname = db.Column(
        db.String(1000),
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )
    
    # VOLUME ------------------------------------------------------------
    
    # intial amount; managed in a separate form
    initial_volume = db.Column(
        db.Integer,
        default=0,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )
    
    # total replaced = *incremented* from a separate form
    volume_replaced = db.Column(
        db.Integer,
        default=0,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )                                
    
    # auto-completed via triggers in the SALES table
    ## total sold = tally of sales from sales table
    volume_sold = db.Column(
        db.Integer,
        default=0,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )
    # in stock = initial volume - volume sold + volume replaced
    in_stock = db.Column(
        db.Integer,
        default=0,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue()
    )
    
    # REF: tags table
    tags = db.relationship('Tag', secondary=product_tags_table)
    
    discontinued = db.Column(db.Boolean())

    def __str__(self):
        return self.fullname
    
class ProductView(ModelView):
    column_formatters = {
        'list_price': format_currency,
        'selling_price': format_currency
    }
    column_searchable_list = ('name', Supplier.name, 'tags.name', 'fullname','code')
    column_exclude_list = ['description','initial_volume', 'volume_replaced', 'fullname']
    column_editable_list = ['tags']
    action_disallowed_list = ['delete']
    page_size = 25
    form_excluded_columns = ['products', 'fullname','volume_replaced','volume_sold', 'in_stock']

class InventoryView(BaseView):
    @expose('/')
    def index(self):
        return self.render('custom/inventory_view.html')
    '''
    column_searchable_list = ('name', Supplier.name, 'fullname','code')
    column_include_list = [Supplier.name, 'code', 'name', 'initial_volume', 'volume_replaced', 'volume_sold', 'in_stock']
    action_disallowed_list = ['delete','create','update']
    page_size = 25
    can_create = False
    can_edit = False
    can_delete = False
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
    quantity = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    special_price = db.Column(db.Float)
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
    column_exclude_list = ['notes','special_price', 'fullname']
    form_excluded_columns = ['sold_price']

'''
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey(Product.id))
    product = db.relationship(Product, backref='products_2_inventory')
    initial_volume = db.Column(db.Integer)
    volume_sold = db.Column(db.Integer)
    volume_replaced = db.Column(db.Integer)
    in_stock = db.Column(db.Integer)
    notes = db.Column(db.Text)
    def __str__(self):
        return self.in_stock
'''

# ----------------------------------------------------------------------------
# Flask Views
# ----------------------------------------------------------------------------

# root route
@app.route('/')
def index():
    return redirect("/admin/", code=302)

@app.route('/reports')
def reports():
    summary = sales_summary()
    return render_template('pages/summary.html', summaryChartData=json.dumps(summary))

# Create admin
admin = admin.Admin(
    app,
    name="{0} | {1}".format(app.config['ORG_NAME'], app.config['APP_TITLE']),
    template_mode='bootstrap3'
)

# Add views
admin.add_view(SaleView(Sale, db.session))
admin.add_view(SupplierView(Supplier, db.session))
admin.add_view(ProductView(Product, db.session))
#admin.add_view(InventoryView(name='Inventory', endpoint='inventory'))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Staff, db.session))
