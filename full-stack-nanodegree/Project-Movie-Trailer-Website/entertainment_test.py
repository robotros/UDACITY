""" Movie Trailer website

UDACITY Full stack Developer Project 1
This file contains calls to create movie objects and then pass array off to
fresh_tomatoes provided by UDACITY, to generate HTML portions of project

Author: Aron Roberts
Version: 1.02
Date: 6/4/2015
filename: entertainment_test.py

Last Update: Update file to meet PEP8 Requirements
Lines 25, 32, 39, 60, 67 exceed length requirements but are URLS

"""

import movie
import fresh_tomatoes


# create movie objects
star_wars_1 = movie.Movie(
 "Star Wars : Episode I The Phantom Menace",
 "Episode I in the Star Wars Saga",
 "http://upload.wikimedia.org/wikipedia/en/4/40/Star_Wars_Phantom_Menace_poster.jpg",
 "https://youtu.be/bD7bpG-zDJQ?list=PL3339D1C61DB4AB28",
 "PG")

star_wars_2 = movie.Movie(
 "Star Wars : Episode II Attack of the Clones",
 "Episode II in the Star Wars Saga",
 "https://upload.wikimedia.org/wikipedia/en/3/32/Star_Wars_-_Episode_II_Attack_of_the_Clones_%28movie_poster%29.jpg",
 "https://youtu.be/gYbW1F_c9eM?list=PL3339D1C61DB4AB28",
 "PG")

star_wars_3 = movie.Movie(
 "Star Wars : Episode III Revenge of the Sith",
 "Episode III in the Star Wars Saga",
 "https://upload.wikimedia.org/wikipedia/en/9/93/Star_Wars_Episode_III_Revenge_of_the_Sith_poster.jpg",
 "https://youtu.be/5UnjrG_N8hU?list=PL3339D1C61DB4AB28",
 "PG-13")

star_wars_4 = movie.Movie(
 "Star Wars : Episode IV A New Hope",
 "Episode IV in the Star Wars Saga",
 "https://upload.wikimedia.org/wikipedia/en/8/87/StarWarsMoviePoster1977.jpg",
 "https://youtu.be/vZ734NWnAHA?list=PL3339D1C61DB4AB28",
 "PG")

star_wars_5 = movie.Movie(
 "Star Wars : Episode V The Empire Strikes Back",
 "Episode V in the Star Wars Saga",
 "https://upload.wikimedia.org/wikipedia/en/3/3c/SW_-_Empire_Strikes_Back.jpg",
 "https://youtu.be/JNwNXF9Y6kY?list=PL3339D1C61DB4AB28",
 "PG")

star_wars_6 = movie.Movie(
 "Star Wars : Episode VI Return of the Jedi",
 "Episode VI in the Star Wars Saga",
 "https://upload.wikimedia.org/wikipedia/en/b/b2/ReturnOfTheJediPoster1983.jpg",
 "https://youtu.be/16YLjTkK5jE?list=PL3339D1C61DB4AB28",
 "PG")

star_wars_7 = movie.Movie(
 "Star Wars : Episode VII The Force Awakens",
 "Episode VII in the Star Wars Saga",
 "https://upload.wikimedia.org/wikipedia/en/2/28/Starwarsviitheforceawakens.jpg",
 "https://youtu.be/ngElkyQ6Rhs",
 "NR")


# add movies to array
movies = [star_wars_1,
          star_wars_2,
          star_wars_3,
          star_wars_4,
          star_wars_5,
          star_wars_6,
          star_wars_7]


# pass array off to fresh_tomatoes to generate and open HTML
fresh_tomatoes.open_movies_page(movies)
