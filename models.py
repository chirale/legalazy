import settings
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, PickleType, DateTime, Integer, String, Float, Boolean, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
# from jkows.utils.generic import sql_prepare_select_chunk, chunk, sql_prepare_select_simple
import os

Base = declarative_base()

# SQLITE_ARG_LIMIT = 899


class Page(Base):
    """ Pagine del sito """
    __tablename__ = "page"
    slug = Column(String, primary_key=True, nullable=False, unique=True)
    title = Column(String, nullable=False)
    cache = Column(SmallInteger, default=0)
    file = Column(String)
    in_nav = Column(Boolean, default=False)
    nav_order = Column(SmallInteger)

################################################


class DocuwebDb(object):
    """ in sostituzione di conf """
    profile_name = 'docuweb'
    path = ''
    uri = ''
    engine = None
    """ True to enable database debug """
    debug = False
    sessionmaker = None
    """ @see http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-faq-whentocreate """

    def __init__(self, **kwargs):
        self.profile_dir = kwargs.get('profile_dir', settings.DATA_DIRECTORY)
        self.profile_name = kwargs.get('profile_name', self.profile_name)
        self.path = os.path.join(self.profile_dir, "{}.db".format(self.profile_name))
        self.engine = kwargs.get('engine', None)
        self.uri = "".join(('sqlite:///', self.path))
        """ connect to db """
        self.engine = create_engine(self.uri, echo=self.debug)
        self.sessionmaker = sessionmaker(bind=self.engine)
        self.create_tables()

    def create_tables(self):
        """ create all tables subclasses of Base (or skip if exists) """
        Base.metadata.create_all(self.engine)

