Solaris = ("Solaris", "b30701c1-d925-45fc-afe4-6c341a103f32")
Spice = ("Spice", "491cf29f-224c-4d8b-8e2d-58467686be88")
Favor = ("Favor", "6ed72fed-4a63-4f38-95bb-424cbbcdd427")
Deferment_Token = ("Deferment_Token", "f8f34145-60a8-4d2c-92e9-25824982944e")
Assembly = ("Imperial Assembly", "a5634dc5-ffd0-4428-95b5-13c6bb3ff00d")

phases = [
    'It is currently in the Pre-game Setup Phase',
    "It is now {}'s Opening Interval- Disengage Phase",
    "It is now {}'s Opening Interval- Deferment Phase",
    "It is now {}'s Opening Interval- Initiative Phase",
    "It is now {}'s House Interval",
    "It is now {}'s Closing Interval",
    "It is now {}'s Assembly Administration Phase",
    "It is now {}'s Hand Administration Phase",
    "{} finished his/her turn."]

phaseIdx = 0

loud = 'loud' # So that I don't have to use the quotes all the time in my function calls
silent = 'silent' # Same as above

def nextPhase(group, x = 0, y = 0):
    global phaseIdx
    phaseIdx += 1
    showCurrentPhase(group)

def showCurrentPhase(group, x = 0, y = 0):
    notify(phases[phaseIdx].format(me))

def goToOpeningInterval(group, x = 0, y = 0):
    global phaseIdx
    phaseIdx = 1
    showCurrentPhase(group)

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

#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def flipCoin(group, x = 0, y = 0):
    mute()
    n = rnd(1, 2)
    if n == 1:
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
    card.isFaceUp = not card.isFaceUp # Horrible hack until the devs can allow me to look at facedown card properties.
    type = card.Type             # Gah!
    cost = num(card.properties['Deployment Cost']) # GAH!
    card.isFaceUp = not card.isFaceUp
    random = rnd(100, 4000)
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
    myCards = (card for card in table
               if card.controller == me
               and card.owner == me)
    for card in myCards:
        card.orientation &= ~Rot90
        if card.markers[Assembly] > 0 and card.isFaceUp:
             card.markers[Assembly] = 0
    notify("{} disengages all his cards.".format(me))

def addSolaris(card, x = 0, y = 0):
    mute()
    notify("{} adds 1 Solaris to {}.".format(me, card))
    card.markers[Solaris] += 1

def subSolaris(card, x = 0, y = 0):
    mute()
    notify("{} removes 1 Solaris from {}.".format(me, card))
    card.markers[Solaris] -= 1

def addSpice(card, x = 0, y = 0):
    mute()
    notify("{} adds a Spice token to {}.".format(me, card))
    card.markers[Spice] += 1

def subSpice(card, x = 0, y = 0):
    mute()
    notify("{} removes a Spice token from {}.".format(me, card))
    card.markers[Spice] -= 1

def addFavor(card, x = 0, y = 0):
    mute()
    notify("{} adds a Favor token to {}.".format(me, card))
    card.markers[Favor] += 1

def subFavor(card, x = 0, y = 0):
    mute()
    notify("{} removes a Favor token from {}.".format(me, card))
    card.markers[Favor] -= 1

def addDeferment(card, x = 0, y = 0):
    mute()
    notify("{} adds a Deferment token on {}.".format(me, card))
    card.markers[Deferment_Token] += 1

def subDeferment(card, x = 0, y = 0):
    mute()
    notify("{} removes a Deferment token on {}.".format(me, card))
    card.markers[Deferment_Token] -= 1

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
        if me.hasInvertedTable() == True: 
            group.top().moveToTable(400 - (i * group.top().width()) - (i * 15), -150,True)
            card.markers[Assembly] = 1
        else: 
            group.top().moveToTable((i * group.top().width()) + (i * 15)- 400, 150,True)
            card.markers[Assembly] = 1
        i += 1

def setupAssembly(group = me.piles['Imperial Deck']):
    imperialDraw(times = 3)
    notify("{} Setup his Assembly.".format(me))
    

def shuffle(group):
  group.shuffle()

def drawMany(group, count = None):
    if len(group) == 0: return
    mute()
    if count == None: count = askInteger("Draw how many cards?", 7)
    for c in group.top(count): c.moveTo(me.hand)
    notify("{} draws {} cards.".format(me, count))

