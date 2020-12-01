import sys
from flask import abort
import pymysql as mysql
from config import OPENAPI_AUTOGEN_DIR, DB_HOST, DB_USER, DB_PASSWD, DB_NAME

sys.path.append(OPENAPI_AUTOGEN_DIR)
from openapi_server import models

def db_cursor():
    return mysql.connect(host=DB_HOST,user=DB_USER,passwd=DB_PASSWD,db=DB_NAME).cursor()

def get_heights():
    with db_cursor() as cs:
        cs.execute("SELECT ID,Latitude,Longitude,Height FROM Height WHERE Height IS NOT NULL;")
        result = [models.Height(*row) for row in cs.fetchall()]
        return result

def get_accelerations():
    with db_cursor() as cs:
        cs.execute("SELECT ID,Latitude,Longitude,Acceleration FROM Acceleration")
        result = [models.Acceleration(*row) for row in cs.fetchall()]
        return result

def get_height_avg():
    with db_cursor() as cs:
        cs.execute("""
            SELECT a.grouping, AVG(h.Height) as HeightAVG
            FROM Height as h
            INNER JOIN Acceleration as a on h.Latitude = a.Latitude AND h.Longitude = a.Longitude
            GROUP BY a.grouping
            """)
        result = [models.HeightAVG(Grouping, HeightAVG) for Grouping, HeightAVG in cs.fetchall()]
        if result:
            return result
        else:
            abort(404)

def get_acceleration_avg():
    with db_cursor() as cs:
        cs.execute("""
            SELECT a.grouping, AVG(a.acceleration) as AccelerationAVG
            FROM Height as h
            INNER JOIN Acceleration as a on h.Latitude = a.Latitude AND h.Longitude = a.Longitude
            GROUP BY a.grouping
            """)
        result = [models.AccelerationAVG(Grouping, AccelerationAVG) for Grouping, AccelerationAVG in cs.fetchall()]
        if result:
            return result
        else:
            abort(404)

def get_correlation():
    with db_cursor() as cs:
        cs.execute("""
            SELECT
            Y.Grouping,
            ((tot_sum - (hei_sum * acc_sum / _count)) / sqrt((hei_sum_sq - pow(hei_sum, 2.0) / _count) * (acc_sum_sq - pow(acc_sum, 2.0) / _count))) AS "Correlation"
            FROM(
                SELECT
	            X.Grouping,
                sum(Height) AS hei_sum, #sigma x
                sum(Acceleration) AS acc_sum, #sigma y
                sum(Height * Height) AS hei_sum_sq, #sigma x^2
                sum(Acceleration * Acceleration) AS acc_sum_sq, #sigma y^2
                sum(Height * Acceleration) AS tot_sum, #sigma xy
                count(*) as _count
                FROM(
                    SELECT h.Height AS Height, a.Acceleration AS Acceleration, a.Grouping
                    FROM Height h
                    INNER JOIN Acceleration a ON h.Latitude = a.Latitude AND h.Longitude = a.Longitude
                    WHERE h.Height IS NOT NULL
                ) X
            GROUP BY X.Grouping
            ) Y
        """)
        result = [models.Correlation(Grouping, Correlation) for Grouping, Correlation in cs.fetchall()]
        if result:
            return result
        else:
            abort(404)

def get_height_and_acceleration():
    with db_cursor() as cs:
        cs.execute("""
                SELECT Height.ID , Height.Latitude, Height.Longitude, Height.Height , Acceleration.Acceleration, Acceleration.Grouping
                FROM Height 
                INNER JOIN Acceleration on Height.Latitude = Acceleration.Latitude and Height.Longitude = Acceleration.Longitude
            """)
        result = [models.HeightAndAccel(ID, Latitude, Longitude, Height, Acceleration, Grouping) for ID, Latitude, Longitude, Height, Acceleration, Grouping in cs.fetchall()]
        if result:
            return result
        else:
            abort(404)


