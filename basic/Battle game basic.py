import time

all_players = {}

# Used for all player characters
class Player:

    # Sets the name and stats for each person
    def __init__(self, name, health, strength):
        print(f"{name} is joining the battle! ")

        all_players[name] = self
        self.name = name

        self.stats = {
            "Health": health,
            "Strength": strength 
        }

    def __getitem__(self, key):
        if key in self.stats:
            return self.stats[key]
        
    # Displays the player's HP and strength when printed as a string
    def __repr__(self):
        return f"{self.name}\nHP: {self.stats['Health']}\nStrength: {self.stats['Strength']}"
    
    # Obtains the player's health stat
    def getHealth(self):
        return self.stats["Health"]

    # Obtains the player's strength stat
    def getStrength(self):
        return self.stats["Strength"]
    
    # Inflicts damage on the player
    def damage(self, damage):
        self.stats["Health"] -= damage


# Makes a Player class character for each name entered
input("Enter each player's name. Once each name is entered, leave the question blank and press Enter. Press Enter to continue ")

while True:
    name = input("Enter a name: ")

    if name != "":
        all_players[name] = Player(name, 100, 30)
    
    else:
        break

# Stores the names of all players which are still alive
active_players = list(all_players.keys())
round = 0

# Keeps making new rounds until there is one player left
while True:
    
    # If there is only 1 player left, they win
    if len(active_players) == 1:
            print(f"{active_players[0]} wins!\n")
            exit()

    # Increments the round counter and starts a new round
    round += 1
    print(f"\n========== Round {round} ==========")
    for player in active_players:
        player = all_players[player] 

        print(f"{player.name}: {player.getHealth()} HP")

    for player in active_players:
        player = all_players[player]

        print(f"\n------ {player.name}'s turn ------")
    
        # Allows the user to choose which other player to attack
        while True:
            target = input("Who would you like to attack? ")

            # Checks that the chosen target is present in the game
            # If so, checks that the chosen target is not themself
            if target in active_players:
                if target != player.name:
                    target = all_players[target]
                    target.damage(player.getStrength())

                    print(f"{target.name} was inflicted with {player.getStrength()} damage")

                    # Removes the player from the game if their health reaches 0
                    if target.getHealth() <= 0:
                        active_players.remove(target.name)
                        print(f"{target.name} is down!")
                        time.sleep(1)

                    break


                else:
                    input("You cannot attack yourself. Press Enter to continue")

            else:
                if target in all_players:
                    input(f"You cannot attack {target} because they are down. Press Enter to continue ")
                
                else:
                    input(f"There is no player called '{target}'. Press Enter to continue ")

    
