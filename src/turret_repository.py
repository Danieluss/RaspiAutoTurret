import mysql.connector
import logging
from datetime import *

insert_detection_sql = """
INSERT INTO turret_detections
    (date, pos_x, pos_y, x, y)
VALUES
    (%s, %s, %s, %s, %s)
"""

create_detection_table_sql = """
create table if not exists turret_detections (
    id INTEGER NOT NULL AUTO_INCREMENT,
    date DATETIME,
    pos_x DOUBLE, pos_y DOUBLE,
    x DOUBLE, y DOUBLE,
    PRIMARY KEY(id) );
"""

class Repository:
    def __init__(self, host, user, password, cooldown_time):
        self.cooldown_timestamp = None
        self.cooldown_time = timedelta(seconds=cooldown_time)
        self.mydb = mysql.connector.connect(
          host=host,
          user=user,
          passwd=password,
          database="turretdb"
        )
        logging.info('connected to mysql at: {}'.format(host))
        self.cursor = self.mydb.cursor()
        logging.info('retrieved cursor from db')
        self.cursor.execute(create_detection_table_sql)
        
    def insert_detection(self, pos_x, pos_y, x, y):
        if self.cooldown_timestamp is None or datetime.now() > self.cooldown_timestamp:
            self.cooldown_timestamp = datetime.now() + self.cooldown_time
            logging.info('inserting detection data to db {} {} {} {}'.format(pos_x, pos_y, x, y))
            self.cursor.execute(insert_detection_sql, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), float(pos_x), float(pos_y), float(x), float(y)))
            self.mydb.commit()
