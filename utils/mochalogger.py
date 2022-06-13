import logging

def getLogger():
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.DEBUG)
  handler = logging.FileHandler('app.log')
  handler.setLevel(logging.DEBUG)
  format = logging.Formatter('%(asctime)s - %(message)s')
  handler.setFormatter(format)
  logger.addHandler(handler)
  return logger