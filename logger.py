# logger.py

import logging
from utility.db import DBHelper
import datetime as dt

db_helper = DBHelper("crawlerDb")



def log_to_db(level, message):
    project_name = "adin_project"
    timestamp = dt.datetime.now()
    sql_script = '''INSERT INTO log_messages (timestamp, level, message, project_name) VALUES (%s, %s, %s, %s)'''
    values = (timestamp, level, message, project_name)
                   
    db_helper.execute(sql_script,values)