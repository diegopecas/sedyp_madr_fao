class CustomException(Exception):

  def __init__(self, message='', error=''):
    self.message = message
    self.error = error
  
  def __str__(self):
    return self.error

  def to_dict(self):
    return {'message': self.message, 'error': self.error}