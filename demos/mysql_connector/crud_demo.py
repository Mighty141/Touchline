import os
import mysql.connector
cnx = mysql.connector.connect(host=os.getenv("MYSQL_HOST","127.0.0.1"), user=os.getenv("MYSQL_USER","root"), password=os.getenv("MYSQL_PASSWORD",""), database=os.getenv("MYSQL_DATABASE","touchline_demo"))
cursor = cnx.cursor(dictionary=True)
try:
    cursor.execute("CREATE TABLE IF NOT EXISTS connector_demo_players (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), position VARCHAR(40))")
    cursor.execute("INSERT INTO connector_demo_players(name,position) VALUES (%s,%s)", ("Sample Striker","Forward"))
    cnx.commit()
    cursor.execute("SELECT id,name,position FROM connector_demo_players ORDER BY id DESC LIMIT 10")
    for row in cursor.fetchall(): print(row)
    # UPDATE example: cursor.execute("UPDATE connector_demo_players SET position=%s WHERE id=%s", ("Midfielder", 1)); cnx.commit()
    # DELETE example: cursor.execute("DELETE FROM connector_demo_players WHERE id=%s", (1,)); cnx.commit()
finally:
    cursor.close()
    cnx.close()
