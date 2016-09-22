import os
import sys
from sqlalchemy import Column, ForiegnKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Restuarant(Base):

	__tablename__ = 'restuarant'

	name = Coumn(String(80), nullable = False)
	id = Coumn(Integer, primary_key = True)
	


class MenuItem(Base):

	__tablename__ = 'menu_item'

	name = Coumn(String(80), nullable = False)
	id = Coumn(Integer, primary_key = True)
	description(String(250), nullable = False)
	course = Column(String(250))
	price = Column(String(8))
	restaurant_id = Column(Integer, ForiegnKey('restaurant.id'))
	restaurant = relationship(Restaurant)



#####insert at end of file ####
engine = create_engine('sqlite:///restaurantmenu.db')
Bade.metadata.create_all(engine)