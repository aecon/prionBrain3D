import yaml

def load(ymlfile):
   with open(ymlfile, 'r') as file:
      try:
         data = yaml.safe_load(file)
         return data
      except yaml.YAMLError as exc:
         print(exc)

