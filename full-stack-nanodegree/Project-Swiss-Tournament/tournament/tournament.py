""" Tournament Database
    UDACITY Full stack Developer Project 2
    This file contains functions that use DB-API calls
    to manage a swiss tournament database
    Author: Aron Roberts
    Version: 1.03
    Date: 1/16/2016
    filename: tournament.py

    Last Update: 1/19/2016
    added cursor creation into connect()

    notes: line 86 is considered long by PEP8 but is a SQL execute
"""


import psycopg2
import time
import bleach


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname = {}".format(database_name))
        c = db.cursor()
        return db, c
    except:
        print("Databse Connection Failed")


def deleteMatches():
    """Remove all the match records from the database."""
    db, c = connect()
    c.execute("DELETE FROM Matches --")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db, c = connect()
    c.execute("DELETE FROM Players --")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db, c = connect()
    c.execute("SELECT count(player_id) FROM players")
    count = c.fetchone()[0]
    db.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db, c = connect()
    name = str(bleach.clean(name, strip=True))
    c.execute("INSERT INTO players (full_name) VALUES(%s)", (name,))
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list is the player in first place,or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, c = connect()
    c.execute("SELECT player_id, full_name, wins, matches FROM Player_Standings")
    players = [(row[0], row[1], int(row[2]), int(row[3]))
               for row in c.fetchall()]
    db.close()
    return players


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.
    Verifies that both players are registered

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    winner = int(bleach.clean(winner, strip=True))
    loser = int(bleach.clean(loser, strip=True))
    db, c = connect()
    c.execute("SELECT player_id FROM players")
    players = [row[0] for row in c.fetchall()]
    if ((winner in players) and ((loser in players) or (loser == 0))):
        c.execute("INSERT INTO matches (winner, loser) VALUES(%s, %s)",
                  (int(winner), int(loser),))
        db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings. If odd pairing, player in last recieved BYE

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db, c = connect()
    c.execute("SELECT player_id, full_name FROM Player_Standings")
    players = [(row[0], row[1])
               for row in c.fetchall()]
    pairs = []
    participants = len(players)
    if (participants % 2 != 0):
        participants = participants - 1
        pairs.append((players[participants][0], players[participants][1],
                      0, 'BYE'))

    i = 0
    while (i < participants):
        pairs.append((players[i][0], players[i][1],
                      players[i+1][0], players[i+1][1]))
        i = i + 2

    db.close()
    return pairs
