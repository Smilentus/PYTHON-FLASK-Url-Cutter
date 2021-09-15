import sqlite3
import hashlib

SALT = '340cfed177c54e2d9491d3b9ad297cf4'

def connectToDatabase():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    return conn, cursor

def closeConnection(conn):
    conn.close()

def createDefaultTables():
    conn, cursor = connectToDatabase()

    cursor.execute("CREATE TABLE url (urlID INTEGER PRIMARY KEY AUTOINCREMENT , longUrl VARCHAR(255), shortUrl VARCHAR(255))")
    cursor.execute("CREATE TABLE urls (userID INTEGER, urlID INTEGER)")
    cursor.execute("CREATE TABLE users (userID INTEGER PRIMARY KEY AUTOINCREMENT , login VARCHAR(255), password VARCHAR(255))")
    cursor.execute("INSERT INTO url (urlID, longUrl, shortUrl) VALUES (0, '8ophavg7voirs6h7', 'aicosdn56u3v0svdf')")
    cursor.execute("INSERT INTO urls (userID, urlID) VALUES (0, 0)")
    cursor.execute("INSERT INTO users (userID, login, password) VALUES (0, 'svn635bus8en3d', 'dvo86n7es8od456b3dx')")

    conn.commit()
    closeConnection(conn)

def createNewUser(user, password):
    if not isUserExist(user):
        conn, cursor = connectToDatabase()

        h = hashlib.md5(password.encode('utf-8'))
        hashPass = h.hexdigest()
        
        cursor.execute("INSERT INTO users (login, password) VALUES ((?), (?))", (user, hashPass))

        conn.commit()
        closeConnection(conn)
        return True
    else:
        return False

def getUser(user):
    conn, cursor = connectToDatabase()
    cursor.execute("SELECT * FROM users WHERE login = (?)", (user, ))
    data = cursor.fetchall()
    closeConnection(conn)
    return data

def isUserExist(user):
    conn, cursor = connectToDatabase()
    cursor.execute("SELECT login FROM users WHERE login = (?)", (user, ))
    data = cursor.fetchall()
    closeConnection(conn)
    if data:
        return True
    else:
        return False

def authUser(login, password):
    if isUserExist(login):
        data = getUser(login)

        h = hashlib.md5(password.encode('utf-8'))
        hashPass = h.hexdigest()

        if data[0][2] == hashPass:
            return True
        else:
            return False
    else:
        return False

def createNewUrl(longUrl, shortUrl, user):
    conn, cursor = connectToDatabase()

    if cursor.execute("""
    SELECT longUrl FROM url 
    JOIN urls ON urls.urlID = url.urlID
    JOIN users ON users.userID = urls.userID
    WHERE longUrl = (?) AND users.login = (?)
    """, (longUrl, user)).fetchall():
        return False
    
    lastID = cursor.execute("SELECT COUNT(*) as counter FROM url").fetchall()[0][0]

    if not shortUrl:
        shortUrl = hex(lastID * 10)[2:]

    cursor.execute("""
    INSERT INTO url (longUrl, shortUrl) VALUES ((?), (?))
    """, (longUrl, shortUrl))
    urlID = cursor.execute("SELECT urlID FROM url WHERE longUrl = (?)", (longUrl, )).fetchall()[0][0]
    userID = cursor.execute("SELECT userID FROM users WHERE login = (?)", (user, )).fetchall()[0][0]
    cursor.execute("""
    INSERT INTO urls (urlID, userID) VALUES ((?), (?))
    """, (urlID, userID))

    conn.commit()
    closeConnection(conn)
    return True

def getLongUrlByShort(url):
    conn, cursor = connectToDatabase()
    data = cursor.execute("SELECT longUrl FROM url WHERE shortUrl = (?)", (url, )).fetchall()
    closeConnection(conn)
    return data[0][0]

def getAllUrlsByAuthor(user):
    conn, cursor = connectToDatabase()

    data = cursor.execute("""
    SELECT longUrl, shortUrl FROM url 
    JOIN urls ON urls.urlID = url.urlID
    JOIN users ON users.userID = urls.userID
    WHERE users.login = (?)
    """, (user, )).fetchall()

    closeConnection(conn)
    return data

def getUserInfo(user):
    data = getAllUrlsByAuthor(user)
    result = []
    for obj in data:
        result.append({ 'long': obj[0], 'short': obj[1] })
    return result