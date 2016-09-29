import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Enum, Numberic
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class Gender(enum.Enum):
	male = 'male'
	female = 'female'

class Shelter(Base):

	__tablename__ = 'shelter'

	name = Column(String(80), nullable = False)
	address = Column(String(80), nullable = False)
	city = Column(String(80), nullable = False)
	state = Column(String(30), nullable = False)
	zip_code = Column(String(10), nullable = False)
	website = Column(String(80))
	id = Column(Integer, primary_key = True)
	


class Puppy(Base):

	__tablename__ = 'puppy'

	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	date_of_birth = Column(Date)
	gender = Column(Enum(Gender), nullable = False)
	weight = Column(Numberic(8))
	picture = Column(String)
	shelter_id = Column(Integer, ForeignKey('shelter.id'))
	shelter = relationship(Shelter)



#####insert at end of file ####
engine = create_engine('sqlite:///puppies.db')
Base.metadata.create_all(engine)