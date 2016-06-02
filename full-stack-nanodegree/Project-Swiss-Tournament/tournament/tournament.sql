-- Database Schema for the tournament project.
-- Author: Aron Roberts
-- Version: 1.02
-- Date Created: 12/30/2015
-- filename: tournament.sql
--
-- Last Update: 1/19/2016
-- added more comments
-- included code to create database
-- added some constraints

-- DROP DATABASE 
DROP DATABASE IF EXISTS tournament;

-- CREATE DATABASE 
CREATE DATABASE tournament;
\c tournament

-- DROP TABLE and VIEW STATEMENTS
DROP VIEW IF EXISTS Player_Standings;
DROP VIEW IF EXISTS Opponent_Wins;
DROP VIEW IF EXISTS Player_Losses;
DROP VIEW IF EXISTS Player_Wins;
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players;

-- CREATE TABLES
-- Players
CREATE TABLE Players
( 
	player_id SERIAL,
	full_name VARCHAR(255) NOT NULL,
	PRIMARY KEY(player_id)
);

-- Matches
CREATE TABLE Matches
(
	match_id SERIAL,
	winner int,
	loser int,
	PRIMARY KEY (match_id),
	FOREIGN KEY (winner) REFERENCES Players(player_id) ON DELETE CASCADE,
	FOREIGN KEY (loser) REFERENCES Players(player_id) ON DELETE CASCADE,
	CHECK (winner <> loser)
);


-- CREATE VIEWS
-- Player_Wins
CREATE VIEW Player_Wins AS
	SELECT winner AS player_id, COUNT(match_id) as wins from Matches
	GROUP BY winner;

-- Player_Losses
CREATE VIEW Player_Losses AS
	SELECT loser AS player_id, COUNT(match_id) as losses from Matches
	GROUP BY loser;
	
-- Opponent_Wins
CREATE VIEW Opponent_Wins AS
	SELECT m.winner AS player_id, SUM(w.wins) AS o_wins FROM Matches AS m INNER JOIN Player_Wins AS w on m.loser=w.player_id
	GROUP BY m.winner;

-- Player_Standings
CREATE VIEW Player_Standings AS
	SELECT p.player_id, p.full_name, coalesce(w.wins, 0) as wins, (coalesce(w.wins,0)+coalesce(l.losses,0)) AS matches, coalesce(o.o_wins, 0)  AS opponent_wins
	FROM Players AS p 
	 LEFT OUTER JOIN Player_Wins AS w ON p.player_id=w.player_id
	 LEFT OUTER JOIN Player_Losses AS l ON p.player_id=l.player_id
	 LEFT OUTER JOIN Opponent_Wins AS o ON p.player_id=o.player_id
	ORDER BY w.wins DESC, o.o_wins DESC;
