from app.config import Config
import psycopg2


class DatabaseService():

  def __init__(self):
      self.connection = psycopg2.connect(user=Config._USER, password=Config._PASSWORD, host=Config._HOST, port=Config._PORT, database=Config._DATABASE)

  def get_connection(self):
    return self.connection

  
