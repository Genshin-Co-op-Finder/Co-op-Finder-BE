import json
import mysql.connector
import os
from dotenv import load_dotenv


load_dotenv()

def connect():
    try:
        dataBase = mysql.connector.connect(
            host="localhost",
            user=os.getenv('DATABASEUSER'),
            password=os.getenv('DATABASEPAS'),
            database="genshinfinder"
        )
        cursor = dataBase.cursor(dictionary=True)
        return dataBase, cursor
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None, None

def createLobby(title, playersMax, tags, uid, displayName):
    dataBase, cursor = connect()
    if not cursor:
        print("Failed to connect to the database.")
        return
    
    try:
        json_tags = json.dumps(tags)
        json_uids = json.dumps([{"uid": uid, "displayName": displayName}])
        cursor.execute(
            "INSERT INTO lobbys (title, playersJoin, playersMax, tags, uid, playersInLobby, displayName) VALUES(%s, 1, %s, %s, %s,%s ,%s)",
            (title, playersMax, json_tags, uid , json_uids, displayName)
        )
        dataBase.commit()

        cursor.execute("SELECT * FROM lobbys WHERE uid = %s", (uid,))
        lobbyDetails = cursor.fetchall()
        return(lobbyDetails[0])
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
    finally:
        cursor.close()
        dataBase.close()


def joinLobby(uid, id, displayName):
    dataBase, cursor = connect()
    if not cursor:
        print("Failed to connect to the database.")
        return 
    
    try:
        cursor.execute("SELECT * FROM lobbys WHERE id = %s", (id,))
        lobbyDetails = cursor.fetchone()
        if lobbyDetails:
            playerList = json.loads(lobbyDetails["playersInLobby"])
            playerList.append({"uid": uid, "displayName": displayName})
            json_uids = json.dumps(playerList)
            cursor.execute(
                "UPDATE lobbys SET playersInLobby = %s, playersJoin = playersJoin + 1 WHERE id = %s",
                (json_uids, id)
            )
            dataBase.commit()
            cursor.execute("SELECT * FROM lobbys WHERE id = %s", (id,))
            lobbyDetails = cursor.fetchone()
            return lobbyDetails
        else:
            print("Lobby not found.")
            return None
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
    finally:
        cursor.close()
        dataBase.close()

def LeaveLobby(id, uid, displayName):
    dataBase, cursor = connect()
    if not cursor:
        print("Failed to connect to the database.")
        return 
    
    try:
        cursor.execute("SELECT * FROM lobbys WHERE id = %s", (id,))
        lobbyDetails = cursor.fetchone()
        if(lobbyDetails):
            playerList = json.loads(lobbyDetails["playersInLobby"])
            playerList.remove({"uid": uid, "displayName": displayName})
            json_uids = json.dumps(playerList)
            cursor.execute(
                "UPDATE lobbys SET playersInLobby = %s, playersJoin = playersJoin - 1 WHERE id = %s",
                (json_uids, id)
            )
            dataBase.commit()
        else:
            print("Lobby not found.")
            return None
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
    finally:
        cursor.close()
        dataBase.close()

def getAllLobbies():
    dataBase, cursor = connect()
    if not cursor:
        print("Failed to connect to the database.")
        return 
    
    try:
        cursor.execute("SELECT * FROM lobbys")
        lobbys = cursor.fetchall()
        return lobbys
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
    finally:
        cursor.close()
        dataBase.close()

def closeLobby(id):
    dataBase, cursor = connect()
    if not cursor:
        print("Failed to connect to the database.")
        return 
    
    try:              
        cursor.execute("DELETE FROM lobbys WHERE id = %s", (id,))
        dataBase.commit()

    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
    finally:
        cursor.close()
        dataBase.close()



print(os.getenv('DATABASEUSER'))