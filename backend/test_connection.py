import os
import oracledb
from dotenv import load_dotenv

oracledb.defaults.fetch_lobs = False
load_dotenv()

cs='''(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.us-chicago-1.oraclecloud.com))(connect_data=(service_name=g02527d20960581_uexulb26uojc2pyx_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'''

try:
    print("starting connection")
    connection = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=cs,
    )
    print("connected!")

    cursor = connection.cursor()
    print("executing query")
    cursor.execute("SELECT 'CONNECTED' FROM dual")
    print("fetched!")
    print(cursor.fetchone())

    cursor.close()
    connection.close()

except Exception as e:
    print("CONNECTION FAILED")
    print(e)