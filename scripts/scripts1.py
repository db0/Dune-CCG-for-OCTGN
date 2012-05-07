    # Python Scripts for the Dune CCG definition for OCTGN
    # Copyright (C) 2012  Konstantine Thoukydides

    # This python script is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this script.  If not, see <http://www.gnu.org/licenses/>.

Solaris = ("Solaris", "b30701c1-d925-45fc-afe4-6c341a103f32")
Spice = ("Spice", "491cf29f-224c-4d8b-8e2d-58467686be88")
Favor = ("Favor", "6ed72fed-4a63-4f38-95bb-424cbbcdd427")
Deferment_Token = ("Deferment_Token", "f8f34145-60a8-4d2c-92e9-25824982944e")
Assembly = ("Imperial Assembly", "a5634dc5-ffd0-4428-95b5-13c6bb3ff00d")
Program = ("Program Token", "e66b8122-e98a-48bb-a9ba-991fde33d01c")

phases = [
    '{} is currently in the Pre-game Setup Phase'.format(me),
    "It is now Opening Interval. Disengage all cards then add Deferment Tokens and finally Assign Initiative",
    "It is now House Interval",
    "It is now Closing Interval. Perform Assembly Administration and then Hand Administration"]

#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------

import re
import time

loud = 'loud' # So that I don't have to use the quotes all the time in my function calls
silent = 'silent' # Same as above
Xaxis = 'x'  # Same as above
Yaxis = 'y'     # Same as above
DoesntDisengageColor = "#ffffff"


#---------------------------------------------------------------------------
# Global variables
#---------------------------------------------------------------------------

PLS = None # Stands for PLayerSide. Variable to keep track on which side each player is. 
playeraxis = None # Variable to keep track on which axis the player is
handsize = 7 # Used when automatically refilling your hand.
assemblysize = 3 # used when automatically refilling your assembly.
favorBought = 0
CHOAMDone = 0
DeployedDuneEvent = 0
DeployedImperiumEvent = 0
allegiances =[] # List to keep track of the player's allegiances.
totalevents = 0 # Variable to allow me to move events a bit to avoid hiding on top of exitisting ones.
totalprogs = 0 # Variable to allow me to move programs a bit to avoid hiding on top of exitisting ones.
totalholdings = 0
totalpersonas = 0
inactiveProgram = { }
assemblyCards = [ ]
Automation = True
CROEsnapshot = 0
#---------------------------------------------------------------------------
# General functions
#---------------------------------------------------------------------------

def num (s): 
# This function reads the value of a card and returns an integer. For some reason integer values of cards are not processed correctly
# see bug 373 https://octgn.16bugs.com/projects/3602/bugs/188805
# This function will also return 0 if a non-integer or an empty value is provided to it as it is required to avoid crashing your functions.
#   if s == '+*' or s == '*': return 0
   if not s: return 0
   try:
      return int(s)
   except ValueError:
      return 0

def addPos(num): # Quick function to add a + next to prositive numbers
   if num > 0: return '+{}'.format(num)
   else: return num

def chooseSide(): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global PLS, playeraxis
   if PLS == None:  # Has the player selected a side yet? If not, then...
      if table.isTwoSided():
         if me.hasInvertedTable():
            playeraxis = Yaxis
            PLS = -1
         else:
            playeraxis = Yaxis
            PLS = 1
      else:
         askside = askInteger("On which side do you want to setup?: 1 = Right, 2 = Left, 3 = Bottom, 4 = Top, 0 = None (All your cards will be put in the middle of the table and you'll have to arrange them yourself", 1) # Ask which axis they want,
         if askside == 1:
            playeraxis = Xaxis
            PLS = 1
         elif askside == 2:
            playeraxis = Xaxis
            PLS = -1
         elif askside == 3:
            playeraxis = Yaxis
            PLS = 1
         elif askside == 4:
            playeraxis = Yaxis
            PLS = -1
         else:
            playeraxis = None
            PLS = 0

def chkOut(globalvar): # A function which safely grabs a global variable by making sure nobody else is currently modifying it.
   retry = 0
   while getGlobalVariable(globalvar) == 'CHECKOUT':
      if retry == 2: 
         whisper("Global variable checkout failed after 3 tries. Another player must by doing something! Please try again later.")
         return 'ABORT'
      whisper("Global variable currently in use, retrying...")
      time.sleep(1)
      retry += 1
   globalVar = getGlobalVariable(globalvar)
   setGlobalVariable(globalvar, 'CHECKOUT')
   return globalVar

def chooseWell(limit, choiceText, default = None):
   if default == None: default = 0# If the player has not provided a default value for askInteger, just assume it's the max.
   choice = limit # limit is the number of choices we have
   if limit > 1: # But since we use 0 as a valid choice, then we can't actually select the limit as a number
      while choice >= limit:
         choice = askInteger("{}".format(choiceText), default)
         if not choice: return False
         if choice > limit: whisper("You must choose between 0 and {}".format(limit - 1))
   else: choice = 0 # If our limit is 1, it means there's only one choice, 0.
   return choice
   
#---------------------------------------------------------------------------
# Card Placement functions
#---------------------------------------------------------------------------

def cwidth(card, divisor = 10):
# This function is used to always return the width of the card plus an offset that is based on the percentage of the width of the card used.
# The smaller the number given, the less the card is divided into pieces and thus the larger the offset added.
# For example if a card is 80px wide, a divisor of 4 will means that we will offset the card's size by 80/4 = 20.
# In other words, we will return 1 + 1/4 of the card width. 
# Thus, no matter what the size of the table and cards becomes, the distances used will be relatively the same.
# The default is to return an offset equal to 1/10 of the card width. A divisor of 0 means no offset.
   if divisor == 0: offset = 0
   else: offset = card.width() / divisor
   return (card.width() + offset)

def cheight(card, divisor = 10):
   if divisor == 0: offset = 0
   else: offset = card.height() / divisor
   return (card.height() + offset)

def yaxisMove(card, force = 'no'):
# Variable to move the cards played by player 2 on a 2-sided table, more towards their own side. 
# Player's 2 axis will fall one extra card length towards their side.
# This is because of bug #146 (https://github.com/kellyelton/OCTGN/issues/146)
   if me.hasInvertedTable() or (playeraxis == Yaxis and PLS == -1): cardmove = cheight(card)
   elif force == 'force': cardmove = -cheight(card)
   else: cardmove = 0
   return cardmove

def placeCard(card,type = None):
# This function automatically places a card on the table according to what type of card is being placed
# It is called by one of the various custom types and each type has a different value depending on if the player is on the X or Y axis.
   global totalprogs, totalholdings, totalpersonas
   if playeraxis == Xaxis:
      if type == 'SetupHomeworld':
         card.moveToTable(homeDistance(card), 0) # We move it to one side depending on what side the player chose.
      if type == 'SetupDune':
         card.moveToTable(homeDistance(card), cheight(card)* PLS) # We move it to one side depending on what side the player chose.
         card.isFaceUp = False
      if type == 'SetupProgram':          # We move them behind the homeworld
         card.moveToTable(homeDistance(card) - cardDistance(card) / 2 - (PLS * totalprogs * 20), 0)
         card.sendToBack()
         card.isFaceUp = False
         totalprogs += 1
      if type == 'PlayEvent': # Events are placed subdued
         card.moveToTable(homeDistance(card) + PLS * totalevents * 35, cheight(card)* -2 * PLS + PLS * totalevents * -35) 
         card.isFaceUp = False
      if type =='DeployHolding':
         card.moveToTable(homeDistance(card) - cardDistance(card), -cheight(card) * PLS + totalholdings * cheight(card)) # We move them just in front and to the side of the player's homeworld
         totalholdings += 1
         if totalholdings == 5: totalholdings = -4
      if type =='DeployPersona':
         card.moveToTable(homeDistance(card) - 2 * cardDistance(card), totalpersonas * cheight(card)) # We move them just ahead of the player's homeworld, as some distance.
         totalpersonas += 1
         if totalpersonas == 5: totalpersonas = -5
      if type =='DeployResource':
         card.moveToTable(cardDistance(card), cheight(card) * PLS) # We move it close to the table center, towards the player's side.
         card.sendToBack()
   elif playeraxis == Yaxis:
      if type == 'SetupHomeworld':
         card.moveToTable(0 ,homeDistance(card) - yaxisMove(card,'force')) 
      if type == 'SetupDune':
         card.moveToTable(cwidth(card)* PLS,homeDistance(card) - yaxisMove(card,'force')) 
         card.isFaceUp = False
      if type == 'SetupProgram': 
         card.moveToTable(0 ,homeDistance(card) - cardDistance(card) / 4 - (PLS * totalprogs * 30) - yaxisMove(card,'force'))
         card.sendToBack()
         card.isFaceUp = False
         totalprogs += 1
      if type == 'PlayEvent':
         card.moveToTable(cwidth(card)* -4 * PLS + PLS * totalevents * -35,homeDistance(card) + PLS * totalevents * 35 - yaxisMove(card)) 
         card.isFaceUp = False
      if type =='DeployHolding':
         card.moveToTable(-cwidth(card) * PLS + totalholdings * cheight(card), homeDistance(card) - cardDistance(card)) # We move them just in front and to the side of the player's homeworld
         totalholdings += 1
         if totalholdings == 7: totalholdings = -4
      if type =='DeployPersona':
         card.moveToTable(totalpersonas * cheight(card),homeDistance(card) - 2 * cardDistance(card)) # We move them just ahead of the player's homeworld, as some distance.
         totalpersonas += 1
         if totalpersonas == 7: totalpersonas = -5
      if type =='DeployResource':
         card.moveToTable(cwidth(card) * PLS,cardDistance(card)) # We move it close to the table center, towards the player's side.
         card.sendToBack()
   else: card.moveToTable(0,0)

def homeDistance(card):
# This function returns the distance from the middle each player's homeworld will be setup towards their PLS. 
# This makes the code more readable and allows me to tweak these values from one place
   if table.isTwoSided(): return (PLS * cheight(card) * 3) # players on an inverted table are placed half a card away from their edge.
   else:
      if playeraxis == Xaxis:
         return (PLS * cwidth(card) * 11) # players on the X axis, are placed 10 times a card's width towards their side (left or right)
      elif playeraxis == Yaxis:
         return (PLS * cheight(card) * 4 - yaxisMove(card)) # players on the Y axis, are placed 4 times a card's height towards their side (top or bottom)

def cardDistance(card):
# This function returns the size of the card towards a player's side. 
# This is useful when playing cards on the table, as you can always manipulate the location
#   by multiples of the card distance towards your side
# So for example, if a player is playing on the bottom side. This function will always return a positive cardheight.
#   Thus by adding this in a moveToTable's y integer, the card being placed will be moved towards your side by one multiple of card height
#   While if you remove it from the y integer, the card being placed will be moved towards the centre of the table by one multiple of card height.
   if playeraxis == Xaxis:
      return (PLS * cwidth(card))
   elif playeraxis == Yaxis:
      return (PLS * cheight(card))

#---------------------------------------------------------------------------
# Conditions Check General Functions
#---------------------------------------------------------------------------

def eventDeployTypeChk(subtype): # Check if the conditions to deploy an event are fulfilled
   global DeployedDuneEvent, DeployedImperiumEvent  
   if re.search(r'Imperium', subtype): # Imperium events can only be played if you control a homeworld, or Dune and only one per round per player.
      if Homeworlds() == 0:
         if not confirm("You're not allowed to deploy an Imperium Event without controlling a Homeworld . Bypass?"): 
            notify("{} is deploying an Imperium event, even though they control no Homeworld.".format(me))
            return 'NOK' 
      if DeployedImperiumEvent == 0: # If no Imperium event has been played this turn, just mark one as played and continue.
         DeployedImperiumEvent = 1
         return 'OK'
      elif confirm("You have already deployed one Imperium event this turn. Are you sure you are allowed to deploy another?"):
         return 'Extra' # If one has been played this turn, ask the player to confirm (in case they have a card effect) and continue or not accordingly.
      else: return 'NOK'
   elif re.search(r'Dune', subtype): # Dune events can only be played if you control a Dune fief, or Dune and only one per round per player.
      if DuneFiefs() == 0:
         if not confirm("You're not allowed to deploy a Dune Event without controlling a Dune fief. Bypass?"): 
            notify("{} is deploying a Dune event, even though they control no Dune fief.".format(me))
            return 'NOK' 
      if DeployedDuneEvent == 0:
         DeployedDuneEvent = 1
         return 'OK'
      elif confirm("You have already deployed one Dune event this turn. Are you sure you are allowed to deploy another?"):
         return 'Extra'
      else: return 'NOK'

def DuneFiefs(DuneOnly = False): # This function goes through your cards on the table and looks to see if you control any Dune Fiefs.
   myCards = [c for c in table
      if c.controller == me
      and c.isFaceUp
      and ((re.search(r'Dune Fief', c.Subtype) and not DuneOnly) or c.model == '2037f0a1-773d-42a9-a498-d0cf54e7a001')] # Dune itself is also a Dune Fief.
   return len(myCards)

def Homeworlds(): # This function goes through your cards on the table and looks to see if you control any Homeworlds.
   HomeNR = 0
   myCards = (c for c in table
      if c.controller == me
      and c.isFaceUp
      and (re.search(r'Homeworld', c.Subtype) or c.model == '2037f0a1-773d-42a9-a498-d0cf54e7a001')) # Dune itself is also a Homeworld.
   for mycard in myCards: HomeNR += 1
   return HomeNR


def noteAllegiances(): # This function checks every card in the Imperial Deck and makes a list of all the available allegiances.
   global allegiances # A global list that will containing all the allegiances existing in a player's deck.
   for card in me.piles['Imperial Deck']: 
      # Ugly hack follows. We need to move each card in the discard pile and then back into the deck because OCTGN won't let us peek at cards in facedown decks.
      card.moveTo(me.piles['Imperial Discard']) # Put the card in the discard pile in order to make its properties visible to us.
      if len(players) > 1: random = rnd(1,100) # Fix for multiplayer only. Makes Singleplayer setup very slow otherwise.
      if card.model == '2037f0a1-773d-42a9-a498-d0cf54e7a001':  # If the player moved dune put Dune by mistake to their Deck, move it to their hand to be placed automatically.
         card.moveTo(me.piles['Imperial Discard'])
         whisper("Dune found in your Imperial Deck. Discarding. Please remove Dune from your Imperial Deck during deck construction!")
         continue
      if card.Allegiance not in allegiances and card.Allegiance != 'None' and card.Allegiance != '': # If the allegiance is not neutral and not in our list already...
         allegiances.append(card.Allegiance)                                     # Then add it at the next available position
      card.moveToBottom(me.piles['Imperial Deck'])
   if chkAdversaries() != 'OK':
      notify("Faction Adversaries found within {}'s Deck. Deck seems to be illegal!".format(me))

def chkAdversaries(): # Check if there are any adversaties of factions in the Imperial deck. (Check page 4 of the ToT Rulebook.)
   global allegiances
   for allegiance in allegiances:
      if allegiance == 'The Fremen' and 'House Harkonnen' in allegiances: return 'conflict'
      elif allegiance == 'The Spacing Guild' and ('The Bene Gesserit Sisterhood' in allegiances or 'Dune Smugglers' in allegiances): return 'conflict'
      elif allegiance == 'House Atreides' and ('House Harkonnen' in allegiances or 'House Corrino' in allegiances): return 'conflict'
      elif allegiance == 'House Corrino' and 'House Atreides' in allegiances: return 'conflict'
      elif allegiance == 'House Harkonnen' and ('House Atreides' in allegiances or 'The Fremen' in allegiances): return 'conflict'
      elif allegiance == 'The Bene Gesserit Sisterhood' and 'The Spacing Guild' in allegiances: return 'conflict'
      elif allegiance == 'Dune Smugglers' and 'The Spacing Guild' in allegiances: return 'conflict'
      elif allegiance == 'The Spice Miners Guid' and 'The Water Sellers Union' in allegiances: return 'conflict'
      elif allegiance == 'The Water Sellers Union' and 'The Spice Miners Guid' in allegiances: return 'conflict'
   return 'OK'

#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def switchAutomation(group,x=0,y=0,command = 'Off'):
    global Automation
    if Automation and command != 'On':
        notify ("{}'s automations are OFF.".format(me))
        Automation = False
    else:
        notify ("{}'s automations are ON.".format(me))
        Automation = True

def nextPhase(group, x = 0, y = 0):  
# Function to take you to the next phase. 
   mute()
   if shared.Phase == 3: 
      shared.Phase = 1 # In case we're on the last phase (Closing Interval), go back to the first game phase (Opening Interval)
   else: shared.Phase += 1 # Otherwise, just move up one phase
   showCurrentPhase()

def goToOpening(group, x = 0, y = 0): # Go directly to the Opening Interval
   mute()
   shared.Phase = 1
   showCurrentPhase()

def goToHouse(group, x = 0, y = 0): # Go directly to the House Interval
   mute()
   shared.Phase = 2
   showCurrentPhase()

def goToClosing(group, x = 0, y = 0): # Go directly to the Closing Interval
   mute()
   shared.Phase = 3
   showCurrentPhase()


def showCurrentPhase(): # Just say a nice notification about which phase you're on.
   notify(phases[shared.Phase].format(me))

def goToSetup(group, x = 0, y = 0):  # Go back to the Pre-Game Setup phase.
# This phase is not rotated with the nextPhase function as it is a way to basically restart the game.
# It also serves as a control, so as to avoid a player by mistake using the setup function during play.
   global PLS, playeraxis, handsize, assemblysize, favorBought, CHOAMDone, DeployedDuneEvent, DeployedImperiumEvent, allegiances, totalevents, inactiveProgram
   mute()
   PLS = None
   playeraxis = None
   handsize = 7
   assemblysize = 3
   favorBought = 0
   CHOAMDone = 0
   DeployedDuneEvent = 0
   DeployedImperiumEvent = 0
   allegiances =['','','',''] # List to keep track of the player's allegiances.
   shared.Phase = 0
   me.Spice = 0
   me.Solaris = 5
   me.Favor = 10
   me.Initiative = 0
   totalevents = 0
   totalprogs = 0
   setGlobalVariable("petitionedCard", "Empty") # Clear the shared variables.
   setGlobalVariable("passedPlayers", "[]")
   setGlobalVariable("defeatedPlayers", "[]")
   inactiveProgram.clear() # Clear the dictionary for reuse.
   assemblyCards[:] = [] # Empty the list.
   showCurrentPhase() # Remind the players which phase it is now

def flipCoin(group, x = 0, y = 0):
    mute()
    n = rnd(1, 10)
    if n < 6:
        notify("{} flips heads.".format(me))
    else:
        notify("{} flips tails.".format(me))

def petition(card, x=0, y=0): # An almost superfluous function that basically redirects to subdue( ) or placeBid(). It's purpose is that I can have the same menu action on both cards and table context menus.
   cardID = chkOut("petitionedCard") # A quick grab of the shared peti
   if cardID == 'ABORT': return # Leave if someone is already using it.
   setGlobalVariable("petitionedCard", cardID)
   if cardID != 'Empty': placeBid(table) # If the player used this action and there's a currently petitioning card, we assume they just wanted to bid.
   elif card.markers[Assembly] == 0: whisper("You can only use this action on Imperial Assembly cards")
   else: subdue(card)


def placeBid(group, x = 0, y = 0):
# This function does the following:
#* It Checks to see if the player has passed in this petition already
#* It check if they are the last player standing in the bidding process and if so, declare them as the winner and take appropriate action, depending on if they are the owner or contestor
#* If they are not the winner, then they can increase their bid for this petition, or pass.
   mute()
   highestbid = 0 # Variable tracking what the highest bid is
   playersInBid = 0 # Variable tracking how many players are still in the bid
   overdraft = False # Variable tracking if the player tried to bid more than the Solaris in their Bank
   costZeroCard = False # A variable to track if the petitioned card has 0 deployment cost and take it into account during checks
   ABORT = False
   cardID = chkOut("petitionedCard") # Grab the card ID being petitioned.
   if cardID == 'ABORT': return # Leave if someone is already using it.
   elif cardID == 'Empty':
      whisper("No petition seems to be in progress. Please use this action on a face-down assembly card to start one first.")
      setGlobalVariable("petitionedCard", cardID) # If we're going to return before the end of the function, we need to checkin, or the next functions will fail.
      return
   else: card = Card(int(cardID)) # to make things easier and more readable.
   if num(card.properties['Deployment Cost']) == 0: costZeroCard = True
   for player in players: # Mark what the highest bid is and see how many players are currently still bidding
      if player.Bid > highestbid: highestbid = player.Bid
      if player.Bid > 0: playersInBid += 1
   if playersInBid == 0 and card.owner == me: playersInBid = 1
   if playersInBid == 1 and (me.Bid > 0 or costZeroCard): # If there's just one player remaining in the bid and it's the current player, then it means he's the "last man standing" so they are the winner of the petition
      if confirm("You seem to have won this petition, is this correct?"): # But lets just make sure just in case...
         if card.owner == me: # if we're the petitioner
            if card.allegiance == allegiances[0]: # if the card is of our own allegiance, we can reduce the cost via favor
               FavorLost = -1
               while FavorLost < 0 or FavorLost > highestbid: # This loop is to prevent the user from putting a value higher than the bid and thus gaining solaris.
                  FavorLost = askInteger("You have the house advantage for this petition and can use favor to reduce the final cost.\n\nHow much favor do you want to spend?\n(Max {})?".format(highestbid), 0)
                  if FavorLost == None: FavorLost = 0
                  if FavorLost > highestbid: whisper("You cannot reduce the deployment cost to negative")
               if me.Solaris < highestbid: # if we don't have enough money to pay the cost, we need to lose favor.
                  FavorLost = highestbid - me.Solaris
               me.Solaris -= highestbid - FavorLost
               me.Favor -= FavorLost
               if FavorLost > 0: extraText = " and {} favor".format(FavorLost)
               else: extraText = ''
            elif card.allegiance in allegiances: # If the card if not of our allegiance, but is of a secondary house we're using, we need to pay one favor extra.
               FavorLost = 1
               if me.Solaris < highestbid:
                  FavorLost += highestbid - me.Solaris
               me.Favor -= FavorLost
               extraText = " and lost {} favor".format(FavorLost)
               FavorLost -= 1 # We need to reduce the favour by 1, because the one extra cost is penalty and shouldn't reduce the cost.
               me.Solaris -= highestbid - FavorLost
            else: # If the card is netural, then there's nothing special.
               FavorLost = 0
               if me.Solaris < highestbid:
                  FavorLost += highestbid - me.Solaris
               me.Favor -= FavorLost
               me.Solaris -= highestbid - FavorLost
               if FavorLost > 0: extraText = " and lost {} favor".format(FavorLost)
               else: extraText = ''
            notify("{} has successfully petitioned for {} with a final bid of {}. They have spent {} solaris{} to pay the deployment cost.".format(me, card, highestbid, highestbid - FavorLost, extraText))
            card.markers[Assembly] = 0
            placeCard(card, "Deploy{}".format(card.Type)) # We deploy the card depending on its type.
            assemblyCards.remove(card) # Remove the deployed card from the list of assembly cards
            card.orientation = Rot90
            chkDeployAutoscripts(card)
         else: # If we're a contesting player...
            ContestCost = highestbid - num(card.properties['Deployment Cost'])
            FavorLost = 0
            if me.Solaris < ContestCost: # If we can't pay the full cost, we need to pay the rest with favor.
               FavorLost -= ContestCost - me.Solaris
               extraText = " and {} favor".format(FavorLost)
            else: extraText = ''
            me.Solaris -= ContestCost
            notify("{} has paid {} Solaris{} to contest the deployment of {}. The house of {} cannot call any more Petitions this turn".format(me, ContestCost, extraText, card, card.owner))
            time.sleep(1)
            card.isFaceUp = False
            ### Add the defeated player to the list.
            chkVar = chkOut("defeatedPlayers")
            if chkVar == 'ABORT': return
            defeatedPL = eval(chkVar)
            defeatedPL.append(card.owner._id)
            setGlobalVariable("defeatedPlayers", str(defeatedPL))
         setGlobalVariable("petitionedCard", "Empty") # Clear the shared variables for use in the next petition. Always need to do this before a return.
         setGlobalVariable("passedPlayers", "[]")
         me.Bid = 0
         return
   chkVar = chkOut("passedPlayers") # Checkout the passedPlayers global variable, which is a list with the player IDs of all the players who have passed on this petition.
   if chkVar == 'ABORT': return
   passedPL = eval(chkVar) # We grab the variable in string format and use the eval() to make it a list
   if me._id in passedPL: # See if the current player has passed already, and if so, warn them but give a chance to re-enter the bid (say because of card effects or wrongly pressing 0)
      if not confirm("You have already passed this petition. You are not normally allowed to bid a petition you have passed on the bid.\n\nBypass?"): ABORT = True
      else: 
         notify("{} has re-enterred the bidding contest".format(me))
         passedPL.remove(me._id)
   if not ABORT:
      mybid = askInteger("What is your bid?\n\n[Currently highest bid is {} Solaris.]\n[Card Deployment Cost is {}].\n(Putting 0 will cancel the bid)".format(highestbid, card.properties['Deployment Cost']), 0)
      while 0 < mybid <= highestbid and highestbid > 0: 
         mybid = askInteger("You must bid higher then the current bid of {}. Please bid again.\n\n(0 will cancel the bid)".format(highestbid), 0)
         if mybid > me.Solaris: 
            if not confirm("You have bid more than your available Solaris in your bank. You're not normally allowed to do this, even if you would reduce it with favor.\n\nBypass?"): mybid = highestbid
            else: overdraft = True
      if mybid == 0 or mybid == None: 
         notify("{} has passed for this petition".format(me))
         passedPL.append(me._id)
         me.Bid = 0
      else:
         if overdraft: extraText = " by exceeding their banked Solaris"
         else: extraText =""
         notify("{} has increased the bid to {}{}".format(me, mybid,extraText))
         me.Bid = mybid
   setGlobalVariable("passedPlayers", str(passedPL))
   setGlobalVariable("petitionedCard", cardID)
   
#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def inspectCard(card, x = 0, y = 0): # This function shows the player the card text, to allow for easy reading until High Quality scans are procured.
   if card.Autoscript == "": ASText = "\n\nThis card is not Auto-Scripted!"
   else: ASText = "\n\nThis card is Auto-Scripted:\n[{}]".format(card.AutoScript)
   confirm("{}{}".format(card.Operation,ASText))

def engage(card, x = 0, y = 0, silent = False, force = False):
   mute()
   if force:
      if force == 'Engage' and card.orientation == Rot90: 
         notify("{} is already engaged. Please try again when it's been disengaged.".format(card))
         return 'ABORT'
      elif force == 'Disengage' and card.orientation == Rot0: 
         notify("{} is already disengaged. You can only take this action this card is engaged.".format(card))
         return 'ABORT'
   card.orientation ^= Rot90
   if card.orientation & Rot90 == Rot90: 
      if not silent: notify('{} engages {}'.format(me, card))
      if re.search('Desert', card.Subtype): autoscriptOtherPlayers('DesertEngaged')
   else: 
      if not silent: notify('{} disengages {}'.format(me, card))
   

def dueling(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify('{} declares a Dueling rite with {}'.format(me, card))
    else:
        notify('{} disengages {}'.format(me, card))

def battle(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify('{} declares a Battle rite with {}'.format(me, card))
    else:
        notify('{} disengages {}'.format(me, card))

def arbitration(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify('{} declares an Arbitration rite with {}'.format(me, card))
    else:
        notify('{} disengages {}'.format(me, card))

def intrigue(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify('{} declares an Intrigue rite with  {}'.format(me, card))
    else:
        notify('{} disengages {}'.format(me, card))

def subdue(card, x = 0, y = 0,  silent = False, force = False):
    mute()
    faceup = 0
    ABORT = False
    if force:
        if force == 'Subdue' and not card.isFaceUp: 
            notify("Target card is already subdued. Please try again when it's been deployed.")
            return 'ABORT'
        elif force == 'Deploy' and card.isFaceUp: 
            notify("Target card is already deployed. You can only take this action this card is subdued.")
            return 'ABORT'
        elif force =='Deploy':
            if card.markers[Assembly] == 1 and not confirm("Are you sure you want to force-deploy an Imperial Assembly card?"): return 'ABORT'
            card.isFaceUp = True
            chkDeployAutoscripts(card)
            if not silent: notify("{} deploys {}.".format(me, card))
            card.markers[Deferment_Token] = 0
            if re.search(r'Program', card.Subtype) and card.Type == 'Plan' and card.owner == me: inactiveProgram[card] = False        
    if not card.isFaceUp: # Horrible hack until the devs can allow me to look at facedown card properties.
        card.isFaceUp = not card.isFaceUp  # Gah!
        snapshot = card
        name = card.name
        type = card.Type
        subtype = card.Subtype
        cost = num(card.properties['Deployment Cost']) 
        card.isFaceUp = not card.isFaceUp # GAH!
    if card.markers[Assembly] == 0:
        if card.isFaceUp:
            if not silent: notify("{} subdues {}.".format(me, card))
            chkRemoveAutoscripts(card)
            card.isFaceUp = False
        elif type == 'Event': # Events have special deployment rules
            if card.markers[Deferment_Token] < cost or card.markers[Deferment_Token] == 0:
                if confirm("Events cannot normally be played unless they have equal or more deferment tokens than their deployment cost and at least one. \n\nAre you sure you want to do this?"):
                    deployCHK = eventDeployTypeChk(subtype)
                    if deployCHK != 'NOK': # Check if there's been any other events of the same typed played this turn by this player.
                        card.isFaceUp = True
                        if deployCHK == 'OK': notify("{} deploys {} with {} deferment tokens.".format(me, card, card.markers[Deferment_Token]))
                        else: notify("{} deploys another {} event - {} with {} deferment tokens.".format(me, subtype, card, card.markers[Deferment_Token]))
            else: 
                deployCHK = eventDeployTypeChk(subtype)
                if deployCHK != 'NOK': # Check if there's been any other events of the same typed played this turn by this player.
                    card.isFaceUp = True
                    if deployCHK == 'OK': notify("{} deploys {} with {} deferment tokens.".format(me, card, card.markers[Deferment_Token]))
                    else: notify("{} deploys another {} event - {} with {} deferment tokens.".format(me, subtype, card, card.markers[Deferment_Token]))
        elif searchUniques(card, name, 'deploy') == 'NOK': return # Check if the card is unique and in the table. If so, abort this function.
        elif searchNatives(subtype) == 'NOK': return # Check if the card is a native persona and if there's any dune fiefs in our control. If so, abort this function after a confirm.
        elif card.markers[Deferment_Token] == 0:
            if confirm("You cannot normally deploy cards with 0 deferment tokens. Bypass?"):
               notify("{} deploys {} which had 0 deferment tokens.".format(me, card))   
               card.isFaceUp = True
               chkDeployAutoscripts(card)
        elif card.markers[Deferment_Token] < cost:
            if confirm("Card has less deferment tokens than its deployment cost. Do you need to automatically pay the difference remaining from your treasury?"):
                if payCost(cost - card.markers[Deferment_Token]) == 'OK':
                    card.isFaceUp = True
                    chkDeployAutoscripts(card)
                    notify("{} pays {} and deploys {}.".format(me, cost - card.markers[Deferment_Token], card))
                    card.markers[Deferment_Token] = 0
            elif confirm("Do you want to deploy the card at no cost instead?"):
                card.isFaceUp = True
                chkDeployAutoscripts(card)
                notify("{} deploys {} at no cost (Card had {} less deferment tokens than its deployment cost).".format(me, card, cost - card.markers[Deferment_Token]))
                card.markers[Deferment_Token] = 0
        else:
            card.isFaceUp = True
            chkDeployAutoscripts(card)
            notify("{} deploys {}.".format(me, card))
            card.markers[Deferment_Token] = 0
            if re.search(r'Program', card.Subtype) and card.Type == 'Plan': inactiveProgram[card] = False
    else:
        chkVar = chkOut("petitionedCard")
        if chkVar == 'ABORT': return
        if card.isFaceUp:
            notify("{} has cancelled their petition.".format(me))
            card.isFaceUp = False
            setGlobalVariable("petitionedCard", "Empty")
            setGlobalVariable("passedPlayers", "[]")
        else:
            chkVar2 = chkOut("defeatedPlayers")
            if chkVar2 == 'ABORT': ABORT = True # This allows me to go through the rest of the cost but not take any actions and still clear the shared variables by avoiding terminating the function.
            defeatedPL = eval(chkVar2)
            if me._id in defeatedPL:
               if not confirm("You cannot start a petition once you've lost one in a turn.\n\nBypass?"): ABORT = True
               else: 
                  notify("{} is starting another petition, even though they lost their previous one".format(me))
                  defeatedPL.remove(card.owner._id)
            if chkVar != 'Empty' and not ABORT: 
               whisper("Another petition (for {}) is currently in progress, please complete that one first.".format(Card(int(chkVar))))
               ABORT = True
            elif me.Solaris < cost and not ABORT and not confirm("You're not allowed to start a peition when you do not have at least as much solaris as the deployment cost of the card. \n\nAre you sure you want to proceed?"): ABORT = True
            elif searchNatives(subtype) == 'NOK' and not ABORT: ABORT = True
            elif searchUniques(card, name, 'petition') == 'NOK' and not ABORT: ABORT = True
            elif not ABORT:
               initialBid = -1
               while initialBid < cost:
                  initialBid = askInteger("What will your initial bid be? (Min {}). 0 will cancel the petition.".format(cost), cost)
                  if (initialBid == 0 and cost != 0) or initialBid == None: ABORT = True # If the player puts zero for the bid, or closes the window, abort.
                  elif initialBid > me.Solaris and not confirm("You cannot bid more Solaris than you have in your bank.\n\nBypass?"): initialBid = -1
               card.isFaceUp = True
               notify("{} initiates a petition for {} with an initial bid of {}".format(me, card, initialBid))
               me.Bid = initialBid
               setGlobalVariable("petitionedCard", card._id)
            chkPetitionAutoscripts(card)
            if ABORT: setGlobalVariable("petitionedCard", chkVar)
            setGlobalVariable("defeatedPlayers", str(defeatedPL))
   
def searchUniques(card, name, type = 'deploy'): # Checks if there is a unique card on the table with the same name as the one about to be deployed.
    allUniques = (c for c in table # Make a comprehension of all the cards on the table
        if c.Decktype == 'Imperial' # That are from Imperial Deck (only those are unique)
        and c.isFaceUp # This is apparently not taken into account. The game still includes the face down cards if they match the other conditions.
        and c.name == name # That have the same name as the one being deployed.
        and c != card) # And that are not the same card object as the one about to be deployed. 
                       # I don't know why, but the comprehension grabs this card if this isn't here, even though I filtered the comprehension to disregard face down cards.
    for unique in allUniques:
        if type == 'petition': notify("{} wanted to petition for {} but it's already controlled by {}.".format(me, name, unique.controller))   
        else: notify("{} wanted to deploy {} but it's already controlled by {}.".format(me, name, unique.controller)) 
        return 'NOK'
    return 'OK'

def searchNatives(subtype):
    if re.search(r'Native', subtype):
        if DuneFiefs() == 0: 
            if not confirm("You must control at least one Dune Fief in order to deploy a Native Persona. \n\nAre you sure you want to proceed?"): return 'NOK'
    return 'OK'
    
def restoreAll(group, x = 0, y = 0): 
    mute()
    if shared.Phase != 1: #One can only disengage during the Opening Interval
      whisper("You can only disengage all cards during the Opening Interval")
      return
    myCards = (card for card in table
               if card.controller == me
               and card.owner == me)
    for card in myCards:
        card.orientation &= ~Rot90
        if card.markers[Assembly] > 0 and card.isFaceUp:
             card.markers[Assembly] = 0
    notify("{} disengages all his cards.".format(me))

def addSpice(card, x = 0, y = 0):
    mute()
    notify("{} adds a Spice token to {}.".format(me, card))
    card.markers[Spice] += 1

def subSpice(card, x = 0, y = 0):
    mute()
    notify("{} removes a Spice token from {}.".format(me, card))
    card.markers[Spice] -= 1

def addDeferment(card, x = 0, y = 0):
    mute()
    notify("{} adds a Deferment token on {}.".format(me, card))
    card.markers[Deferment_Token] += 1

def subDeferment(card, x = 0, y = 0):
    mute()
    notify("{} removes a Deferment token on {}.".format(me, card))
    card.markers[Deferment_Token] -= 1

def addProgram(card, x = 0, y = 0):
    mute()
    notify("{} adds a Program token to {}.".format(me, card))
    card.markers[Program] += 1
    
def switchAssembly(card, x = 0, y = 0):
   mute()
   if card.markers[Assembly] == 0:
      notify("{} marks {} as an Assembly card.".format(me, card))
      card.markers[Assembly] = 1
      assemblyCards.append(card)
   else:
      notify("{} takes {} out of the Imperial Assembly.".format(me, card))
      card.markers[Assembly] = 0
      assemblyCards.remove(card)

def CHOAMbuy(group, x = 0, y = 0): # This function allows the player to purchase spice through checks and balances to avoid mistakes.
    global CHOAMDone # Import the variable which informs us if the player has done another CHOAM exchange this turn
    mute()
    spiceNR = 0 # Variable we use to remember how much spice they want to buy
    if CHOAMDone == 1: # If the player has already done a CHOAM exchange, remind them, but let them continue if they want, in case they have a card effect allowing them to do so.
       if not confirm("You've already done a CHOAM exchange this round. Are you sure you're allowed to do another?"): return
       else: notify("{} is performing another CHOAM Exchange this round.".format(me)) # However if they proceed, alter the message to point it out.
    if CHOAMDone == 0: notify("{} is performing a CHOAM Exchange.".format(me)) # Inform everyone that the player is beggingin a CHOAM exchange.
    while spiceNR > 3 or spiceNR == 0: # We start a loop, so that if the player can alter their number if they realize they don't have enough.
       spiceNR = askInteger("How much spice do you want to buy (Max 3. {} Solaris for the first spice and there are {} spice left in the Guild Hoard)?\n\nRemember that you can only do one CHOAM Exchange per round!".format(shared.CROE, shared.counters['Guild Hoard'].value), 0)
       if spiceNR == 0 or spiceNR == None: 
          notify("{} has cancelled the CHOAM exchange".format(me))
          return # If the player answered 0 or closed the window, cancel the exchange and inform.
       elif spiceNR > 0 and spiceNR < 4:  # If they are within the right value of 1-3...
          fullcost = completeSpiceCost(spiceNR) # Calculate how much the spice they want to purchase would cost. 
          if spiceNR > shared.counters['Guild Hoard'].value:  # Check if the hoard has enough spice left.
             whisper("The hoard does not have enough spice for you to buy.")
             spiceNR = 0 # We do this so that the player stays in the loop and gets asked again
          elif me.Solaris < fullcost: # Check if the player can pay it.
             whisper("You do not have enough solaris in your treasury to buy {} Spice from the hoard. You need at least {}".format(spiceNR, fullcost))
             spiceNR = 0 # We do this so that the player stays in the loop and gets asked again
          else: 
             me.Solaris -=fullcost # Player pays here.
             me.Spice += spiceNR # Then they get their spice.
             autoscriptOtherPlayers('TransferredSpice',spiceNR) # We trigger other player's autoscripts
             shared.counters['Guild Hoard'].value -= spiceNR # Then the spice is taken away from the hoard.
             shared.CROE = CROEAdjust(shared.counters['Guild Hoard'].value) # Then the CROE is reset.
             notify("{} has bought {} Spice for {}. The Guild Hoard now has {} Spice left and the CROE is set at {}".format(me, spiceNR, fullcost, shared.counters['Guild Hoard'].value, shared.CROE))
             CHOAMDone = 1 # Then mark that the player has done their CHOAM exchange for the turn.
       else:
          whisper("You cannot buy more than 3 spice per CHOAM Exchange.")
        

def CHOAMsell(group, x = 0, y = 0): # Very similar as CHOAMbuy, but player sells spice instead.
    global CHOAMDone
    mute()
    spiceNR = 0
    if CHOAMDone == 1:
       if not confirm("You've already done a CHOAM exchange this round. Are you sure you're allowed to do another?"): return
       else: notify("{} is performing another CHOAM Exchange this round.".format(me))
    if CHOAMDone == 0: notify("{} is performing a CHOAM Exchange.".format(me))
    while spiceNR > 3 or spiceNR == 0:
       spiceNR = askInteger("How much spice do you want to sell (Max 3. {} Solaris for the first spice and there are {} spice currently in the Guild Hoard)?\n\nRemember that you can only do one CHOAM Exchange per round!".format(shared.CROE, shared.counters['Guild Hoard'].value), 0)
       if spiceNR == 0 or spiceNR == None:
          notify("{} has cancelled the CHOAM exchange".format(me))
          return
       elif spiceNR > 0 and spiceNR < 4: 
          if me.Spice - spiceNR < 0: 
             whisper("You do not have this amount of spice to sell. You have only {} to sell.".format(me.Spice))
             spiceNR = 0 # We do this so that the player stays in the loop and gets asked again
          else: 
             fullcost = completeSpiceCost(-spiceNR)
             me.Solaris +=fullcost
             me.Spice -= spiceNR
             autoscriptOtherPlayers('TransferredSpice',spiceNR) # We trigger other player's autoscripts
             shared.counters['Guild Hoard'].value += spiceNR
             shared.CROE = CROEAdjust(shared.counters['Guild Hoard'].value)
             notify("{} has sold {} Spice for {}. The Guild Hoard now has {} Spice left and the CROE is set at {}".format(me, spiceNR, fullcost, shared.counters['Guild Hoard'].value, shared.CROE))
             CHOAMDone = 1
       else:
          whisper("You cannot sell more than 3 spice per CHOAM Exchange.")

def resetBank(group, x=0, y=0): # Asks the player to set the amount of spice there should be in the bank and resets the CROE.
   mute()
   currentbank = shared.counters['Guild Hoard'].value
   newbank = askInteger("Set the bank at how many spice?\n[Currently at {} Spice]\n\n(Hint: close this window to simply reset the CROE for the current number of spice)".format(currentbank), currentbank)
   if newbank == None: newbank = currentbank
   if newbank >= currentbank: difference = '+' + str(newbank - currentbank)
   elif currentbank > newbank: difference = '-' + str(currentbank - newbank)
   shared.CROE = CROEAdjust(newbank)
   shared.counters['Guild Hoard'].value = newbank 
   notify("{} has reset the Guild Hoard to {} Spice ({}). The CROE is now {}".format(me,shared.counters['Guild Hoard'].value, difference, shared.CROE))

def completeSpiceCost(count = 1): # This takes as input how many spice we want to buy or sell, and returns how much it's going to cost in total.
   i = 0
   cost = 0
   simulatedHoard = shared.counters['Guild Hoard'].value #We use simulated numbers in order to avoid touching the counters.
   simulatedCROE = shared.CROE 
   if count > 0:
      while i < count:
         cost += simulatedCROE
         simulatedHoard -= 1
         simulatedCROE = CROEAdjust(simulatedHoard)
         i += 1
      return cost
   elif count < 0:
      while i > count:
         cost += simulatedCROE
         simulatedHoard += 1
         simulatedCROE = CROEAdjust(simulatedHoard)
         i -= 1
      return cost
 

def CROEAdjust(hoard): # We need to pass the guild hoard number here. We cannot set it as default when it's not provided. It bugs out.
   if hoard == 0: return 6
   elif hoard >0 and hoard < 4: return 5
   elif hoard >3 and hoard < 7: return 4
   elif hoard >6 and hoard < 10: return  3
   elif hoard >9 and hoard < 13: return 2
   elif hoard >12: return 1
   else: notify("Why is the Guild Hoard at a {}?".format(hoard)) # Notify the players, in case the counter is set below 0 by mistake.

def buyFavor(group, x = 0, y = 0): # Very similar to CHOAMbuy, but player buys Favour instead, which is simpler.
    global favorBought
    mute()
    favorNR = 0
    if favorBought == 1:
       if not confirm("You've already bought favor this round. Are you sure you're allowed to buy more?"): return
       else: notify("{} is performing another favor purchase this round.".format(me))
    if favorBought == 0: notify("{} is performing a favor purchase.".format(me))
    while favorNR > 5 or favorNR == 0:
       favorNR = askInteger("How much Imperial favor do you want to purchase (Max 5, 2 Solaris per Favor)?\n\n(Remember that you can only purchase favor once per round!)", 0)
       if favorNR == 0 or favorNR == None:
          notify("{} has cancelled the favor purchase".format(me))
          return
       elif favorNR > 0 and favorNR < 6: 
          fullcost = favorNR * 2
          if me.Solaris < fullcost: 
             whisper("You do not have enough solaris in your treasury to buy {} favor. You need at least {}".format(favorNR, fullcost))
             favorNR = 0 # We do this so that the player stays in the loop and gets asked again
          else: 
             me.Solaris -=fullcost
             me.Favor += favorNR
             autoscriptOtherPlayers('BoughtFavor',favorNR) # We trigger other player's autoscripts
             notify("{} has bought {} favor. They now have {} favor".format(me, favorNR, me.Favor))
             favorBought = 1
       else:
          whisper("You cannot buy more than 5 favor per exchange.")


def automatedOpening(group, x = 0, y = 0):
   global favorBought, CHOAMDone, DeployedDuneEvent, DeployedImperiumEvent, inactiveProgram
   favorBought = 0 # Reset the player's favor exchanges for the round.
   CHOAMDone = 0 # Reset the player's CHOAM exchanges for the round.
   DeployedDuneEvent = 0 # Reset the amount of Dune events for this round.
   DeployedImperiumEvent = 0 # Reset the amount of Imperium events for this round.
   mute()
   if shared.Phase != 1: # This function is allowed only during the Opening Interval
      whisper("You can only perform this action during the Opening Interval")
      return
   myCards = (card for card in table if card.controller == me and card.owner == me)
   for card in myCards:
      if card.highlight != DoesntDisengageColor: card.orientation &= ~Rot90 # If a card can disengage, disengage it.
      if card.markers[Assembly] > 0 and card.isFaceUp: card.markers[Assembly] = 0 # If a card came from the assembly last turn. Remove its special assembly marker.
      if not card.isFaceUp and card.markers[Assembly] == 0: card.markers[Deferment_Token] += 1 # If a card is not an Assembly or Program and is face down (subdued), add a deferment token on it.
      try: # We don't want to put deferment tokens on inactive programs.
         if inactiveProgram[card]: card.markers[Deferment_Token] = 0
      except KeyError: pass   
   notify("{} disengaged all his cards and added deferment tokens to all subdued ones.".format(me))
   setGlobalVariable("petitionedCard", "Empty") # Clear the shared variables, just in case any of them are stuck
   setGlobalVariable("passedPlayers", "[]")
   setGlobalVariable("defeatedPlayers", "[]") # Clear the players who have lost a petition last turn.

   
def automatedClosing(group, x = 0, y = 0):
   if shared.Phase != 3: # This function is allowed only during the Closing Interval
      whisper("You can only perform this action during the Closing Interval")
      return
   if me.Favor < 1 and len(me.hand) < handsize:
      notify("{} cannot not refill their hand because they have less than 1 Imperial favor. Is {} is defeated?".format(me, me))
      return   
   if not confirm("Have you remembered to discard any cards you don't want from your hand and Assembly?"): return
   refill()
   myCards = (card for card in table
              if card.controller == me
              and card.owner == me
              and card.Type == 'Event'
              and card.isFaceUp)
   for card in myCards:
      if re.search(r'Nexus', card.Subtype): 
         card.markers[Deferment_Token] -= 1 # Nexus events lose one deferment token per House discard phase.
         if card.markers[Deferment_Token] == 0: # If Nexus events lose their last deferment token, they are discarded.
            card.moveTo(me.piles['House Discard'])
            notify ("{}'s Nexus Event {} has expired and was automatically discarded".format(me, card))
      elif re.search(r'Duration Effect', card.Operation): 
         card.moveTo(me.piles['House Discard']) # Duration events are discarded at the end of the turn.
         notify ("{}'s Duration Effect from {} has expired and was automatically discarded".format(me, card))
   notify("{} refills their hand back to {} and their Imperial Assembly to {}.".format(me, handsize, assemblysize))
   

def doesNotDisengage(card, x = 0, y = 0): # Mark a card as "Does not disengage" or unmark it. We use a card highlight to do this.
   if card.highlight == DoesntDisengageColor: # If it's already marked, remove highlight from it and inform.
      card.highlight = None
      notify("{}'s {} can now Disengage during Opening Interval.".format(me, card))
   else:
      card.highlight = DoesntDisengageColor # Otherwise highlight it and inform. 
      notify("{}'s {} will not Disengage during Opening Interval.".format(me, card))

def discard(cards, x = 0, y = 0): # Discard a card.
   mute()
   for card in cards: # Can be done at more than one card at the same time, since attached cards follow their parent always.
      cardowner = card.owner
      if card.isFaceUp: chkRemoveAutoscripts(card) # We run the removal scripts only if the card was deployed.
      card.isFaceUp = True
      if card in assemblyCards: assemblyCards.remove(card)
      if card.Decktype == 'Imperial': card.moveTo(cardowner.piles['Imperial Discard'])
      else: card.moveTo(cardowner.piles['House Discard'])
      notify("{} has discarded {}.".format(me, card))

def produceSpice(card, x = 0, y = 0):
   mute()
   spiceNR = askInteger("How much spice to produce directly into the Guild Hoard?", 1)
   if spiceNR == 0: return
   card.orientation = Rot90
   shared.counters['Guild Hoard'].value += spiceNR
   shared.CROE = CROEAdjust(shared.counters['Guild Hoard'].value)
   notify("{} has engaged {} to produce {} spice directly into the Guild Hoard. The Guild Hoard now has {} Spice and the CROE is set at {}".format(me, card, spiceNR, shared.counters['Guild Hoard'].value, shared.CROE))

#------------------------------------------------------------------------------
# Hand Actions
#------------------------------------------------------------------------------

def payCost(count = 1, notification = silent): # Automatically pays the cost of a card being played from your hand, or confirms/informs if you can't play it.
   count = num(count)
   if count == 0 : return 'OK'
   if me.Solaris < count:  
      if not confirm("You do not seem to have enough Solaris in your House Treasury to pay the cost. \n\nAre you sure you want to proceed? \
      \n(If you do, your solaris will go to the negative. You will need to increase it manually as required.)"): return 'ABORT'
      if notification == loud: notify("{} was supposed to pay {} Solaris but only has {} in their house treasury. They'll need to reduce the cost by {} with card effects.".format(me, count, me.Solaris, count - me.Solaris))   
      me.Solaris -= count
   else: 
      me.Solaris -= count
      if notification == loud: notify("{} has paid {} Solaris. {} is left their house treasury".format(me, count, me.Solaris))  
   return 'OK'

def play(card, x = 0, y = 0):
   global totalevents
   mute()
   src = card.group
   # The function below checks if the player is allowed to play this house card. House cards can only be played if the player has one card of same allegiance in their Imperial deck.
   if card.Allegiance != 'None' and card.Allegiance != '' and card.Allegiance not in allegiances: 
      if confirm("{}'s Allegiance ({}) does not exist your Imperial Deck. You are not normally allowed have it in your deck. \n\nContinue?".format(card.name, card.Allegiance)):
         notify("{}'s Allegiance does not exist in {}'s Imperial Deck. Illegal deck?".format(card, me))
      else: return
   if card.Type == 'Event':  # Events are placed face down.
      placeCard(card, 'PlayEvent')
      notify("{} plays an event from their hand.".format(me))
      totalevents += 1 # This is used to moves every new event a bit from the old one, to avoid stacking them and making them invisible.
      if totalevents == 11: totalevents = 0
   elif card.Type == 'Persona' and re.search(r'Native', card.Subtype): # A player can only play aides with subtype "Native" if they control a "Dune Fief".
      if DuneFiefs() == 0: 
         if confirm("You must control at least one Dune Fief in order to play a Native aide. \n\nAre you sure you want to proceed?"):
            if payCost(card.properties['Deployment Cost'], loud) == 'OK': # Take cost out of the bank, if there is any.
               placeCard(card, "DeployPersona")
               notify("{} plays {} from their hand.".format(me, card))
      else: 
         if payCost(card.properties['Deployment Cost'], loud) == 'OK': # Take cost out of the bank, if there is any.
            placeCard(card, "DeployPersona")
            notify("{} plays {} from their hand.".format(me, card))
   elif card.Type == 'Persona':
      if payCost(card.properties['Deployment Cost'], loud) == 'OK':# Take cost out of the bank, if there is any.
         placeCard(card, "DeployPersona")
         notify("{} plays {} from their hand.".format(me, card))   
   else:
      if payCost(card.properties['Deployment Cost'], loud) == 'OK':# Take cost out of the bank, if there is any.
         card.moveToTable(0, 0 - yaxisMove(card))
         notify("{} plays {} from their hand.".format(me, card))
   chkDeployAutoscripts(card)
 
def setup(group = me.hand, x= 0, y = 0):
# This function is usually the first one the player does. It will setup their homeworld on their side of the table. 
# It will also shuffle their decks, setup their Assembly and Dune and draw 7 cards for them.
   group = me.hand # Because this action can be run from the table as well now.
   if shared.Phase == 0: # First check if we're on the pre-setup game phase. 
                     # As this function will play your whole hand and wipe your counters, we don't want any accidents.
#      if not confirm("Have bought all the favour and spice you'll need with your bonus solaris? \n\n(Remember you need 1 solaris per program you're going to install.)"): return
      global PLS, allegiances, inactiveProgram # Import some necessary variables we're using around the game.
      DuneinHand = 0
      mute()
      chooseSide() # The classic place where the players choose their side.
      me.piles['Imperial Deck'].shuffle() # First let's shuffle our decks now that we have the chance.
      me.piles['House Deck'].shuffle()
      for card in group: # For every card in the player's hand... (which should be just their homeworld and possibly some plans)
         if re.search(r'Homeworld', card.Subtype) and card.Type == 'Holding':  # If it's the homeworld...
            placeCard(card,'SetupHomeworld')
            allegiances.append(card.Allegiance) # We make a note of the Allegiance the player is playing this time (used later for automatically losing favour)
         if re.search(r'Program', card.Subtype) and card.Type == 'Plan':  # If it's a program...
            if payCost(1) == 'OK': # Pay the cost of the program
               placeCard(card,'SetupProgram')
               inactiveProgram[card] = True
         if card.model == '2037f0a1-773d-42a9-a498-d0cf54e7a001': # If the player has put Dune in their hand as well...
            placeCard(card,'SetupDune')
            DuneinHand = 1 # Note down that player brought their own Dune, so that we don't generate a second one.
      if DuneinHand == 0: # If the player didn't bring their own Dune, generate a new one on their side.
         Dune = table.create("2037f0a1-773d-42a9-a498-d0cf54e7a001", 0, 0, 1, True) # Create a Dune card in the middle of the table.
         placeCard(Dune,'SetupDune')
      noteAllegiances() # Note down the rest allegiances of the player
      shared.counters['Guild Hoard'].value = 4 + len(players) * 2 # Starting Spice is 4 + (Nr of players * 2)
      shared.CROE = CROEAdjust(shared.counters['Guild Hoard'].value)
      startFav = -1
      startSpice = -1
      while startSpice < 0 or startSpice >= 5: # keep asking the amount until a valid number is given.
         startSpice = askInteger("How much spice do you want to buy with your bonus solaris?\n\n({} per Spice)".format(shared.CROE + 1), 0)
         if payCost(startSpice * (shared.CROE + 1)) == 'ABORT': startSpice = -1
      me.Spice += startSpice
      while startFav < 0 or startFav >= 5: 
         startFav = askInteger("How much favor do you want to buy with your bonus solaris?\n\n(2 per favor)", 0)
         if payCost(startFav * 2) == 'ABORT': startFav = -1         
      me.Favor += startFav
      me.Solaris += 20     
      refill() # We fill the player's play hand to their hand size (usually 5)
      notify("{} is playing {}. Their starting Solaris is {} and their Imperial Favour is {}. They have {} Programs".format(me, allegiances[0], me.Solaris, me.Favor, totalprogs))  
   else: whisper('You can only setup your starting cards during the Pre-Game setup phase') # If this function was called outside the pre-game setup phase
            
def setHandSize(group): # A function to modify a player's hand size. This is used during Closing Interval when refilling the player's hand automatically.
   global handsize
   tempsize = askInteger("What is your current hand size?", handsize)
   if tempsize == None: return
   else: handsize = tempsize
   notify("{} sets their hand size to {}".format(me, handsize))

def setAssemblySize(group): # A function to modify a player's hand size. This is used during Closing Interval when refilling the player's hand automatically.
   global assemblysize
   tempsize = askInteger("What is your current Assembly limit?", assemblysize)
   if tempsize == None: return
   else: assemblysize = tempsize
   notify("{} sets their Assembly limit to {}".format(me, assemblysize))
   
def refill(group = me.hand): # Refill the player's hand to its hand size.
   if len(me.hand) < handsize: drawMany(me.piles['House Deck'], handsize - len(me.hand), silent) # If there's less cards than the handsize, draw from the deck until it's full.
   if len(assemblyCards) < assemblysize: imperialDraw(times = assemblysize - len(assemblyCards))

def handDiscard(card, x = 0, y = 0): # Discard a card from your hand.
   mute()
   card.moveTo(me.piles['House Discard'])
   notify("{} has discarded {}.".format(me, card))  

def randomDiscard(group): # Discard a card from your hand randomly.
   mute()
   card = group.random() # Select a random card
   if card == None: return # If hand is empty, do nothing.
   notify("{} randomly discards a card.".format(me)) # Inform that a random card was discarded
   card.moveTo(me.piles['House Discard']) # Move the card in the discard pile.

#------------------------------------------------------------------------------
# Pile Actions
#------------------------------------------------------------------------------

def draw(group):
    if len(group) == 0: return
    i = 0
    mute()
    group.top().moveTo(me.hand)
    notify("{} draws a card.".format(me))

def imperialDraw(group = me.piles['Imperial Deck'], times = 1):
   if len(group) == 0: return
   mute()
   for i in range(times):
      card = group.top()
      card.moveToTable(0,0, True)
      card.markers[Assembly] = 1
      assemblyCards.append(card)
   for n in range(len(assemblyCards)): # Reorganizing the assembly cards.
      card = assemblyCards[n]
      if playeraxis == Yaxis:
         card.moveToTable(PLS * cwidth(card) + PLS * (len(assemblyCards) - 2) * (cwidth(card) / 2) - PLS * n * cwidth(card), homeDistance(card) + cardDistance(card) - yaxisMove(card,'force'),True)
      else: 
         card.moveToTable(homeDistance(card) + cardDistance(card), PLS * cheight(card)  + PLS * (len(assemblyCards) - 2) * (cheight(card) / 2) - n * PLS * cheight(card),True)
    
def shuffle(group):
  group.shuffle()

def drawMany(group, count = None, notification = loud): # This function draws a variable number cards into the player's hand.
    mute()
    if count == None: count = askInteger("Draw how many cards?", 7)
    if len(group) < count: 
       notify("{}'s House deck has {} cards and they attempted to draw {} cards. Did they just lose the game?.".format(me, len(group), count))
       return
    for c in group.top(count): c.moveTo(me.hand)
    if notification == loud : notify("{} draws {} cards to their play hand.".format(me, count)) # And if we're "loud", notify what happened.

def mill(group):
   mute()
   if len(group) == 0: return
   count = askInteger("Discard how many cards?", 3)
   for c in group.top(count): c.moveTo(me.piles['House Discard'])
   notify("{} discards the top {} cards from their house deck.".format(me, count))
   
#------------------------------------------------------------------------------
# Autoscripts 
#------------------------------------------------------------------------------

def useAbility(card, x = 0, y = 0):
   global CROEsnapshot
   mute()
   if card.markers[Assembly] == 1 or not card.isFaceUp: # If card is face down or assembly, assume they wanted to deploy it.
      subdue(card)
      return
   elif not Automation or card.AutoScript == "": 
      engage(card) # If card is face up but has no autoscripts, or automation is disabled just engage/disengage it.
      return
   elif re.search(r'{Custom:', card.AutoScript): 
      customScript(card) # Some cards just have a fairly unique effect and there's no use in trying to make them work in the generic framework.
      return
   ### Checking if card has multiple autoscript options and providing choice to player.
   Autoscripts = card.AutoScript.split('||')
   for autoS in Autoscripts: # Checking and removing any "WhileDeployed" actions.
      if re.search(r'WhileDeployed', autoS): Autoscripts.remove(autoS)
   if len(Autoscripts) == 0:
      engage(card) # If the card had only "WhileDeployed" effect, just engage it.
      return      
   if len(Autoscripts) > 1: 
      abilConcat = "This card has multiple abilities.\nWhich one would you like to use?\n\n" # We start a concat which we use in our confirm window.
      for idx in range(len(Autoscripts)): # If a card has multiple abilities, we go through each of them to create a nicely written option for the player.
         #notify("Autoscripts {}".format(Autoscripts)) # Debug
         abilRegex = re.search(r"C(P?[ES0])F?X?[0-9]?:([A-Z][a-z]+)([0-9]*)([A-Z][a-z ]+)-?([A-Za-z -{},]*)", Autoscripts[idx]) # This regexp returns 3-4 groups, which we then reformat and put in the confirm dialogue in a better readable format.
         #notify("abilRegex is {}".format(abilRegex.groups())) # Debug
         if abilRegex.group(1) == 'E': abilCost = 'Engage'
         elif abilRegex.group(1) == 'S': abilCost = 'Subdue'
         elif abilRegex.group(1) == 'PE': abilCost = 'Engage Parent'
         elif abilRegex.group(1) == 'PS': abilCost = 'Subdue Parent'
         else: abilCost = 'Use Ability'
         favorCost = re.search(r"F(X)?([0-9])?:", Autoscripts[idx])
         if favorCost:
            if favorCost.group(1) and favorCost.group(2): 
               abilCost += ' and discard X favor (Max {})'.format(favorCost.group(2))
            elif favorCost.group(1):
               abilCost += ' and discard X favor'
            else:
               abilCost += ' and discard {} favor'.format(favorCost.group(2))
         abilConcat += '{}: {} to {} {} {}'.format(idx, abilCost, abilRegex.group(2), abilRegex.group(3), abilRegex.group(4)) # We add the first three groups to the concat. Those groups are always Gain/Hoard/Prod ## Favo/Solaris/Spice
         if abilRegex.lastindex == 5: # If the autoscript has a fourth group, then it means it has subconditions. Such as "per Holding" or "by Rival"
            subconditions = abilRegex.group(5).split('-') # These subconditions are always separated by dashes "-", so we use them to split the string
            for idx2 in range(len(subconditions)): 
               abilConcat += ' {}'.format(subconditions[idx2]) #  Then we iterate through each distinct subcondition and display it without the dashes between them. (In the future I may also add whitespaces between the distinct words)
         abilConcat += '\n' # Finally add a newline at the concatenated string for the next ability to be listed.
      abilChoice = len(Autoscripts) + 1 # Since we want a valid choice, we put the choice in a loop until the player exists or selects a valid one.
      while abilChoice >= len(Autoscripts):
         abilChoice = askInteger('{}'.format(abilConcat), 0) # We use the ability concatenation we crafted before to give the player a choice of the abilities on the card.
         if abilChoice == None: return # If the player closed the window, abort.
      selectedAutoscripts = Autoscripts[abilChoice].split('&&') # If a valid choice is given, choose the autoscript at the list index the player chose.
   else: selectedAutoscripts = Autoscripts[0].split('&&')
   timesNothingDone = 0 # A variable that keeps track if we've done any of the autoscripts defined. If none have been coded, we just engage the card.
   CROEsnapshot = shared.CROE # Some scripts, like "CHOAM Contract" are based on CROE, so we need to take a snapshot of it, because their costs actions might modify it.
   for activeAutoscript in selectedAutoscripts:
      ### Checking if any of  card effects requires one or more targets first
      if re.search(r'Targeted', activeAutoscript) and not findTarget(activeAutoscript): return
   for activeAutoscript in selectedAutoscripts:
      targetC = findTarget(activeAutoscript)
      ### Warning the player in case we need to
      if chkWarn(activeAutoscript) == 'ABORT': return
      ### Checking the activation cost and preparing a relevant string for the announcement
      actionCost = re.match(r"CP?([ES0])(F)?(X)?([0-9]*):", activeAutoscript) 
      # This is the cost of the card. It always starts with 'C' which is standsa for "Cost"
      # After C, follows 'E', 'S' or '0', which stand for "Engage", "Subdue" or "No Card Modification" cost respectively.
      # The follows the Favor cost, if any. If it exists, it must start with 'F'
      # After the F can follow a number, which will be automatically taken out of the player's counter.
      # If an X exists then the number is optional. The X will ask the player for an amount of favour to discard, up to the number. No number means unlimited.
      if actionCost: # If there's no match, it means we've already been through the cost part once.
         if actionCost.group(1) == 'E':
            if engage(card, silent = True, force = 'Engage') == 'ABORT': return
            announceText = '{} engages {}'.format(card.controller, card)
         elif actionCost.group(1) == 'S': 
            announceText = '{} subdues {}'.format(card.controller, card.name)
            random = rnd(10,1000) # Small wait to grab the name.
            card.isFaceUp = False
         else: announceText = '{} activates {}'.format(card.controller, card)
         X = 0 # Variable for custom cost. Is set to 0 if the card does not require it.
         if actionCost.group(2):
            if actionCost.group(3) == 'X':
               if actionCost.group(4): 
                  limitX = num(actionCost.group(4))
                  X = askInteger("How much favor do you want to discard?\n\n(Max {})".format(limitX), limitX)
                  if X > limitX: X = limitX
               else: X = askInteger("How much favor do you want to discard?", 1)
               if not X: return
               me.Favor -= X
               announceText += ' and discards {} favor'.format(X)
            else:
               me.Favor -= num(actionCost.group(4))
               announceText += ' and discards {} favor'.format(actionCost.group(2))
         announceText += ' to'
      elif not announceText.endswith(' to') and not announceText.endswith(' and'): announceText += ' and'
      ### Calling the relevant function depending on if we're increasing our own counters, the hoard's or putting card markers.
      if re.search(r'Gain([0-9]+)', activeAutoscript): announceText = GainX(activeAutoscript, announceText, card, targetC, True, n = X)
      elif re.search(r'Hoard([0-9]+)', activeAutoscript): announceText = HoardX(activeAutoscript, announceText, card, True)
      elif re.search(r'(Prod|Spawn)([0-9]+)', activeAutoscript): announceText = ProdX(activeAutoscript, announceText, card, True)
      elif re.search(r'Transfer([0-9]+)', activeAutoscript): announceText = TransferX(activeAutoscript, announceText, card, targetC, True, n = X)
      elif re.search(r'(Assign|Remove)([0-9]+)', activeAutoscript): announceText = TokensX(activeAutoscript, announceText, card, targetC, True, n = X)
      elif re.search(r'(Engage|Disengage|Subdue|Deploy|Discard)Target', activeAutoscript): announceText = ModifyStatus(activeAutoscript, announceText, card, targetC, True)
      elif re.search(r'Draw([0-9]+)', activeAutoscript): announceText = DrawX(activeAutoscript, announceText, card, targetC, True)
      elif re.search(r'(Steal|Pay)([0-9]+)', activeAutoscript): announceText = StealX(activeAutoscript, announceText, card, targetC, True)
      elif re.search(r'UseCustomAbility', activeAutoscript): announceText = UseCustomAbility(activeAutoscript, announceText, card, targetC)
      else: timesNothingDone += 1
      if announceText == 'ABORT': 
         autoscriptCostUndo(selectedAutoscripts[0], card) # If nothing was done, try to undo. The first item in selectedAutoscripts[] contains the cost.
         return
   if announceText.endswith(' to'): # If our text annouce ends with " to", it means that nothing happened. Try to undo and inform player.
      notify("{} but there was nothing to do.".format(announceText[:-len(' to')]))
      autoscriptCostUndo(selectedAutoscripts[0], card)
   else: notify("{}.".format(announceText)) # Finally announce what the player just did by using the concatenated string.

def chkWarn(Autoscript):
   warning = re.search(r'warn([A-Z][A-Za-z0-9 ]+)-?', Autoscript)
   if warning:
      if warning.group(1) == 'Discard': 
         if not confirm("This action requires that you discard some cards. Have you done this already?"):
            whisper("--> Aborting action. Please discard the necessary amount of cards and run this action again")
            return 'ABORT'
   return 'OK'
            
def findTarget(Autoscript):
   targetC = None
   if re.search(r'Targeted', Autoscript):
      validTargets = [] # a list that holds any type that a card must be, in order to be a valid target.
      validNamedTargets = [] # a list that holds any name or allegiance that a card must have, in order to be a valid target.
      invalidTargets = [] # a list that holds any type that a card must not be to be a valid target.
      invalidNamedTargets = [] # a list that holds the name or allegiance that the card must not have to be a valid target.
      requiredAllegiances = []
      whatTarget = re.search(r'\bon([A-Za-z_{}, ]+)[-]?', Autoscript) # We signify target restrictions keywords by starting a string with "or"
      if whatTarget: validTargets = whatTarget.group(1).split('_or_') # If we have a list of valid targets, split them into a list, separated by the string "_or_". Usually this results in a list of 1 item.
      ValidTargetsSnapshot = list(validTargets) # We have to work on a snapshot, because we're going to be modifying the actual list as we iterate.
      for chkTarget in ValidTargetsSnapshot: # Now we go through each list item and see if it has more than one condition (Eg, non-desert fief)
         if re.search(r'_and_', chkTarget):  # If there's a string "_and_" between our restriction keywords, then this keyword has mutliple conditions
            multiConditionTargets = chkTarget.split('_and_') # We put all the mutliple conditions in a new list, separating each element.
            for chkCondition in multiConditionTargets: 
               regexCondition = re.search(r'(no[nt]|allegiance){?([A-Za-z, ]+)}?', chkCondition) # Do a search to see if in the multicondition targets there's one with "non" in front
               if regexCondition and regexCondition.group(1):
                  if regexCondition.group(2) not in invalidTargets == 'non': invalidTargets.append(regexCondition.group(2)) # If there is, move it without the "non" into the invalidTargets list.
               elif regexCondition and regexCondition.group(1) == 'not':
                  if regexCondition.group(2) not in invalidNamedTargets: invalidNamedTargets.append(regexCondition.group(2))
               elif regexCondition and regexCondition.group(1) == 'allegiance':
                  if regexCondition.group(2) not in validNamedTargets: validNamedTargets.append(regexCondition.group(2))
               else: validTargets.append(chkCondition) # Else just move the individual condition to the end if validTargets list
            validTargets.remove(chkTarget) # Finally, remove the multicondition keyword from the valid list. Its individual elements should now be on this list or the invalid targets one.
         else:
            regexCondition = re.search(r'(no[nt]){?([A-Za-z, ]+)}?', chkTarget)
            if regexCondition and regexCondition.group(1) == 'non' and regexCondition.group(2) not in invalidTargets: # If the keyword has "non" in front, it means it's something we need to avoid, so we move it to a different list.
               invalidTargets.append(regexCondition.group(2))
               validTargets.remove(chkTarget)
               continue
            if regexCondition and regexCondition.group(1) == 'not' and regexCondition.group(2) not in invalidNamedTargets: # Same as above but keywords with "not" in front as specific card names.
               invalidNamedTargets.append(regexCondition.group(2))
               validTargets.remove(chkTarget)
               continue
            regexCondition = re.search(r'{([A-Za-z, ]+)}', chkTarget)
            if regexCondition and regexCondition.group(1) not in validNamedTarget: # Same as above but keywords in {curly brackets} are exact names in front as specific card names.
               validNamedTargets.append(regexCondition.group(1))
               validTargets.remove(chkTarget)
      for targetLookup in table: # Now that we have our list of restrictions, we go through each targeted card on the table to check if it matches.
         if targetLookup.targetedBy and targetLookup.targetedBy == me and chkPlayer(Autoscript, targetLookup.controller, False): # The card needs to be targeted by the player. If the card needs to belong to a specific player (me or rival) this also is taken into account.
            if not targetLookup.isFaceUp: # If we've targeted a subdued card, we turn it temporarily face-up to grab its properties.
               targetLookup.isFaceUp = True
               wasSubdued = True
            else: wasSubdued = False
            if len(validTargets) == 0 and len(validNamedTargets) == 0: targetC = targetLookup # If we have no target restrictions, any targeted  card will do.
            else:
               for validtargetCHK in validTargets: # look if the card we're going through matches our valid target checks
                  if re.search(r'{}'.format(validtargetCHK), targetLookup.Type) or re.search(r'{}'.format(validtargetCHK), targetLookup.Subtype) or re.search(r'{}'.format(validtargetCHK), targetLookup.Decktype):
                     targetC = targetLookup
               for validtargetCHK in validNamedTargets: # look if the card we're going through matches our valid target checks
                  if validtargetCHK == targetLookup.name or validtargetCHK == targetLookup.Allegiance:
                     targetC = targetLookup
            if len(invalidTargets) > 0: # If we have no target restrictions, any selected card will do as long as it's a valid target.
               for invalidtargetCHK in invalidTargets:
                  if re.search(r'{}'.format(invalidtargetCHK), targetLookup.Type) or re.search(r'{}'.format(invalidtargetCHK), targetLookup.Subtype) or re.search(r'{}'.format(invalidtargetCHK), targetLookup.Decktype):
                     targetC = None
            if len(invalidNamedTargets) > 0: # If we have no target restrictions, any selected card will do as long as it's a valid target.
               for invalidtargetCHK in invalidNamedTargets:
                  if invalidtargetCHK == targetLookup.name or invalidtargetCHK == targetLookup.Allegiance:
                     targetC = None
            if wasSubdued: targetLookup.isFaceUp = False
            if targetC: return targetC
      if targetC == None: 
         targetsText = ''
         if len(validTargets) > 0: targetsText += "\nValid Target types: {}.".format(validTargets)
         if len(validNamedTargets) > 0: targetsText += "\nSpecific Valid Targets: {}.".format(validNamedTargets)
         if len(invalidTargets) > 0: targetsText += "\nInvalid Target types: {}.".format(invalidTargets)
         if len(invalidNamedTargets) > 0: targetsText += "\nSpecific Invalid Targets: {}.".format(invalidNamedTargets)
         if not chkPlayer(Autoscript, targetLookup.controller, False): 
            allegiance = re.search(r'by(Rival|Mw)', Autoscript)
            requiredAllegiances.append(allegiance.group(1))
         if len(requiredAllegiances) > 0: targetsText += "\nValid Target Allegiance: {}.".format(requiredAllegiances)
         whisper("You need to target a valid card before using this action{}".format(targetsText))
         return targetC
   else: return targetC

def GainX(Autoscript, announceText, card, targetCard = None, manual = False, n = 0):
# n is used when other scripts are calling this variable, to automatically provide the generated result to the counters of another player owning a specific card.
# For example if one player owns a card that produces one Solaris per Spice produced in a desert, and another player produces 3 spice with a Spice Blow event...
# ...then the other script will call this one, giving an n of 3.
   gain = 0
   extraText = ''
   action = re.search(r'\bGain([0-9]+)(Solaris|Spice|Favor)', Autoscript) # First see if we're gaining Solaris, Spice or Favour and how much.
   gain += num(action.group(1))
   duneXtra = re.search(r'Dune([0-9])Xtra', Autoscript) # Some cards give you extra Solaris if you control Dune.
   if duneXtra and DuneFiefs(True) == 1: # If the autoscript includes extra cost for controlling Dune, and we contol Dune...
      extraText = ' ({} + {} for controlling Dune)'.format(action.group(1),duneXtra.group(1))
      gain += num(duneXtra.group(1))
   multiplier = per(Autoscript, card, n, targetCard, manual) # We check if the card provides a gain based on something else, such as favour bought, or number of dune fiefs controlled by rivals.
   if action.group(2) == 'Solaris': card.owner.Solaris += gain * multiplier
   elif action.group(2) == 'Spice': card.owner.Spice += gain * multiplier
   elif action.group(2) == 'Favor': card.owner.Favor += gain * multiplier
   else: 
      whisper("Gain what?! (Bad autoscript)")
      return 'ABORT'
   announceString = "{} gain {} {}{}".format(announceText, gain * multiplier, action.group(2),extraText)
   if not manual and multiplier > 0: notify('--> {}.'.format(announceString))
   else: return announceString
      
def HoardX(Autoscript, announceText, card, manual = False):
   action = re.search(r'\bHoard([0-9]+)Spice', Autoscript)
   multiplier = per(Autoscript, card)
   shared.counters['Guild Hoard'].value += num(action.group(1)) * multiplier
   shared.CROE = CROEAdjust(shared.counters['Guild Hoard'].value)   
   announceString = "{} add {} Spice to the Guild Hoard (Total:{}.CROE:{})".format(announceText, num(action.group(1)) * multiplier, shared.counters['Guild Hoard'].value, shared.CROE)
   if not manual and multiplier > 0: notify('--> {}.'.format(announceString))
   else: return announceString

def ProdX(Autoscript, announceText, card, manual = False):
   action = re.search(r'\b(Prod|Spawn)([0-9]+)Spice', Autoscript)
   if action.group(1) == 'Prod' and not confirm('Do you want to produce spice on {}?\n\nPressing "No" will send it directly to the Guild Hoard instead'.format(card.name)):
      return HoardX('Hoard{}Spice'.format(action.group(2)), announceText, card) # If we want to produce the spice to the hoard, we're going to use the HoardX() function, but we need to sent it a modified Autoscript.
   card.markers[Spice] += num(action.group(2))
   autoscriptOtherPlayers('GeneratedSpice',num(action.group(2)))
   announceString = "{} produce {} spice assigned to it".format(announceText,action.group(2))
   if not manual: notify('--> {}.'.format(announceString))
   else: return announceString

def TransferX(Autoscript, announceText, card, targetCard = None, manual = False):
   breakadd = 1
   if not targetCard: targetCard = card # If there's been to target card given, assume the target is the card itself.
   action = re.search(r'\bTransfer([0-9]+)Spice-to(Owner|Hoard|Discard)', Autoscript)
   if targetCard.markers[Spice] < num(action.group(1)): 
      if re.search(r'isCost', Autoscript):
         whisper("You must have at least {} Spice on the card to take this action".format(action.group(1)))
         return 'ABORT'
      elif targetCard.markers[Spice] == 0: 
         whisper("There was nothing to transfer.")
         return 'ABORT'
   for transfer in range(num(action.group(1))):
      if targetCard.markers[Spice] > 0: 
         targetCard.markers[Spice] -= 1
         if action.group(2) == 'Owner': 
            card.owner.Spice += 1
            destination = "{}'s hoard".format(card.owner)
         elif action.group(2) == 'Hoard': 
            shared.counters['Guild Hoard'].value += 1
            destination = "the Guild Hoard"
         elif action.group(2) == 'Discard': destination = "the Discard Pile" # If the tokens are discarded, do nothing
      else: 
         breakadd -= 1 # We decrease the transfer variable by one, to make sure we announce the correct total.
         break # If there's no more tokens to transfer, break out of the loop.
   if action.group(2) == 'Hoard': 
      shared.CROE = CROEAdjust(shared.counters['Guild Hoard'].value)
      destination += ' (Total:{}.CROE:{})'.format(shared.counters['Guild Hoard'].value, shared.CROE)
   announceString = "{} transfer {} spice from {} to {}".format(announceText, transfer + breakadd, targetCard, destination)
   if not manual: notify('--> {}.'.format(announceString))
   else: return announceString
   
def TokensX(Autoscript, announceText, card, targetCard = None, manual = False, n = 0):
   if not targetCard: targetCard = card # If there's been to target card given, assume the target is the card itself.
   action = re.search(r'\b(Assign|Remove)([0-9]+)(Deferment|Spice|Program)', Autoscript)
   if action.group(3) == 'Deferment' : token = Deferment_Token
   elif action.group(3) == 'Spice' : token = Spice
   elif action.group(3) == 'Program' : token = Program
   else: 
      whisper("Wat Token? [Error in autoscript!]")
      return 'ABORT'
   multiplier = per(Autoscript, card, n, targetCard, manual)
   if action.group(1) == 'Assign': modtokens = num(action.group(2)) * multiplier
   else: modtokens = -num(action.group(2)) * multiplier
   targetCard.markers[token] += modtokens
   autoscriptOtherPlayers('Generated{}'.format(action.group(3)),modtokens)
   announceString = "{} {} {} {} tokens to {}".format(announceText, action.group(1), abs(modtokens), action.group(3), targetCard)
   if not manual and multiplier > 0: notify('--> {}.'.format(announceString))
   else: return announceString

def DrawX(Autoscript, announceText, card, targetCard = None, manual = False, n = 0): # Function for drawing X Cards from the house deck to your hand.
   action = re.search(r'\bDraw([0-9]+)Card', Autoscript)
   draw = num(action.group(1))
   multiplier = per(Autoscript, card, n, targetCard, manual)
   drawMany(me.piles['House Deck'], draw * multiplier, silent)
   announceString = "{} draw {} cards to their hand".format(announceText, draw * multiplier)
   if not manual and multiplier > 0: notify('--> {}.'.format(announceString))
   else: return announceString

def ModifyStatus(Autoscript, announceText, card = None, targetCard = None, manual = False):
   action = re.search(r'\b(Engage|Disengage|Subdue|Deploy|Discard)(Target|Parent)', Autoscript)
   if action.group(1) == 'Engage' and engage(targetCard, silent = True, force = 'Engage') != 'ABORT': pass
   elif action.group(1) == 'Disengage'and engage(targetCard, silent = True, force = 'Disengage') != 'ABORT': pass
   elif action.group(1) == 'Subdue' and subdue(targetCard, silent = True, force = 'Subdue') != 'ABORT': pass
   elif action.group(1) == 'Deploy' and subdue(targetCard, silent = True, force = 'Deploy') != 'ABORT': pass
   elif action.group(1) == 'Discard': whisper(":::Note::: No automatic discard action is taken. Please ask the owner of the card to do take this action themselves.") # We do not discard automatically because it's easy to make a mistake that will be difficult to undo this way.
   else: return 'ABORT'
   announceString = "{} {} {}".format(announceText, action.group(1), targetCard)
   if not manual: notify('--> {}.'.format(announceString))
   else: return announceString

def StealX(Autoscript, announceText, card, targetCard = None, manual = False, n = 0):
   action = re.search(r'\b(Steal|Pay)([0-9]+)(Solaris|Spice|Favor)', Autoscript)
   if targetCard and re.search(r'toGovernor', Autoscript): targetPL = targetCard.controller
   elif targetCard and re.search(r'toOwner', Autoscript): targetPL = targetCard.owner
   else:
      playerChoice = 'Please select target player\n\n'
      for idxPL in range(len(players)):
         playerChoice += "{}: {}\n".format(idxPL, players[idxPL])
      idxPL = chooseWell(len(players), playerChoice, 0)
      if idxPL == None: return 'ABORT'
      targetPL = players[idxPL]
   if targetPL == me: return announceText # If the player is us, there's nothing to do anyway
   multiplier = per(Autoscript, card, n, targetCard, manual)
   if action.group(1) == 'Pay': 
      multiplier *= -1 # If the action to pay someone, then we reverse the numbers.
      extraText = 'to'
   else: extraText = 'from'
   count = num(action.group(2))
   if action.group(3) == 'Solaris': 
      me.Solaris += count * multiplier
      targetPL.Solaris -= count * multiplier
   elif action.group(3) == 'Spice': 
      me.Spice += count * multiplier
      targetPL.Spice -= count * multiplier
   elif action.group(3) == 'Favor': 
      me.Favor += count * multiplier
      targetPL.Favor -= count * multiplier
   announceString = "{} {} {} {} {} {}".format(announceText, action.group(1), abs(count * multiplier), action.group(3), extraText, targetPL)
   if not manual and multiplier > 0: notify('--> {}.'.format(announceString))
   else: return announceString

def UseCustomAbility(Autoscript, announceText, card, targetCard = None):
   action = re.search(r'\bUseCustomAbility{([A-Za-z0-9 ,]+)}', Autoscript)
   if not action: return 'ABORT' # Bad string on card property's AutoScript.
   if action.group(1) == 'The Shield Wall, Great Barrier Range':
      SpiceProduce = re.search(r'(Prod|Hoard)([0-9]+)Spice', targetCard.AutoScript)
      if not SpiceProduce: cost = 1
      else: cost = num(SpiceProduce.group(2))
      if payCost(cost, silent) == 'OK':
         announceText = '{} engaged {} and paid {} in order to disengage {}.'.format(me, card, SpiceProduce.group(2), targetCard)
         announceText = ModifyStatus('DisengageTarget', announceText, card, targetCard, True)
         if announceText == 'ABORT': me.Solaris += cost
         return announceText
      else: 
         notify("Couldn't pay the cost for {}'s ability".format(card))
         autoscriptCostUndo(Autoscript, card)
   else: # Is the custom script is unimplemented, abort.
      return "{} use the card's custom ability (Unimplemented! {} will have to take the necessary actions manually)".format(announceText,me)

def autoscriptCostUndo(Autoscript, card):
   whisper("--> Undoing action...")
   actionCost = re.match(r"\bC([ES0])F?([1-9]?)", Autoscript)
   if actionCost.group(1) == 'E': 
      random = rnd(10,5000) # Need to wait a bit or card is left engaged but program thinks it's not o.O
      card.orientation = Rot0
   if actionCost.group(1) == 'S': card.isFaceUp = True
   if num(actionCost.group(2)) > 0: me.Favor += num(actionCost.group(2))
   
def per(Autoscript, card = None, count = 0, targetCard = None, manual = False): # This function goes through the autoscript and looks for the words "per<Something>". Then figures out what the card multiplies its effect with, and returns the appropriate multiplier.
   per = re.search(r'\b(per|upto)(Assigned|Target|Parent|Generated|Deployed|Petitioned|Transferred|Bought)?([{A-Z][A-Za-z0-9,_ {}]*)[-]?', Autoscript) # We're searching for the word per, and grabbing all after that, until the first dash "-" as the variable.
   if per: # If the  search was successful...
      if per.group(2) and per.group(2) == 'Target': useC = targetCard # If the effect is targeted, we need to use the target's attributes
      else: useC = card # If not, use our own.
      if per.group(3) == 'X': multiplier = count
      elif per.group(3) == 'Intrigue': multiplier = num(useC.Intrigue) * chkPlayer(Autoscript, useC.controller, False)
      elif per.group(3) == 'Arbitration': multiplier = num(useC.Arbitration) * chkPlayer(Autoscript, useC.controller, False)
      elif per.group(3) == 'Battle': multiplier = num(useC.Battle) * chkPlayer(Autoscript, useC.controller, False) 
      elif per.group(3) == 'Dueling': multiplier = num(useC.Dueling) * chkPlayer(Autoscript, useC.controller, False) 
      elif per.group(3) == 'Weirding': multiplier = num(useC.Weirding) * chkPlayer(Autoscript, useC.controller, False) 
      elif per.group(3) == 'Prescience': multiplier = num(useC.Prescience) * chkPlayer(Autoscript, useC.controller, False) 
      elif per.group(3) == 'Resistance': multiplier = num(useC.Resistance) * chkPlayer(Autoscript, useC.controller, False) 
      elif per.group(3) == 'Command': multiplier = num(useC.Command) * chkPlayer(Autoscript, useC.controller, False) 
      elif per.group(3) == 'DeploymentCost': multiplier = num(useC.properties['Deployment Cost']) * chkPlayer(Autoscript, useC.controller, False) 
      elif per.group(3) == 'CROE': multiplier = shared.CROE
      elif re.search(r'CROE(plus|minus)([0-6])', per.group(3)):
         CROEregex = re.search(r'CROE(plus|minus)([0-6])', per.group(3))
         if CROEregex.group(1) == 'plus': multiplier = CROEsnapshot + num(CROEregex.group(1))
         else: multiplier = shared.CROE - num(CROEregex.group(2))
      elif count: multiplier = num(count) * chkPlayer(Autoscript, card.controller, manual) # All non-special-rules per<somcething> requests use this formula.
                                                                                           # Usually there is a count sent to this function (eg, number of favour purchased) with which to multiply the end result with
                                                                                           # and some cards may only work when a rival owns or does something.
      elif per.group(2): return 1 * chkPlayer(Autoscript, card.controller, manual) # To be able to grab those not yet implemented, or run manually.
      else:
         if re.search(r'Targeted', Autoscript): return 1 # Temporary fix for that give according to the attached cards. So that they can still work manually until I implement that.
         perItems = per.group(3).split('_or_')     
         perItemPool = [] # A list with all the properties we'll need to match on each card on the table.
         cardProperties = [] #we're making a big list with all the properties of the card we need to match
         multiplier = 0
         for perItem in perItems:
            subItems = perItem.split('_and_')
            for subItem in subItems:
               regexCondition = re.search(r'{?([A-Z][A-Za-z0-9, ]*)}?', subItem)
               perItemPool.append(regexCondition.group(1))
         for c in table: # Go through each card on the table and gather its properties, then see if they match.
            del cardProperties[:] # Cleaning the previous entries
            cardProperties.append(c.name)
            cardProperties.append(c.Allegiance)
            cardProperties.append(c.Type)
            cardSubtypes = c.Subtype.split('.')
            for cardSubtype in cardSubtypes:
               strippedCS = cardSubtype.strip() # Remove any leading/trailing spaces. We need to use a new variable, because we can't modify the loop iterator.
               if strippedCS: cardProperties.append(strippedCS) # If there's anything left after the stip (i.e. it's not an empty string anymrore) add it to the list.
            cardProperties.append(c.Decktype)
            perCHK = True
            for perItem in perItemPool: # Now we check if the card properties include all the properties we need
               if perItem not in cardProperties: perCHK = False # The perCHK starts as True. We only need one missing item to turn it to False, since they all have to exist.
            if perCHK: multiplier += 1 # If the perCHK remains 1 after the above loop, means that the card matches all our requirements.
      if per.group(1) == 'upto': # If we're using an "upto" autoscript instead of per, the player can choose any number up to the max we found.
         choiceText = re.search(r':([A-Z][A-Za-z]+)[0-9]+([A-Z][A-Za-z]+)', Autoscript)
         choice = multiplier + 1
         while choice > multiplier:
            choice = askInteger("{} how many {}?\n(Max {})".format(choiceText.group(1), choiceText.group(2), multiplier), multiplier)
            if not choice: multiplier = 0
            elif choice <= multiplier: multiplier = choice
   else: multiplier = 1 # If the search was not successful, then return a mutliplier of 1.
   return multiplier

def chkPlayer(Autoscript, governor, manual):
# Function returns 1 if the card is not only for rivals, or if it is for rivals and the card being activated it not ours.
# This is then multiplied by the multiplier, which means that if the card activated only works for Rival's cards, our cards will have a 0 gain.
# This will probably make no sense when I read it in 10 years...
   byRival = re.search(r'byRival', Autoscript)
   byMe = re.search(r'byMe', Autoscript)
   if manual: return 1 #manual means that the actions was called by a player double clicking on the card. In which case we always do it.
   elif not byRival and not byMe: return 1 # If the card has no restrictions on being us or a rival.
   elif byRival and governor != me: return 1 # If the card needs to be played by a rival.
   elif byMe and governor == me: return 1 # If the card needs to be played by us.
   else: return 0 # If all the above fail, it means that we're not supposed to be triggering, so we'll return 0 which will make the multiplier 0.
   
def autoscriptOtherPlayers(lookup, count = 1):
# This function is called from other functions in order to go through the table and see if other players have any cards which would be activated by it.
# For example a card that would produce solaris whenever a desert was engaged. I would have the engage() function call autoscriptOtherPlayers('DesertEngaged')
   if not Automation: return # If automations have been disabled, do nothing.
   for card in table:
      if not card.isFaceUp: continue # Don't take into accounts cards that are subdued but we've peeked at them.
      costText = '{} activates {} to'.format(card.controller, card) 
      if re.search(r'{}'.format(lookup), card.AutoScript): # Search if in the script of the card, the string that was sent to us exists. The sent string is decided by the function calling us, so for example the ProdX() function knows it only needs to send the 'GeneratedSpice' string.
         GainX(card.AutoScript, costText, card, n = count) # If it exists, then call the GainX() function, because cards that automatically do something when other players do something else, always give the player something directly.

def chkDeployAutoscripts(card): # This function is called whenever a card is deployed to check if any other cards on the table will trigger from it
   if re.search(r'Mentat', card.Subtype): autoscriptOtherPlayers('DeployedMentat')
   if re.search(r'Equipment', card.Subtype): autoscriptOtherPlayers('DeployedEquipment')
   if re.search(r'Holding', card.Type): autoscriptOtherPlayers('DeployedHolding')
   if re.search(r'WhileDeployed', card.AutoScript): whileDeployedEffects(card)

def chkPetitionAutoscripts(card): # This function is called whenever a card is petition to check if any other cards on the table will trigger from it
   if re.search(r'Holding', card.Type): autoscriptOtherPlayers('PetitionedHolding')

def chkRemoveAutoscripts(card): # This function is called whenever a card is subdued or otherwise leaves active play, to check if any effects on it need to be reversed.
   if re.search(r'WhileDeployed', card.AutoScript): whileDeployedEffects(card, 'Remove')
   
def whileDeployedEffects(card, action='Deploy'): # This script defines effects that happen and stick around only while a card is deployed.
   global handsize, assemblysize
   effect = re.search(r'WhileDeployed:(Gain|Accrue)([0-9]+)(AssemblyLimit|HandSize|XtraDeferment)', card.Autoscript)
   effectNR = num(effect.group(2))
   if effect.group(1) == 'Gain':
      if action == 'Remove': effectNR *= -1 # When removing card from play (subduing or discarding), we reverse the effects.
      if effect.group(3) == 'AssemblyLimit': 
         if card.controller == me: assemblysize += effectNR
         affectedText = 'Assembly Limit'
      if effect.group(3) == 'HandSize': 
         if card.controller == me: handsize += effectNR
         affectedText = 'Hand Size'
      # If we're not the controller of the card, this means that we're deploying/removing another player's card with an autoscript, so we don't want their effect to affect us.
      if card.controller == me: notify("--> {} has modified their {} by {}".format(me, affectedText, addPos(effectNR)))
      else: notify("--> {} has been {}'d by {}. {} needs to manually modify their {} by {}".format(card, action, me, card.controller, affectedText, addPos(effectNR)))

def customScript(card):
# This function has specific autoscripts tailored to specific cards which have fairly unique effects.
   custom = re.search(r'{Custom:([A-Za-z ]+)', card.Autoscript)
   if custom.group(1) == 'Carthag Engineering' or custom.group(1) == 'Arrakeen Water Facilities': 
      if re.search('Carthag', custom.group(1)): targetC = findTarget('Targeted-on{Carthag}')
      else: targetC = findTarget('Targeted-on{Arrakeen, Capital of Arrakis}')
      if not targetC: return
      if engage(card, silent = True, force = 'Engage') == 'ABORT': return
      elif targetC.controller == me:
         choice = 2
         while choice > 1:
            choice = askInteger("You are the governor of {}. What ability do you want to use?\n\n0: Gain 3 Solaris\n1: Gain 3 Favor".format(targetC.name), 0)
            if choice == None: return # If the player closed the window, abort.
         if choice == 0: GainX('Gain3Solaris', '{} engages {} to'.format(me, card), card)
         else: GainX('Gain3Favor', '{} engages {} to'.format(me, card), card) # We pass a custom autostring for what we want to do and call the GainX() function directly.
      else:
         choice = 2
         while choice > 1:
            choice = askInteger("{} is the governor of {}. What ability do you want to use?\n\n0: Take 3 Solaris from {} (Player must accept and be able to pay)\n1: Gain 3 Favor".format(targetC.controller, targetC.name, targetC.controller), 0)
            if choice == None: return # If the player closed the window, abort.
            elif choice == 0 and targetC.controller.Solaris < 3: 
               whisper("{} does not have enough Solaris. You can only gain 3 favor".format(targetC.controller))
               choice = 2
         if choice == 0: 
            notify ("{}, taking it from {}".format(GainX('Gain3Solaris', '{} engages {} to'.format(me, card), card, manual = True), targetC.controller))
            targetC.controller.Solaris -= 3
         else: GainX('Gain3Favor', '{} engages {} to'.format(me, card), card)
   else: engage(card)