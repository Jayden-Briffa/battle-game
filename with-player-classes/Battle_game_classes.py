import time
import random
from numpy import arange
from collections import namedtuple

all_players = {}
game_speed = 1

# Format a player's name
def name_fmt(player_name):
    return '\033[1m' + '\033[4m' + player_name + '\033[0m'

# Generate names for default players
def default_players():

    # Define default names and classes
    default_names = ["Mitchell", "Dave", "Kyran", "Chuckles", "Ford", "Alex", "Briff"]
    default_classes = ["Warrior", "Mage"]

    # Rearrange names and classes to randomise output order
    random.shuffle(default_names)
    random.shuffle(default_names)

    no_of_names = len(default_names)
    
    # Make the possible names an iterator to allow use of next()
    default_names = iter(default_names)

    # Return the next generated name and class each time it is called
    for i in range(no_of_names):
        name = next(default_names)
        atk_class = random.choice(default_classes)

        yield (name, atk_class)

# Format and print the given message 
def error_message(header, message):
    top_str = f"\n/ / / / / / {header} / / / / / /" 
    print(top_str)
    time.sleep(0.25 / game_speed)
    input(f"{message}. Press Enter to continue: ")
    print((int(len(top_str)) // 2) * "/ " + "\n")

# Create a new player instance with the given name and class
def add_new_player(name, atk_class):
    all_players[name] = Player(name, atk_class)

    new_player = list(all_players.values())[-1]

    return f'{str(new_player)} is joining the battle as a {new_player.atk_class_name}! '

# Used to define moves players can use
class Move:
    def __init__(self, name, move_type, effect, accuracy, crit_info, targets, description, stagger = None):
        
        # Set an attribute for each given parameter
        all_attr = locals().copy()
        del all_attr["self"]

        for attr in all_attr:
            setattr(self, attr, all_attr[attr])

    # Format and return status effects as a human-readable string
    def format_effects(self):
        effect_info = ''
        for fx, val in self.effect.items():
            if effect_info != '':
                effect_info += ', '

            effect_info += f'{fx}: {val}'

        return effect_info
    
    # Format and return critical hit chance and effects as a human-readable string
    def format_crit(self):
        if self.crit_info == False:
            crit_fmt = 'None'

        else:
            crit_fmt = f'Chance = {self.crit_info["chance"]}%, Effect = x{self.crit_info["crit_effect"]}'

        return crit_fmt
    
    # Format and return move's effects, crit chance, and accuracy as a human-readable string
    def format_self(self):

        effect_fmt = self.format_effects()

        crit_fmt = self.format_crit()

        accuracy_fmt = format_accuracy(self.accuracy)

        return f'-- {self.name} info -- \nType: {self.move_type} \nEffect: {effect_fmt} \nAccuracy: {accuracy_fmt} \nCritical hit: {crit_fmt} \nTargets: {self.targets}'
    

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __repr__(self):
        return self.name

# Used to define classes players can choose from
class Attack_Class:
    
    def __init__(self, name, moves, speed, health):

        self.name = name
        self.speed = speed
        self.health = health

        # Creates a dictionary containing all moves the class can perform
        self.move_set = {}
        for move in moves:
            self.move_set[move.name] = move
        
# Used to define player names, stats, and classes
class Player:

    # Sets the name and stats
    def __init__(self, name, atk_class):
        
        self.name = name
        self.atk_class_name = atk_class.name
        self.move_set = atk_class.move_set.copy()
        self.speed = atk_class.speed
        self.health = atk_class.health

        # Stat multiplier = [multiplier, remaining turns]
        self.status_fx = []
        self.staggered_moves = []

    # Give the player a status effect
    def add_status_effect(self, name, **properties):
        self.status_fx.append({"name": name, **properties})
    
    # Have the player charge up a move to use later
    def add_staggered_move(self, move, user, targets, stagger):
        self.staggered_moves.append({"move": move, "user": user, "targets": targets, "remaining_turns": stagger[0], "block_use_move": stagger[1]})

    # Allows the program to access a player's speed adjusted with any relevent effects
    def get_true_speed(self):

        true_speed = self.speed

        for status_effect in self.status_fx:
            effect_name = status_effect["name"]

            if effect_name == "+Speed" :
                true_speed += status_effect["value"]

            elif effect_name == "-Speed":
                true_speed -= status_effect["value"]

        return true_speed

    # Make all status effects and staggered moves progress by 1 turn
    def increment_turns(self):

        for i, effect in zip(range(len(self.status_fx)), self.status_fx.copy()):

            turns = effect["remaining_turns"]
            if turns <= 0:
                del self.status_fx[i]

            else:
                effect["remaining_turns"] -= 1

        for i, move in zip(range(len(self.staggered_moves)), self.staggered_moves):
            
            turns = move["remaining_turns"]
            
            move["remaining_turns"] -= 1

    # Format and return player's status effets as a human-readable string
    def format_stat_fx(self):
        formatted = f""
        
        for effect in self.status_fx:

            # Seperates different effects with a comma
            if len(formatted) > 0:
                formatted += ", "

            name = effect["name"]
            turns = effect["remaining_turns"]

            # Creates a dictionary which only includes the items which relate the the effect's power level
            power_key = list(filter(lambda key: key not in ["name", "remaining_turns", "chance"], effect.keys()))[0]
            power = str(effect[power_key])

            if power_key == "multiplier":
                power = "x" + power

            formatted += f"{name}: {power} ({turns} turns)"
             
        # Return default message or status effects, depending on if there are any active
        if len(formatted) == 0:
            formatted = "No status effects"

        else:
            formatted = "Status FX- " + formatted
        
        return formatted

    # Return default message or staggered moves, depending on if there are any active
    def format_staggered_moves(self):
        formatted = ""

        for move in self.staggered_moves:

            if len(formatted) > 0:
                formatted += ", "
            formatted += f"{move['move']}: {move['remaining_turns']} turns"
        
        if len(formatted) == 0:
            formatted = "No staggered moves"

        return formatted
    
    # Make the player take damage from burning 
    def burn_tick(self):
    
        for effect in self.status_fx:

            if effect["name"] == "Burning":
                damage = self.inflict_damage(effect["value"])
                print(f"{self.name} was burned for {damage} damage")

                time.sleep(1 / game_speed)


    def __str__(self):
        return name_fmt(self.name)
    
    # Return the player's summary as a human-readable string
    def format_self(self):
        formatted_fx = self.format_stat_fx()
        formatted_staggered_moves = self.format_staggered_moves()

        # Displays HP, Speed, Status FX, and Staggered Moves
        return f"{self.name}: {self.health} HP --- {self.get_true_speed()} Speed --- {formatted_fx} --- {formatted_staggered_moves}"
    
    # Update the player to reflect a turn being used
    def new_turn(self):
        self.increment_turns()
        self.burn_tick()
        

    # Inflicts damage on the player
    def inflict_damage(self, damage):

        # Check player Status FX for relevent FX and apply them
        for effect in self.status_fx:
            if effect["name"] == "Protection":  
                damage *= effect["multiplier"]
            
            elif effect["name"] == "Weakness":
                damage /= effect["multiplier"]

        # Round damage to nearest whole number
        damage = round(damage, 0)

        # Reduce the player's health by the given damage
        self.health -= damage
        return damage
    
    # Heals the player
    def heal(self, heal):
        self.health += heal

# Format and return move accuracy as a human-readable string
def format_accuracy(accuracy):
    return str(accuracy) + '%' if accuracy != True else 'Cannot miss'

# Check user input to decide whether move info should be displayed
def check_if_info_req(req):

    is_info_req = False
    if len(req) >= 5:
        is_info_req = req[0:5].upper() == 'INFO '
    
    if is_info_req:
        req = req[5:]

    return is_info_req, req

# Allow the player to select a move from their class move list
def select_move(player):
    is_valid_move = False

    while True:
        move_set = player.move_set

        print("CHOOSE YOUR MOVE")
        time.sleep(0.25 / game_speed)

        # Print all ofthe user's moves in a human-readable format
        for i, move in zip(range(1, len(move_set) + 1), move_set):
            time.sleep(0.1 / game_speed)
            print(f"{i}: {move} --- {move_set[move].description}")

        # Get the user's move choice
        move = input("Which move would you like to use? Type \'INFO <choice>\' to get information about that move. ")
        is_info_req, move = check_if_info_req(move)

        if move != "":

            # Allow user to enter move name in full
            if move.capitalize() in move_set:
                is_valid_move = True
            
            # Allow user to enter move number as shorthand
            elif move.isnumeric():
                move = int(move)

                # If move is a valid number, set move to its...
                #...corresponding attack
                if move in range(1, len(move_set) + 1):
                    move = move_set[list(move_set.keys())[move - 1]]
                    is_valid_move = True

                else:
                    error_message("INVALID NUMBER", f"You must either enter the move name or a number from 1 to {len(move_set)}")

            else:
                error_message("INVALID INPUT", f"{move} is not in your move set")
        else:
            error_message("NOTHING ENTERED", "You must enter a move to use")

        # Print the move's information or allow the move to be used
        if is_valid_move:
            if is_info_req:
                print('\n', move.format_self(), '\n')
                input('Press Enter to continue: ')

            else:
                break

    return move

# Allow the player to slect their move's target
def select_target(num_targets, possible_targets, move_info = None):

    chosen_trgts = []

    # Allows the user to select a number of targets equal to...
    #...whichever is lowest; num_targets or length of possible_targets
    for i in range(min( num_targets, len( possible_targets))):
        
        print("CHOOSE YOUR TARGET")
        time.sleep(0.25 / game_speed)

        is_valid_target = False
        while True:

            # Creates a dictionary which holds each potential target and a corresponding number
            targets_dict = {}
            for trgt_num, target in zip(range(len(possible_targets)), possible_targets):
                trgt_num += 1
                targets_dict[trgt_num] = all_players[target]
                print(f"{trgt_num}: {target}")
            
            new_trgt = input("Who would you like to target? Type \'INFO <choice>\' to see how accurate the move will be on them. ")
            is_info_req, new_trgt = check_if_info_req(new_trgt)

            # Decides if the user had entered a number or a name
            # Gives appropriate error messages if input is invalid
            # Validates input
            target_names = [target.name for target in targets_dict.values()]
            if new_trgt in target_names:
                new_trgt = all_players[new_trgt]
                is_valid_target = True

            elif new_trgt.isnumeric():
                new_trgt = int(new_trgt)

                if new_trgt in targets_dict:
                    
                    new_trgt = targets_dict[new_trgt]
                    is_valid_target = True
                
                else:       
                    error_message("INVALID NUMBER", f"You must only enter a number between 1 and {len(targets_dict)} (inclusive)")
                
            else:
                error_message("INVALID TARGET", f"You must enter a player name with correct casing or corresponding number")

            # If a valid target was chosen, print info or allow the move to progress
            if is_valid_target: 
                
                if is_info_req:
                    print('\n', new_trgt.format_self(), '\n')

                    # Print the liklihood of landing a hit on that target
                    if move_info != None:
                        usual_accuracy = format_accuracy(move_info[0].accuracy)
                        actual_accuracy = format_accuracy(str(get_true_accuracy(*move_info, new_trgt)))

                        print('Baseline chance of hitting: ', usual_accuracy)
                        print('Actual chance of hitting: ', actual_accuracy, '\n')
                    
                    input('Press Enter to continue: ')

                else:
                    chosen_trgts.append(new_trgt)
                    possible_targets.remove(new_trgt.name)
                    break

       
    
    return chosen_trgts

# Finds the real accuracy of a move based on it user and target
def get_true_accuracy(move, user, target):

    accuracy = move.accuracy
    move_type = move.move_type
    target_speed = target.speed
    user_speed = user.speed

    # Applies any necessary speed changes to the target
    target_speed = target.get_true_speed()
    
    # Applies any necessary speed changes to the user
    user_speed = user.get_true_speed()

    # If the move is used on themself, only the move's accuracy is taken into account
    if user.name == target.name:
        hit_chance = accuracy
    
    # If the move is ranged, the user's speed is not taken into account
    # However, the target's speed is also less impactful
    elif "Ranged" in move_type:
        hit_chance = accuracy - (target_speed / 6)
    
    else:
        hit_chance = accuracy - (target_speed / 3) + (user_speed / 3)

    hit_chance = int(round(hit_chance, 0))
    if hit_chance > 99:
        hit_chance = 99

    return hit_chance

# Decide whether the user landed or didn't land a hit on the target
def hit_or_miss(move, user, target):

    accuracy = move.accuracy
    move_type = move.move_type
    crit_info = move.crit_info
    target_speed = target.speed
    user_speed = user.speed

    hit = True
    if accuracy != True:

        # Calculate real chance of landing a hit
        hit_chance = get_true_accuracy(move, user, target)
        hit = False

        # If the hit chance (%) is below the generated number, it misses...
        # ... otherwise it hits
        roll = random.randint(1, 100)
        if roll >= hit_chance:
            hit = False
        
        else:
            hit = True

        #print(f"ROLL: {roll}/ {hit_chance}. Hit: {hit}")

    # Checks if a crit is possible. If so, use RNG to generate...
    #...whether the hit was a critical hit
    crit = False
    if crit_info != False:
        
        crit_chance = crit_info["chance"]

        # The user's speed will increase the chance of a crit if the move is...
        #...neither ranged nor self-targetting
        if "Ranged" not in move_type and move.targets != "Self":
            crit_chance += user.get_true_speed() / 10
        
        crit_chance = int(round(crit_chance, 0))
        roll = random.randint(1, 100)

        if  roll > crit_chance:
            crit = False

        else:
            crit = True

        #print(f"CRIT ROLL: {roll}/ {crit_chance}. Crit: {crit}")

    return hit, crit

# Executes a move regardless of accuracy
def execute_move(move, user, target, crit):

    # If the move doesn't do anything (right now), print a default message
    if len(move.effect) == 0:
        msg = 'He\'s just standing there... MENACINGLY'
        
        print(msg)
        time.sleep(1 / game_speed)

    # Apply all effects from the used move
    for effect in move.effect:

        if user.name == target.name:
            target_name = "themself"

        else:
            target_name = target.name

        # Stores the properties of an effect, e.g., {"Damage": {"value": 10}}
        effect_props = move.effect[effect]
        
        # Apply damage
        if effect == "Damage":

            damage = effect_props["value"]

            # Checks for any status effects that affect the damage output
            for status_effect in user.status_fx:

                if status_effect["name"] == "+Attack":
                    damage *= status_effect["multiplier"]

            if crit == True:

                damage *= move.crit_info["crit_effect"]
                damage = int(round(damage, 0))

                damage = target.inflict_damage(damage)
                msg = f"*** {user.name} landed a critical hit on {target_name} with {move.name}, causing {damage} damage! ***"
                
            else:
                damage = target.inflict_damage(damage)
                msg = f"{user.name} hit {target_name} with {move.name}, causing {damage} damage!"


        # Apply healing
        elif effect == "Heal":

            heal = effect_props["value"]

            if crit == True:

                heal *= move.crit_info["crit_effect"]
                heal = int(round(heal, 0))

                msg = f"*** {user.name} healed themself for {heal} HP! ***"
                
            else:
                msg = f"{user.name} healed themself for {heal} HP"

            target.heal(heal)

        # Apply attack modifiers
        elif effect == "+Attack" or effect == "-Attack":
            
            percentage = effect_props["percentage"]
            multiplier = (percentage / 100) + 1
            duration = effect_props["duration"]

            if crit == True:
                multiplier *= move.crit_info["crit_effect"]

                multiplier = int(round(multiplier, 2))

                if multiplier < 1:
                    effect = "-Attack"
                
                else:
                    effect = "+Attack"

                msg = f"*** {user.name} gave {target_name} {effect}(x{multiplier}) ***"
            
            else:
                if multiplier < 1:
                    effect = "-Attack"
                
                else:
                    effect = "+Attack"

                msg = f"{user.name} gave {target_name} {effect}(x{multiplier})"
            
            target.add_status_effect(effect, multiplier = multiplier, remaining_turns = duration)
            

        # Apply speed modifiers
        elif effect == "+Speed" or effect == "-Speed":

            reverse_speed = lambda effect: "-Speed" if effect == "+Speed" else "+Speed" if effect == "-Speed" else effect

            speed_change = effect_props["value"]
            duration = effect_props["duration"]

            if crit == True:
                speed_change *= move.crit_info["crit_effect"]

                speed_change = int(round(speed_change, 0))

                # If speed_change is negative, change the effect to "-Speed" and...
                #...use the positive version of speed_change
                if speed_change < 0:
                    effect = reverse_speed(effect)
                    speed_change = -speed_change

                msg = f"*** {user.name} gave {target_name} {effect}({speed_change}) ***"
            
            else:
                if speed_change < 0:
                    effect = reverse_speed(effect)
                    speed_change = -speed_change
                msg = f"{user.name} gave {target_name} {effect}({speed_change})"

            target.add_status_effect(effect, value = speed_change, remaining_turns = duration)

        # Apply defense modifiers
        elif effect == "Protection" or effect == "Weakness":

            if effect == "Protection":
                percentage = effect_props["value"]

            elif effect == "Weakness":
                percentage = effect_props["value"] + 100
            
            multiplier = (percentage / 100)

            duration = effect_props["duration"]

            if crit == True:
                multiplier *= move.crit_info["crit_effect"]
                multiplier = int(round(speed_change, 0))

                msg = f"*** {target.name} will now take {multiplier}x damage! ***"

            else:
                msg = f"{target.name} will now take {multiplier}x damage!"
            
            target.add_status_effect(effect, multiplier = multiplier, remaining_turns = duration)

        elif effect == "Burning":
            burn_dmg = effect_props["value"]
            duration = effect_props["duration"]

            if crit == True:
                burn_dmg *= move.crit_info["crit_effect"]
            
                msg = f"*** {user.name} inflicted {target_name} with Burning ({burn_dmg}) ***"
            
            else:
                msg = f"{user.name} inflicted {target_name} with Burning ({burn_dmg})"

            target.add_status_effect(effect, value = burn_dmg, remaining_turns = duration)


        if len(msg) > 0:
            print(msg)
            time.sleep(1 / game_speed)
    

# Calculates whether a move crits, hits, or misses, and executes it...
#...on each target
def attempt_move(move, user, targets):
    for target in targets:

        # Find whether the move lands and if it is a critical hit
        hit, crit = hit_or_miss(move, user, target)

        if hit == True:
        
            execute_move(move, user, target, crit)
    
        else:

            # Executes only if the move misses
            print(f"{user.name} missed {target.name} with {move.name}")
            time.sleep(1 / game_speed)

        # 'Kill' the player if their health is below 1
        if target.health < 1:
            remove_player(target)

            print(f"{target.name} is down!")
            time.sleep(1 / game_speed)

# Remove a player from the game
def remove_player(player):
    global active_players

    active_players.remove(player.name)


# All moves
# Name, type, effect {effect: {property: value}}, accuracy %, crit_info {chance, effect}, targets, description
# ATK- Defines a move which will be used to attack others
# EFX- Defines a move which will be used to apply status FX to one's self

ATK_sword_slash = Move(
    name = "Sword slash",
    move_type = "Melee",
    effect = {"Damage": {"value": 20}},
    accuracy = 90,
    crit_info = {"chance": 20, "crit_effect": 1.5},
    targets = 1,
    description = "Deals moderate damage to 1 opponent"
)

ATK_whirlwind_slash = Move(
    name = "Whirlwind slash",
    move_type = "Melee",
    effect = {"Damage": {"value": 10}},
    accuracy = 75,
    crit_info = {"chance": 20, "crit_effect": 1.5},
    targets = 2,
    description = "Deals weak damage to 2 opponents"
)

ATK_hamstring_slash = Move(
    name = "Hamstring slash",
    move_type = "Melee",
    effect = {
        "Damage": {"value": 10},
        "-Speed": {"value": 15, "duration": 2}
    },
    accuracy = 85,
    crit_info = {"chance": 10, "crit_effect": 1.5},
    targets = 1,
    description = "Deals weak damage to 1 opponent and moderately slows them down for the next 2 turns"
)

ATK_fireball = Move(
    name = "Fireball",
    move_type = "Spell, Ranged, Fire",
    effect = {
        "Damage": {"value": 25},
        "Burning": {"value": 5, "duration": 3}
    },
    accuracy = 70,
    crit_info = False,
    targets = 1,
    description = "Deals heavy ranged damage and inflicts burning (5) for 3 turns but has a high chance to miss"
)

ATK_lightning_bolt = Move(
    name = "Lightning bolt",
    move_type = "Spell, Ranged, Electric",
    effect = {
        "Damage": {"value": 40},
        "-Speed": {"value": 20, "duration": 3}
    },
    accuracy = 95,
    crit_info = {"chance": 15, "crit_effect": 1.3},
    targets = 1,
    description = "Takes 2 turns to charge but deals 40 damage and gives the target -Speed (20) for 3 turns",
    stagger = [2, True]
)

ATK_flying_kick = Move(
    name = "Flying kick",
    move_type = "Melee",
    effect = {"Damage": {"value": 15}},
    accuracy = 99,
    crit_info = {"chance": 15, "crit_effect": 1.2},
    targets = 1,
    description = "Performs a single flighty kick against an opponent. Deals weak damage but almost guaranteed to hit its target"
)

ATK_pressure_points = Move(
    name = "Pressure points",
    move_type = "Melee",
    effect = {
        "Damage": {"value": 15},
        "Weakness": {"value": 30, "duration": 2}
    },
    accuracy = 70,
    crit_info = False,
    targets = 1,
    description = "Presses on specific points on the opponent's body to make them take more damage for 2 turns"
)

EFX_rallying_cry = Move(
    name = "Rallying cry",
    move_type = "Spell",
    effect = {"+Attack": {"percentage": 50, "duration": 2}},
    accuracy = True,
    crit_info = False,
    targets = "Self",
    description = "Increases your own attack damage by 50% for the next 2 turns"
)

EFX_healing_chi = Move(
    name = "Healing chi",
    move_type = "Spell",
    effect = {"Heal": {"value": 5}},
    accuracy = True,
    crit_info = {"chance": 30, "crit_effect": 5},
    targets = "Self",
    description = "Heals you for 5 HP. Has a 30% chance to heal you for 5x the normal amount"
)

EFX_time_warp = Move(
    name = "Time warp",
    move_type = "Spell",
    effect = {"+Speed": {"value": 30, "duration": 1}},
    accuracy = True,
    crit_info = {"chance": 50, "crit_effect": -0.5},
    targets = "Self",
    description = "Slows down time for the mage, increasing their speed by 30. Small chance to mess up and reduce their speed instead"
)

EFX_mana_shield = Move(
    name = "Mana shield",
    move_type = "Spell",
    effect = {"Protection": {"value": 50, "duration": 0}},
    accuracy = True,
    crit_info = False,
    targets = "Self",
    description = "Forms a protective shield to block 50% of all damage for 1 turn"
)

EFX_literally_nothing = Move(
    name = "Literally nothing",
    move_type = "Melee",
    effect = {},
    accuracy = True,
    crit_info = False,
    targets = "Self",
    description = "Does nothing"
)

# Define all_var separately from globals() to prevent unexpected behaviour when iterating and altering
all_moves = []
all_var = globals().copy()

# Automatically add all moves to all_moves by checking for an ATK or EFX prefix
for var in all_var:
    if "ATK" in var or "EFX" in var:
        all_moves.append(globals()[var])

del all_var
""" 
{"Damage": {"value": 40}, "-Speed": {"value": 20, "duration": 3}}
{"Damage": {"value": 15}, "Weakness": {"value": 30, "duration": 2}} """
# All classes
all_classes = {}

all_classes["Warrior"] = Attack_Class("Warrior", [ATK_sword_slash, ATK_whirlwind_slash, ATK_hamstring_slash, EFX_rallying_cry], 50, 100)
all_classes["Mage"] = Attack_Class("Mage", [ATK_fireball, ATK_lightning_bolt, EFX_mana_shield, EFX_time_warp], 50, 80)
all_classes["Monk"] = Attack_Class("Monk", [ATK_flying_kick, ATK_pressure_points, EFX_healing_chi], 60, 100)
#all_classes["God"] = Attack_Class("God", all_moves, 50, 100)
#all_classes["Test"] = Attack_Class("Test", [ATK_sword_slash, ATK_lightning_bolt, EFX_literally_nothing], 50, 100)

# Prevents the main program from running if it is not being run directly
if __name__ == "__main__":
    # Makes a Player class character for each name entered
    input("Enter each player's name below. \nOnce each name is entered, leave the input blank and press Enter. \nTo use default players, type \'default<number of players>\'. \nPress Enter to continue ")

    while True:
        name = input("Enter a name: ")

        # Checks that the user entered a name
        # If the player name is not already present, ask for their class...
        #... and add them to the all_players dictionary

        if name != "":
            
            # If the first part of a name input is the default trigger, use default players
            default_trigger = "default"
            def_trig_length = len(default_trigger)
            use_default = name[0:def_trig_length] == default_trigger

            if use_default:
                try:
                    # Get number of defaults from end of user's input
                    num_defaults = int(name[def_trig_length:])

                except:
                    pass
                    
                else:

                    try:
                        # Define player generator and create a number of default players...
                        #... equal to the number entered after the default trigger phrase
                        default_player_generator = default_players()
                        
                        for i in range(num_defaults):
                            while True:
                                name, atk_class = next(default_player_generator)

                                atk_class = all_classes[atk_class]

                                # Only add the name if it doesn't already exist
                                if name not in all_players:
                                    print(add_new_player(name, atk_class))
                                    time.sleep(0.25 / game_speed)
                                    break

                    # Print an error if the generator has reached the end of its name list
                    except StopIteration:
                        error_message("NO MORE DEFAULTS", "No more default players can be added")

                use_default = False

            else:
                # Only add the player if their name isn't already in use
                if name not in all_players:
                    
                    # Forces the user to enter either a class name or its corresponding number
                    while True:
                        for i, class_name in zip(range(len(all_classes)), all_classes):

                            print(f"{i + 1}: {class_name}")

                        atk_class = input(f"Which class is {name}? ")

                        # If they entered a class name, add the person as that class
                        if atk_class in all_classes:
                            atk_class = all_classes[atk_class]
                            all_players[name] = Player(name, atk_class)
                            break 
                        
                        # If they didn't enter a class name, check if they entered a number
                        # If so, add them as the corresponding class 
                        elif atk_class.isnumeric():
                            atk_class = int(atk_class)
                            if atk_class in range(1, len(all_classes) + 1):
                                atk_class = list(all_classes.values())[atk_class - 1]
                                
                                print(add_new_player(name, atk_class))
                                break

                            else: 
                                error_message("INVALID CLASS", f"You must enter either a class name or a number from 1 to {len(all_classes)}")

                        else:
                            error_message("IVALID CLASS", f"You must enter one of the following: {'/ '.join(all_classes)}")
            
                else:
                    error_message("INVALID PLAYER NAME", "You cannot enter the same name more than once")
        else:
            if len(all_players) >= 2:
                break
            
            else:
                error_message("INVALID PLAYER COUNT", "You must enter 2 or more players")

    # Stores the names of all players which are still alive
    active_players = list(all_players.keys())
    round_count = 0

    # Keeps making new rounds until there is one player left
    while True:
        
        # If there is only 1 player left, they win
        if len(active_players) == 1:
                print("\n=======================================")
                print(f"{active_players[0]} wins!\n")
                exit()

        # Increments the round counter and starts a new round
        round_count += 1
        print(f"\n========== Round {round_count} ==========")
        time.sleep(0.5 / game_speed)

        # Gives each active player a turn each round
        for player in active_players:
            player = all_players[player]

            player.new_turn()

            # Print the player's summary
            print(f"\n------ {str(player)}'s turn ------")
            for p in active_players:
                print(all_players[p].format_self())
                time.sleep(0.25 / game_speed)


            print()
            time.sleep(0.5 / game_speed)

            # Prints a status update for each staggered move and blocks using other moves if necessary
            block_use_move = False
            for i, stag_move in zip(range(len(player.staggered_moves)), player.staggered_moves):
            
                turns = stag_move['remaining_turns']

                stagger_complete = turns <= 0
                
                # If a move is ready to use, force the player to use it 
                if stagger_complete == True:

                    attempt_move(stag_move['move'], player, stag_move['targets'])

                    del player.staggered_moves[i]
                
                else:
                    print(f'{str(player)} is charging a {stag_move["move"].name}')
                    time.sleep(1 / game_speed)

                if stag_move['block_use_move'] == True:
                    block_use_move = True

            # Allow the player to choose a move to use...
            #... if they aren't blocked from doing so
            if block_use_move != True:

                move = select_move(player)
                print()

                # Determine who will be targeted with the move
                if move.targets == "Self":
                    
                    targets = [player]

                elif move.targets == "All":
                    targets = active_players.copy()
                
                elif move.targets == "All others":
                    targets = active_players.copy()
                    targets.remove(player.name)

                # If needed, allow the user to select all required targets
                elif isinstance(move.targets, int): 
                    possible_targets = active_players.copy()
                    possible_targets.remove(player.name)

                    targets = select_target(move.targets, possible_targets, (move, player))
                    print()

                if move.stagger == None:

                    attempt_move(move, player, targets)

                else:
                    player.add_staggered_move(move, player, targets, move.stagger)

    # TO DO ------------------------------------------------------
    # Modualarise project to include multiple files
    # Remove over-nesting
    # Make attacks be able to have multiple targets
    # Change target info to include a % after actual chance to hit
    # Improve UX 
    # Complete 3 other classes 
