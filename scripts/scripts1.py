    # Python Scripts for the Doomtown CCG definition for OCTGN
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

phases = [
    '{} is currently in the Pre-game Setup Phase'.format(me),
    "It is now Opening Interval. Disengage all cards then add Deferment Tokens and finally Assign Initiative",
    "It is now House Interval",
    "It is now Closing Interval. Perform Assembly Administration and then Hand Administration"]

#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------

import re

loud = 'loud' # So that I don't have to use the quotes all the time in my function calls
silent = 'silent' # Same as above
Xaxis = 'x'  # Same as above
Yaxis = 'y'	 # Same as above


#---------------------------------------------------------------------------
# Global variables
#---------------------------------------------------------------------------

playerAllegiance = None # Variable to keep track of the player's outfit.
playerside = None # Variable to keep track on which side each player is
playeraxis = None # Variable to keep track on which axis the player is
handsize = 7 # Used when automatically refilling your hand
favorBought = 0
CHOAMDone = 0


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

def chooseSide(): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global playerside, playeraxis
   if playerside == None:  # Has the player selected a side yet? If not, then...
      if table.isTwoSided():
         if me.hasInvertedTable():
            playeraxis = Yaxis
            playerside = -1
         else:
            playeraxis = Yaxis
            playerside = 1
      else:
         askside = askInteger("On which side do you want to setup?: 1 = Right, 2 = Left, 3 = Bottom, 4 = Top, 0 = None (All your cards will be put in the middle of the table and you'll have to arrange them yourself", 1) # Ask which axis they want,
         if askside == 1:
            playeraxis = Xaxis
            playerside = 1
         elif askside == 2:
            playeraxis = Xaxis
            playerside = -1
         elif askside == 3:
            playeraxis = Yaxis
            playerside = 1
         elif askside == 4:
            playeraxis = Yaxis
            playerside = -1
         else:
            playeraxis = None
            playerside = 0


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


#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def nextPhase(group, x = 0, y = 0):  
# Function to take you to the next phase. 
   mute()
   if shared.Phase == 3: 
      shared.Phase = 1 # In case we're on the last phase (Closing Interval), go back to the first game phase (Opening Interval)
   else: shared.Phase += 1 # Otherwise, just move up one phase
   showCurrentPhase()

def showCurrentPhase(): # Just say a nice notification about which phase you're on.
   notify(phases[shared.Phase].format(me))

def goToSetup(group, x = 0, y = 0):  # Go back to the Pre-Game Setup phase.
# This phase is not rotated with the nextPhase function as it is a way to basically restart the game.
# It also serves as a control, so as to avoid a player by mistake using the setup function during play.
   mute()
   shared.Phase = 0
   showCurrentPhase() # Remind the players which phase it is now

def flipCoin(group, x = 0, y = 0):
    mute()
    n = rnd(1, 10)
    if n < 6:
        notify("{} flips heads.".format(me))
    else:
        notify("{} flips tails.".format(me))

#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def engage(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify('{} engages {}'.format(me, card))
    else:
        notify('{} disengages {}'.format(me, card))

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

def subdue(card, x = 0, y = 0):
    mute()
    faceup = 0
    if not card.isFaceUp: # Horrible hack until the devs can allow me to look at facedown card properties.
       card.isFaceUp = not card.isFaceUp  # Gah!
       type = card.Type
       cost = num(card.properties['Deployment Cost']) 
       card.isFaceUp = not card.isFaceUp # GAH!
#    notify("{} Deferments. {} Cost(int). Cost(str). {} is the difference.".format(card.markers[Deferment_Token], cost, card.properties['Deployment Cost'], cost - card.markers[Deferment_Token]))
    if card.markers[Assembly] == 0:
        if card.isFaceUp:
            notify("{} subdues {}.".format(me, card))
            card.isFaceUp = False
        elif card.markers[Deferment_Token] == 0 and cost > 0:                         
            notify("{} deploys {} which had 0 deferment tokens.".format(me, card))   
            card.isFaceUp = True
        elif card.markers[Deferment_Token] < cost:
            if type == 'Event': 
                if confirm("Events cannot normally be played unless they have equal or more deferment tokens than their deployment cost. Are you sure you want to do this?"):
                    card.isFaceUp = True
                    notify("{} deploys {} with {} deferment tokens.".format(me, card, card.markers[Deferment_Token]))
                    card.markers[Deferment_Token] = 0
            elif confirm("Card has less deferment tokens than its deployment cost. Do you need to automatically pay the difference remaining from your treasury?"):
                card.isFaceUp = True
                payCost(cost - card.markers[Deferment_Token])
                notify("{} pays {} and deploys {}.".format(me, cost - card.markers[Deferment_Token], card))
                card.markers[Deferment_Token] = 0
        else:
            card.isFaceUp = True
            notify("{} deploys {}.".format(me, card))
            card.markers[Deferment_Token] = 0
    else:
        if card.isFaceUp:
            notify("{}'s petition for {} was unsuccesful.".format(me, card))
            card.isFaceUp = False
        else:
            card.isFaceUp = True
            notify("{} initiates a petition for {}.".format(me, card))

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

def CHOAMbuy(group, x = 0, y = 0): # This function allows the player to purchase spice through checks and balances to avoid mistakes.
    global CHOAMDone # Import the variable which informs us if the player has done another CHOAM exchange this turn
    mute()
    spiceNR = 0 # Variable we use to remember how much spice they want to buy
    if CHOAMDone == 1: # If the player has already done a CHOAM exchange, remind them, but let them continue if they want, in case they have a card effect allowing them to do so.
       if not confirm("You've already done a CHOAM exchange this round. Are you sure you're allowed to do another?"): return
       else: notify("{} is performing another CHOAM Exchange this round.".format(me)) # However if they proceed, alter the message to point it out.
    if CHOAMDone == 0: notify("{} is performing a CHOAM Exchange.".format(me)) # Inform everyone that the player is beggingin a CHOAM exchange.
    while spiceNR > 3 or spiceNR == 0: # We start a loop, so that if the player can alter their number if they realize they don't have enough.
       spiceNR = askInteger("How much spice do you want to buy (Max 3)? Remember that you can only do one CHOAM Exchange per round!", 0)
       if spiceNR == 0 or spiceNR == None : return # If the player answered 0 or closed the window, cancel the exchange.
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
       spiceNR = askInteger("How much spice do you want to sell (Max 3)? Remember that you can only do one CHOAM Exchange per round!", 0)
       if spiceNR == 0 or spiceNR == None : return
       elif spiceNR > 0 and spiceNR < 4: 
          if me.Spice - spiceNR < 0: 
             whisper("You do not have this amount of spice to sell. You have only {} to sell.".format(me.Spice))
             spiceNR = 0 # We do this so that the player stays in the loop and gets asked again
          else: 
             fullcost = completeSpiceCost(-spiceNR)
             me.Solaris +=fullcost
             me.Spice -= spiceNR
             shared.counters['Guild Hoard'].value += spiceNR
             shared.CROE = CROEAdjust(shared.counters['Guild Hoard'].value)
             notify("{} has sold {} Spice for {}. The Guild Hoard now has {} Spice left and the CROE is set at {}".format(me, spiceNR, fullcost, shared.counters['Guild Hoard'].value, shared.CROE))
             CHOAMDone = 1
       else:
          whisper("You cannot sell more than 3 spice per CHOAM Exchange.")


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
       favorNR = askInteger("How much Imperial favor do you want to purchase (Max 5)? Remember that you can only purchase favor once per round!", 0)
       if favorNR == 0 or favorNR == None : return
       elif favorNR > 0 and favorNR < 6: 
          fullcost = favorNR * 2
          if me.Solaris < fullcost: 
             whisper("You do not have enough solaris in your treasury to buy {} favor. You need at least {}".format(favorNR, fullcost))
             favorNR = 0 # We do this so that the player stays in the loop and gets asked again
          else: 
             me.Solaris -=fullcost
             me.Favor += favorNR
             notify("{} has bought {} favor. They now have {} favor".format(me, favorNR, me.Favor))
             favorBought = 1
       else:
          whisper("You cannot buy more than 5 favor per exchange.")


#------------------------------------------------------------------------------
# Hand Actions
#------------------------------------------------------------------------------

def payCost(count = 1, notification = silent): 
   count = num(count)
   if me.Solaris < count:  
      if notification == 'loud' and count > 0: notify("{} was supposed to pay {} Solaris but only has {} in their house treasury. Assuming card effect used. **No Solaris has been taken!** Please modify your treasury manually as necessary.".format(me, count, me.Solaris))   
   else: 
      me.Solaris -= count
      if notification == 'loud' and count > 0: notify("{} has paid {} Solaris. {} is left their house treasury".format(me, count, me.Solaris))  

def play(card, x = 0, y = 0):
    mute()
    src = card.group
    card.moveToTable(0, 0)
    notify("{} plays {} from his {}.".format(me, card, src.name))
    payCost(card.properties['Deployment Cost'], loud) # Take cost out of the bank, if there is any.

def setup(group):
# This function is usually the first one the player does. It will setup their homeworld on their side of the table. 
# It will also shuffle their decks, setup their Assembly and Dune and draw 7 cards for them.
   if shared.Phase == 0: # First check if we're on the pre-setup game phase. 
                     # As this function will play your whole hand and wipe your counters, we don't want any accidents.
      if not confirm("Have bought all the favour and spice you'll need with your bonus solaris?"): return
      global playerside, playerAllegiance # Import some necessary variables we're using around the game.
      DuneinHand = 0
      mute()
      chooseSide() # The classic place where the players choose their side.
      me.piles['Imperial Deck'].shuffle() # First let's shuffle our decks now that we have the chance.
      me.piles['House Deck'].shuffle()
      for card in group: # For every card in the player's hand... (which should be just their homeworld and possibly some plans)
         notify("card is {}. Subtype is {}". format (card, card.subtype))
         if re.search(r'Homeworld', card.Subtype) and card.Type == 'Holding':  # If it's the homeworld...
            placeCard(card,'SetupHomeworld')
            playerAllegiance = card.Allegiance # We make a note of the Allegiance the player is playing this time (used later for automatically losing favour)
         if re.search(r'Program', card.Subtype) and card.Type == 'Plan':  # If it's a program...
            placeCard(card,'SetupProgram')
            payCost(card.properties['Deployment Cost']) # Pay the cost of the dude
         if card.model == '2037f0a1-773d-42a9-a498-d0cf54e7a001': # If the player has put Dune in their hand as well...
            placeCard(card,'SetupDune')
            DuneinHand = 1 # Note down that player brought their own Dune, so that we don't generate a second one.
      if DuneinHand == 0: # If the player didn't bring their own Dune, generate a new one on their side.
         Dune = table.create("2037f0a1-773d-42a9-a498-d0cf54e7a001", 0, 0, 1, True) # Create a Dune card in the middle of the table.
         placeCard(Dune,'SetupDune')
      me.Solaris += 20     
      refill() # We fill the player's play hand to their hand size (usually 5)
      notify("{} is playing {}. Their starting Solaris is {} and their Imperial Favour is {}".format(me, playerAllegiance, me.Solaris, me.Favor))  
      setupAssembly() # Setup the 3 imperial cards which will be our assembly.
   else: whisper('You can only setup your starting cards during the Pre-Game setup phase') # If this function was called outside the pre-game setup phase
            
def placeCard(card,type = None):
# This function automatically places a card on the table according to what type of card is being placed
# It is called by one of the various custom types and each type has a different value depending on if the player is on the X or Y axis.
   if playeraxis == Xaxis:
#      if type == 'HireAide': # Not implemented yet
#         card.moveToTable(homeDistance(card) + (playerside * cwidth(card,-4)), 0)
      if type == 'SetupHomeworld':
         card.moveToTable(homeDistance(card), cheight(card)* -4 * playerside) # We move it to one side depending on what side the player chose.
      if type == 'SetupDune':
         card.moveToTable(homeDistance(card), cheight(card)* -3 * playerside) # We move it to one side depending on what side the player chose.
         card.isFaceUp = False
      if type == 'SetupProgram':
         card.moveToTable(homeDistance(card) + (playerside * cwidth(card,-4)), cheight(card)* -4 * playerside)
         card.sendToBack()
         # We move them behind the homeworld
   elif playeraxis == Yaxis:
#      if type == 'HireAide':# Not implemented yet
#         card.moveToTable(0,homeDistance(card) + (playerside * cheight(card,-4)))
      if type == 'SetupHomeworld':
         card.moveToTable(cwidth(card)* -4 * playerside,homeDistance(card)) 
      if type == 'SetupDune':
         card.moveToTable(cwidth(card)* -3 * playerside,homeDistance(card)) 
         card.isFaceUp = False
      if type == 'SetupProgram': 
         card.moveToTable(cwidth(card)* -4 * playerside,homeDistance(card) + (playerside * cheight(card,-4)))
         card.sendToBack()
   else: card.moveToTable(0,0)

def homeDistance(card):
# This function returns the distance from the middle each player's homeworld will be setup towards their playerSide. 
# This makes the code more readable and allows me to tweak these values from one place
   if table.isTwoSided(): return (playerside * cwidth(card) / 2) # players on an inverted table are placed half a card away from their edge.
   else:
      if playeraxis == Xaxis:
         return (playerside * cwidth(card) * 5) # players on the X axis, are placed 5 times a card's width towards their side (left or right)
      elif playeraxis == Yaxis:
         return (playerside * cheight(card) * 3) # players on the Y axis, are placed 3 times a card's height towards their side (top or bottom)

def cardDistance(card):
# This function returns the size of the card towards a player's side. 
# This is useful when playing cards on the table, as you can always manipulate the location
#   by multiples of the card distance towards your side
# So for example, if a player is playing on the bottom side. This function will always return a positive cardheight.
#   Thus by adding this in a moveToTable's y integer, the card being placed will be moved towards your side by one multiple of card height
#   While if you remove it from the y integer, the card being placed will be moved towards the centre of the table by one multiple of card height.
   if playeraxis == Xaxis:
      return (playerside * cwidth(card))
   elif playeraxis == Yaxis:
      return (playerside * cheight(card))

def setHandSize(group): # A function to modify a player's hand size. This is used during Closing Interval when refilling the player's hand automatically.
   global handsize
   handsize = askInteger("What is your current hand size?", handsize)
   if handsize == None: handsize = 7
   notify("{} sets their hand size to {}".format(me, handsize))
   
def refill(group = me.hand): # Refill the player's hand to its hand size.
   global handsize
   playhand = len(me.hand) # count how many cards there are currently there.
   if playhand < handsize: drawMany(me.piles['House Deck'], handsize - playhand, silent) # If there's less cards than the handsize, draw from the deck until it's full.

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
    i = 0
    while i < times:
        card = group.top()
        if playeraxis == Yaxis: 
            group.top().moveToTable(cwidth(card)* -6 - playerside * i * cwidth(card), cardDistance(card) * 2,True)
            card.markers[Assembly] = 1
        else: 
            group.top().moveToTable(cardDistance(card) * 2, cwidth(card)* -6 - playerside * i * cheight(card),True)
            card.markers[Assembly] = 1
        i += 1

def setupAssembly(group = me.piles['Imperial Deck']):
    imperialDraw(times = 3)
#    notify("{} Setup his Assembly.".format(me))
    

def shuffle(group):
  group.shuffle()

def drawMany(group, count = None, notification = loud): # This function draws a variable number cards into the player's hand.
    if len(group) == 0: return
    mute()
    if count == None: count = askInteger("Draw how many cards?", 7)
    for c in group.top(count): c.moveTo(me.hand)
    if notification == loud : notify("{} draws {} cards to their play hand.".format(me, count)) # And if we're "loud", notify what happened.

