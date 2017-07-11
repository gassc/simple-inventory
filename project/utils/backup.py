import os
import sqlite3
import petl as etl
import click
import zipfile
import time

## Import zlib for zip file compression if available
try:
	import zlib
	compression = zipfile.ZIP_DEFLATED
except:
	compression = zipfile.ZIP_STORED

def timestamp():
	"""return current date/time as a string: "yyyymmddHHMMSS"
	"""
	return time.strftime("%Y%m%d_%H%M%S", time.localtime())

@click.command()
@click.argument('sqlite_db')
@click.argument('backup_path')
def run_backup(sqlite_db, backup_path):
    """backs-up each table in the inventory database to a csv,
    zips them all up, and saves the zip with a timestamp-derived name.
    """
    ts = timestamp()
    
    # SET UP THE FOLDERS -----------------------------------------------------

    #check for backup folder, make if it doesn't exist
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
    
    #make a folder for this backup
    this_backup_path = os.path.join(backup_path, "backup_{0}".format(ts))
    if not os.path.exists(this_backup_path):
        os.makedirs(this_backup_path)
    click.echo(this_backup_path)
    
    # GET THE DATA OUT -------------------------------------------------------
    
    # temporarily store extracted csv files. (use this to delete them later)
    csvs = []
    
    # connect to the DB, get each table, save out as a csv.
    conn = sqlite3.connect(sqlite_db)
    for table in ['product','product_tags','sale','staff','supplier','tag']:
        t = etl.fromdb(
            lambda: conn.cursor(), """SELECT * FROM {0}""".format(table)
        )
        out_csv = os.path.join(this_backup_path,'{0}.csv'.format(table))
        etl.tocsv(t, out_csv)
        csvs.append(out_csv)
    
    
    # ZIP THE DATA UP --------------------------------------------------------
        
    # make a zip file in the main backup location
    zipfile_directory = os.path.join(
        backup_path,
        "inventory_backup_{0}.zip".format(ts)
    )
    # create a zip file object
    zf = zipfile.ZipFile(zipfile_directory, mode="w")
    
    for each in csvs:
        click.echo(each)
        zf.write(
            filename=each,
            arcname=os.path.basename(each),
            compress_type=compression
        )
    zf.close()
    
    # REMOVE TEMP FILES -------------------------------------------------------
    
    for each in csvs:
        os.remove(each)
    os.rmdir(this_backup_path)
    
if __name__ == '__main__':
    run_backup()