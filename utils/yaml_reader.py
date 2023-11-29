import yaml

Class YamlReader:

   def __init__(self, input):
      with open(input, 'r') as file:
         try:
            data = yaml.safe_load(file)
            return data
         except yaml.YAMLError as exc:
            print(exc)


