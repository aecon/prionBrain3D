from utils.yaml_reader import YamlReader
from utils import preprocessor


class DataLoader:

   def __init__(self, file):
      self.file = file
      self.dict = ""
      self._read_yaml()


   def _read_yaml(self):
      self.dict = YamlReader(self.file)


   def preprocess_data(self, data):
      return preprocessor.preprocess(data)


