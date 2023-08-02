from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(String, nullable=True)
    date_of_death = Column(String, nullable=True)

    def __repr__(self):
        return f"Author(id={self.id}, name='{self.name}', birth_date='{self.birth_date}', date_of_death='{self.date_of_death}')"

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False)
    title = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=True)
    author_id = Column(Integer, ForeignKey('authors.id'))

    author = relationship('Author', back_populates='books')

    def __repr__(self):
        return f"Book(id={self.id}, isbn='{self.isbn}', title='{self.title}', publication_year={self.publication_year})"

# Bind the engine to the existing SQLite database
engine = create_engine('sqlite:///data/library.sqlite')

# Create the tables if they do not exist
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
