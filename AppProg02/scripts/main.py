import json
import os
import time

# Game classes
class Player:
  def __init__(self, name, character_class, location, health= 100, attack= 10, gold= 0, inventory= []):
    self.name = name
    self.char_class = character_class
    self.health = health
    self.attack = attack
    self.inventory = inventory
    self.gold = gold
    self.max_inventory= 5
    self.current_location = location

  def print_stats(self):
    print(f"{self.name}'s stats:")
    print(f"Health: {self.health}")
    print(f"Attack: {self.attack}")
    print(f"Gold: {self.gold}")
    print(f"Inventory: {self.inventory}")

  def attack_enemy(self, enemy):
    damage = self.attack - enemy.defense
    if damage < 0:
      damage = 0
    enemy.health -= damage
    print(f"You hit the {enemy.name} for {damage} damage!")
    if enemy.health <= 0:
      print(f"The {enemy.name} dies.")
      
class Enemy:
  def __init__(self, name, health, attack, defense, gold_drop):
    self.name = name 
    self.health = health
    self.attack = attack
    self.defense = defense
    self.gold_drop = gold_drop

class NPC:
  def __init__(self, name, messages):
    self.name = name
    self.messages = messages
  def talk(self):
    print(f"[{self.name} says]: {self.messages[0]}")

class Quest:
  def __init__(self, name, description, reward):
    self.name = name
    self.description = description 
    self.reward = reward
    self.completed = False

class Location:
  def __init__(self, name, description):
    self.name = name
    self.description = description
    self.exits = {}
    self.enemies = []
    self.items = []
    self.npcs = []

class Item:
  def __init__(self, name, description, value):
    self.name = name
    self.description = description
    self.value = value

# Game functions
def print_location(p):
  print('\n' + p.current_location.name)
  print('-'*len(p.current_location.name))
  print(p.current_location.description)

def prompt_action():
  print("\nWhat would you like to do?")
  for action in actions:
    print(f"- {action}")
  action_input = input("> ")
  return action_input

def perform_action(player, action_input):
  if action_input == 'talk' and player.current_location.npcs:
    talk_to_npc(player.current_location.npcs[0])
  elif action_input == 'fight' and player.current_location.enemies:
    fight_enemy(player.current_location.enemies[0])
  elif action_input == 'move':
    prompt_move(player)
  elif action_input == 'take' and player.current_location.items:
    add_to_inventory(player)
  elif action_input == 'help':
    print_help()
  elif action_input == 'save':
    save_game(player)
  else:
    print("Invalid action.")

def prompt_move(p):
  exits = p.current_location.exits
  print("You can move to:") 
  for e in exits:
    print(f"- {e}")
  move_to = input("Where would you like to move? ")
  if move_to in exits:
    change_location(p, exits[move_to])
  else:
    print("You can't move there.")

def change_location(p, loc_name):
  try:  p.current_location = locations[loc_name]
  except: p.current_location= loc_name

def add_to_inventory(player):
  if len(player.inventory) < player.max_inventory:
    item= player.current_location.items[0]
    print(type(item))
    player.inventory.append(item)
    player.current_location.items.remove(item)
    print(f"You picked up the {item.name}")
  else:
    print("Inventory full!")

def print_inventory():
  print("Inventory:")
  for item in player.inventory:  
    print(f"- {item.name}")

def print_help():
  print("Commands:")
  print("- move: Move to a new location")
  print("- take: Pick up an item")
  print("- talk: Talk to an NPC")
  print("- fight: Fight an enemy")
  print("- inventory: View inventory")
  print("- help: View all commands")

def talk_to_npc(npc):
  print(f"[You talk to {npc.name}]")
  npc.talk()

def fight_enemy(enemy):
  while enemy.health > 0:
    print(f"You are fighting a {enemy.name}")
    print("What will you do?")
    action = prompt_action()
    if action == 'attack':
      player.attack_enemy(enemy)
      if enemy.health <= 0:
        print("You defeated the enemy!")
        player.gold += enemy.gold_drop
      else:
        enemy_damage = max(0, enemy.attack - player.attack)
        print(f"The {enemy.name} hits you for {enemy_damage} damage!")  
        player.health -= enemy_damage
    elif action == 'run':
      print("You ran away!")
      break
    else:
      print("Invalid combat action!")
      
# Save game
def save_game(player):

  lines = []
  
  # Player data
  lines.append(f"Name: {player.name}")
  lines.append(f"Class: {player.char_class}")
  lines.append(f"HP: {player.health}")
  lines.append(f"Gold: {player.gold}")
  lines.append(f"Attack: {player.attack}")
  items= []
  for item in player.inventory:
    items.append(item.name)
  lines.append("Inventory: "+ ','.join(items))
  
  lines.append(f"Current location: {player.current_location.name}")
  lines.append("")
  # Locations
  for loc in locations.values():
    lines.append(loc.name)
    lines.append(loc.description)
    lines.append(f"Exits: {loc.exits}")

  with open(f"{player.name}.txt", "w") as f:
    f.write("\n".join(lines)) 


# Load game
def load_game(filename):
  with open(filename+'.txt', "r") as f:
    lines = f.readlines()

  # Create player
  player_name = lines[0].split(": ")[1].strip('\n')
  char_class = lines[1].split(": ")[1].strip('\n')
  hp_data = lines[2].split(": ")[1]
  gold = lines[3].split(": ")[1]
  attack = lines[4].split(": ")[1]
  inventory = lines[5].split(': ')[1].split(',')
  # Set current location
  current_location= locations['home']
  current_loc_name = lines[6].split(": ")[1].strip('\n')
  if current_loc_name == 'Home':
    current_location= locations['home']
  elif current_loc_name == 'Forgotten Kingdom':
    current_location= locations['dungeon']
  elif current_loc_name == 'Wild Lands':
    current_location= locations['wilderness']
  else: 
    loc_names= [x.name for x in sublocs]
    if current_loc_name in loc_names:
      current_location= sublocs[loc_names.index(current_loc_name)]
  # Inventory

  player = Player(player_name, char_class, current_location, int(hp_data), int(attack), int(gold), inventory)

  # Locations
#   loc_index = lines.index("")
#   locs = {}
#   for i in range(loc_index+1, len(lines), 3):
#     name = lines[i]
#     desc = lines[i+1]
#     exits = lines[i+2].split(": ")[1]
#     locs[name] = Location(name, desc, exits)

  return player

def show_profiles():

  # Get .txt save files
  saves = [f for f in os.listdir() if f.endswith(".txt")]
  
  if not saves:
    print("No saved profiles found!")
    return

  print("\nSaved Profiles:")

  # Read data from each .txt file
  choices= []
  for save in saves:
    with open(save) as f:
      lines = f.readlines()
    
    # Extract player details     
    name = lines[0].split(": ")[1].strip('\n')
    choices.append(name)
    char_class = lines[1].split(": ")[1].strip('\n')
    hp = lines[2].split(": ")[1].strip('\n')
    
    print(name+ ':  A '+ char_class+ ' - with '+ str(hp)+ ' Health', end='\n')

  choice = input("\nEnter a name to load profile or press enter to start new game: ")
  if choice in choices:
    return load_game(choice)
  else: return 0
    
## Initialize world
# Create empty locations
locations = {}

# Dungeon locations
dungeon_entrance = Location("Dungeon Entrance", "A tunnel leads underground")
city_ruins = Location("City Ruins","Collapsed buildings and debris") 
castle = Location("Castle","An imposing castle looms ahead")
catacombs = Location("Catacombs","An eerie underground cemetery")
throne_room = Location("Throne Room","The ruined remains of a throne")

# home locations 
town_center = Location("home Center", "A bustling home square")
market = Location("Market", "Busy stalls line the streets")
docks = Location("Docks", "Ships are docked at the harbor")

# Wilderness locations
forest = Location("Deep Forest", "Lush dense woods") 
mountain = Location("High Mountain", "Steep treacherous slopes")
canyon = Location("Narrow Canyon", "A long ravine with sheer cliffs")

# Main locations
locations['home'] = Location("Home", "A peaceful home at the end of village")
locations['dungeon'] = Location("Forgotten Kingdom", "An ancient underground city") 
locations['wilderness'] = Location("Wild Lands", "Dangerous uncharted territory")

# Connect dungeon
dungeon_entrance.exits = {'dungeon': locations['dungeon'], 'city_ruins': city_ruins} 
city_ruins.exits = {'catacombs': catacombs, 'castle': castle, 'dungeon_entrance': dungeon_entrance} 
castle.exits = {'throne_room': throne_room}
throne_room.exits = {'castle': castle}
catacombs.exits = {'city_ruins': city_ruins}
castle.exits = {'city_ruins': city_ruins}
locations['dungeon'].exits = {'home': locations['home'], 'dungeon_entrance': dungeon_entrance}

# Connect home
town_center.exits = {'home': locations['home']}
market.exits = {'home': locations['home']}
docks.exits = {'home': locations['home']}
locations['home'].exits = {'dungeon': locations['dungeon'], 'wilderness': locations['wilderness'],
                           'town_center': town_center, 'market': market, 'docks': docks}
                           
# Connect wilderness                        
forest.exits = {'wilderness': locations['wilderness']}
mountain.exits = {'wilderness': locations['wilderness']}
canyon.exits = {'wilderness': locations['wilderness']}
locations['wilderness'].exits = {'home': locations['home'], 'forest': forest, 
                                 'mountain': mountain, 'canyon': canyon}

sublocs= [dungeon_entrance, city_ruins, castle, catacombs, throne_room, town_center, market, docks, forest, mountain, canyon]

# Add other details

catacombs.enemies.append(Enemy('Skeleton', 9, 4, 1, 5))
throne_room.enemies.append(Enemy('Lich', 50, 15, 8, 40)) 
canyon.enemies.append(Enemy('Serpent', 25, 8, 3, 12)) 
forest.enemies.append(Enemy('Bear', 20, 6, 2, 10)) 
mountain.enemies.append(Enemy('Stone Golem', 30, 8, 5, 15)) 


castle.items.append(Item('Ruby', 'A bright red gemstone', 100))
market.items.append(Item('Health Potion', 'Restores 20 HP', 20))
market.items.append(Item('Ancient Sword', 'A powerful blade', 150))
docks.npcs.append(NPC('John', ['Please help save our kingdom!']))


# Create player
def create_account():
  print("Create your account!")

  # Get player name
  name = input("Enter your name: ")

  # Character class selection
  print("Select your class:")
  print("1. Warrior (high strength)")
  print("2. Ranger (high dexterity)")
  print("3. Mage (high intelligence)")
  
  char_class = input("Enter your class (1/2/3): ")

  # Initialize based on selection
  loc = town_center
  if char_class == "1":
    player = Player(name, "Warrior", loc) 
    player.strength = 10
    player.dexterity = 5
    player.intelligence = 3

  elif char_class == "2":
    player = Player(name, "Ranger", loc)
    player.strength = 5
    player.dexterity = 10
    player.intelligence = 3

  elif char_class == "3": 
    player = Player(name, "Mage", loc)
    player.strength = 3
    player.dexterity = 5
    player.intelligence = 10

  print("Your account has been created!")
  print(f"Welcome, {player.name} the {player.char_class}")

  return player

# Start game
print("Welcome adventurer!")
with open('../resources/welcome.txt', 'r') as f:
  for lines in f.readlines():
    print(lines)
start_input= show_profiles()
if start_input:
  player= start_input
else:
  player= create_account()

while True:
    print_location(player)

    actions = ['move', 'talk', 'fight', 'take', 'help', 'save']

    action_input = prompt_action()
    print(action_input)
    perform_action(player, action_input)

    if player.health <= 0:
        print("You have died. Game over!")
        break
      
print("Thank you for playing!")