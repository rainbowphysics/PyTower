import argparse
from subprocess import Popen, PIPE
import sys
import os
import json
import uuid
import copy

SUITEBRO_PATH = r'C:\Users\gklub\Documents\Tower Unite\suitebro'

def dict_walk(d, replacement_table):
  if isinstance(d, dict):
    for k,v in d.items():
      if isinstance(v, dict):
        dict_walk(v, replacement_table)
      elif isinstance(v, list):
        for x in v:
          dict_walk(x, replacement_table)
      else:
        if k == 'value':
          for original, replacement in replacement_table.items():
            if v == original:
              d[k] = replacement

class ItemConnectionObject:
  def __init__(self, data):
    self.data = data
  
  def __init__(self, guid=None, event_name=None, delay=None, listener_event=None, data=None):
    self.data = JSON.loads('''{
                  "struct_type": "ItemConnectionData",
                  "value": {
                    "Item": {
                      "StructProperty": {
                        "struct_type": "GUID",
                        "value": null
                      }
                    },
                    "EventName": {
                      "NameProperty": null
                    },
                    "Delay": {
                      "FloatProperty": 0.0
                    },
                    "ListenerEventName": {
                      "NameProperty": null
                    },
                    "DataType": {
                      "EnumProperty": {
                        "enum_type": "FItemDataType",
                        "value": "FItemDataType::NONE"
                      }
                    },
                    "Data": {
                      "StrProperty": ""
                    }
                  }
                }''')
    
    if guid is not None:
      self.set_item_guid(guid)
    if event_name is not None:
      self.set_event_name(event_name)
    if delay is not None:
      self.set_delay(delay)
    if listener_event is not None:
      self.set_listener_event_name(listener_event)
    if datatype is not None:
      self.set_datatype(datatype)
    if data is not None:
      self.set_data(data)
  
  # Returns connected item GUID
  def get_item_guid(self) -> str:
    return self.data['value']['Item']['StructProperty']['value']
  
  def set_item_guid(self, guid: str):
    self.data['value']['Item']['StructProperty']['value'] = guid
  
  # Returns targeted event on item
  def get_event_name(self) -> str:
    return self.data['value']['EventName']['NameProperty']       
  
  def set_event_name(self, name: str):
    self.data['value']['EventName']['NameProperty'] = name   
  
  # Returns time delay in seconds
  def get_delay(self) -> float:
    return self.data['value']['Delay']['FloatProperty']   
  
  def set_delay(self, delay: float):
    self.data['value']['Delay']['FloatProperty'] = delay 
  
  # Returns evnet being listened to
  def get_listener_event_name(self) -> str:
     return self.data['value']['Item']['StructProperty']['value']
  
  def set_listener_event_name(self, name: str) -> str:
     self.data['value']['Item']['StructProperty']['value'] = name
  
  def get_datatype(self) -> dict:
    return self.data['value']['DataType']
  
  def set_datatype(self, datatype: dict):
    self.data['value']['DataType'] = datatype
  
  def get_data(self) -> dict:
    return self.data['value']['Data']
  
  def set_data(self, data: dict) -> dict:
    return self.data['value']['Data'] = data
  
  def get_dict(self) -> dict:
    return self.data
  
  def set_dict(self, data):
    self.data = data
  
  def to_dict(self) -> dict:
    return copy.deepcopy(self.data)
  
  # Needed to call dict(...) on objects of this class type
  def __iter__(self):
    for k,v in self.data:
      yield (k, v)

class TowerObject:
  def __init__(self, item=None, properties=None):
    self.item = copy.deepcopy(item)
    self.properties = copy.deepcopy(properties)
    
    if 'ItemConnections' not in self.item.keys():
      self.item['ItemConnections'] = JSON.loads('''{
          "ArrayProperty": {
            "StructProperty": {
              "field_name": "ItemConnections",
              "value_type": "StructProperty",
              "struct_type": "ItemConnectionData",
              "values": []
            }
          }
        }''')
  
  def copy(self):
    copied = TowerObject(item=self.item, properties=self.properties)
    copied.item['guid'] = str(uuid.uuid4()).upper()
    return copied
  
  def get_name(self):
    return self.item['name']
  
  def get_custom_name(self):
    return self.item['properties']['ItemCustomName']['NameProperty']
  
  def matches_name(self, name):
    name = name.casefold()
    return self.get_name() == name or self.get_custom_name().casefold() == name
  
  @staticmethod
  def copy_group(group: list):
    # First pass: new guids and setup replacement table
    replacement_table = {}
    copies = [None] * len(group)
    for x, obj in enumerate(group):
      old_guid = obj.item['guid']
      copied = obj.copy()
      new_guid = copied.item['guid']
      replacement_table[old_guid] = new_guid
      
      copies[x] = copied
    
    # Second pass: replace any references to old guids with new guids
    for obj in copies:
      # TODO just json encode/decode and re.sub
      dict_walk(obj.item, replacement_table)
      dict_walk(obj.properties, replacement_table)
    
    return copies
  
  def add_connection(self, con: ItemConnectionObject):
    connections = self.item['ItemConnections']['ArrayProperty']['StructProperty']['values']
    connections += con.to_dict()
    self.properties['ItemConnections'] = self.item['ItemConnections']
  
  def get_connections(self) -> [ItemConnectionObject]:
    cons = []
    for data in self.item['ItemConnections']['ArrayProperty']['StructProperty']['values']:
      cons.append(ItemConnectionObject(data))
    
    return cons
  
  def set_connections(self, cons: [ItemConnectionObject]):
    self.item['ItemConnections']['ArrayProperty']['StructProperty']['values'] = list(map(lambda con: con.to_dict(), cons))
  
  def __lt__(self, other):
    if not isinstance(other, TowerObject):
      return False
    
    if self.item is None and other.item is None:
      # CondoWeather needs to always be first, followed by CondoSettingsManager, then Ultra_Dynamic_Sky?
      if self.properties['name'].startswith('CondoWeather'):
        return True
      elif self.properties['name'].startswith('CondoSettingsManager'):
        return not other.properties['name'].startswith('CondoWeather')
      elif self.properties['name'].startswith('Ultra_Dynamic_Sky'):
        return (not other.properties['name'].startswith('CondoWeather')) and \
               (not other.properties['name'].startswith('CondoSettingsManager'))
      
      return self.properties['name'] < other.properties['name']
    
    if self.item is None:
      return True
    
    if other.item is None:
      return False
    
    return self.item['name'] < other.item['name']
  
  def __repl__(self):
    return f'TowerObject({self.item}, {self.properties})'

class Suitebro:
  def __init__(self, data):
    self.data = data
    self.parse_objects()
  
  
  def parse_objects(self):
    prop_section = self.data['properties']
    item_section = self.data['items']
    self.objects = [None] * len(prop_section)
    
    item_idx = 0
    for x in range(len(prop_section)):
      p = prop_section[x]
      i = item_section[item_idx]
      if p['name'].startswith(i['name']):
        self.objects[x] = TowerObject(item=i, properties=p)
        item_idx += 1
      else:
        self.objects[x] = TowerObject(item=None, properties=p)
  
  def add_object(self, obj):
    self.objects += [obj]
  
  def add_objects(self, objs):
    self.objects += objs
  
  def to_dict(self):
    new_dict = {}
    for k,v in self.data.items():
      if k != 'items' and k != 'properties':
        new_dict[k] = v
    
    self.objects.sort()
    
    num_obj = len(self.objects)
    item_arr = [None] * num_obj
    prop_arr = [None] * num_obj
    
    item_idx = 0
    prop_idx = 0
    
    last_name = None
    last_num = 0
    for obj in self.objects:
      if obj.item is not None:
        item_arr[item_idx] = obj.item
        item_idx += 1
      if obj.properties is not None:
        # Name fuckery TODO determine if the naming even matters
        if obj.item is not None:
          name_split = obj.properties['name'].split('_')
          root_name = '_'.join(name_split[:-1])
      
          if last_name == root_name:
            last_num += 1
          else:
            last_num = 0
      
          obj.properties['name'] = root_name + '_' + str(last_num)
      
          last_name = root_name
        
        # Now actually add to prop_arr
        prop_arr[prop_idx] = obj.properties
        prop_idx += 1
    
    item_arr = item_arr[:item_idx]
    prop_arr = prop_arr[:prop_idx]
    
    # Finally set new dictionary and return
    new_dict['items'] = item_arr
    new_dict['properties'] = prop_arr
    return new_dict
  
  def __repl__(self):
    return f'Suitebro({self.data}, {self.objects})'
  
def main():
  filename = 'CondoData'
  abs_filepath = os.path.realpath(filename)
  condo_dir = os.path.dirname(abs_filepath)
  json_output_path = os.path.join(condo_dir, os.path.basename(abs_filepath) + ".json")
  json_final_path = os.path.join(condo_dir, 'output.json')
  final_output_path = os.path.join(condo_dir, 'output')
  
  os.chdir(SUITEBRO_PATH)

  process = Popen(f'cargo run --release to-json -! -i \"{abs_filepath}\" -o \"{json_output_path}\"', stdout=PIPE)
  (output, err) = process.communicate()
  print(output, file=sys.stderr)
  for line in output.splitlines(False):
    print(line)
  
  exit_code = process.wait()
  
  if exit_code != 0:
    logging.warning('WARNING: Suitebro to-json did not complete successfully!')
    
  
  os.chdir(condo_dir)
  
  print('Loading JSON file...')
  with open(json_output_path, 'r') as fd:
    save_json = json.load(fd)
  
  save = Suitebro(save_json)
  
  exclusions = ['CanvasWallFull', 'Counter', 'FloatingTextSign']
  template_objects = list(filter(lambda obj: (obj.item is not None) and (obj.item['name'] not in exclusions), save.objects))
  print(template_objects)
     
  for x in range(-5, 5):
    for y in range(-5, 5):
      for z in range(20):
        if x == 0 and y == 0 and z == 0:
          continue
        copies = TowerObject.copy_group(template_objects)
          
        # Set position
        for obj in copies:
          obj.item['position']['x'] += 70*x
          obj.item['position']['y'] += 70*y
          obj.item['position']['z'] += 70*z
        
        save.add_objects(copies)
  
  with open(json_final_path, 'w') as fd:
    json.dump(save.to_dict(), fd, indent=2)
  
  # Finally run!
  os.chdir(SUITEBRO_PATH)
  
  process = Popen(f'cargo run --release to-save -! -i \"{json_final_path}\" -o \"{final_output_path}\"', stdout=PIPE)
  (output, err) = process.communicate()
  print(output, file=sys.stderr)
  for line in output.splitlines(False):
    print(line)
  
  exit_code = process.wait()
  if exit_code != 0:
    logging.warning('WARNING: Suitebro to-save did not complete successfully!')
  
  
if __name__ == '__main__':
  main()