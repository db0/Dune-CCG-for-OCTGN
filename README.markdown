Dune CCG plugin for OCTGN
=========================

One of the most interesting and complex and deep CCGs ever devised, within the best Sci-Fi universe ever conceived. The Dune CCG is now available in OCTGN. You want more details? Then [look no further](http://boardgamegeek.com/thread/739664/god-created-dune-ccg-to-train-the-faithful-paul).

Note: This is just the game engine, you'll also need to download [the sets](http://octgn.gamersjudgement.com/viewtopic.php?f=42&t=236). If you've never played the Dune CCG before, you can find [the rulebook here](http://boardgamegeek.com/file/download/c6bw2c3cu/DuneRulebookv2.1.pdf).

Screenshots
-----------
(Click for larger size)

Sample screenshot of 1.1.2 (A 3-Player game in progress)

[![](http://i.imgur.com/wt1rXl.jpg)](http://i.imgur.com/wt1rX.jpg)

Sample screenshot of 1.1.2 (Another 3-Player game in progress

[![](http://i.imgur.com/9jKNml.jpg)](http://i.imgur.com/9jKNm.jpg)

Changelog
---------

### 2.0.2

* Cards with effects per specific kind of card on the table, should now not take into account subdued cards that you've peeked at.
* Cancelling a petition should will clear all player bids.
* Double clicking on a subdued card will now try to deploy it, not engage it.
* You now can't setup unless you've gone to the pre-game setup phase first.
* Restarting the game should now also clear the holdings and persona placement variables.

### 2.0.1

Fixed small bug when sending spice produced by deserts straight to the CHOAM.

### 2.0.0

Big Changes! Card Automation is here!

**Important:** For this version, you'll require to update all your sets. [Use the provided patch](https://github.com/downloads/db0/Dune-CCG-for-OCTGN/Patch-to-2.0.x.o8p).

Basically, now most of the holdings, as well as some personas and resources have automated abilities, which means you double-click them and they perform their printed ability.
For most cards, this is something simple, like "Gain 2 Solaris" or something, but the scripts also support multiple-choice abilities, and even abilities with two or three different effects.
You can see if a card has been automated by using the Inspect Feature. This will tell you if it's Auto-Scripted or not (as well as show you the script for debugging purposes)

A lot of cards also are automated when they have passive abilities, such as making money when someone deploys some equipment, or when someone buys solaris and so on. You can also call these effect manually by clicking on the card, in case something went wrong.

The autoscripts support also cards that target other cards. To use those, you have to target first, and then use the ability. If you haven't selected a valid target, the script will abort and the game will inform you. If you've selected more than one valid target, the game will select the one who's been put the table earlier.
Targeting can also recognise if the target needs to be controlled by you or a rival.

Support also exists for cards with variable effects depending on the cards on the table. So for example a card that gives you 1 solaris per Desert, Harvester or Carryall, will take all these into account.

Abilities which trigger depending on assigned cards are not implemented correctly yet. They may seemingly work in some function, but you may have to complete things manually.

At the moment, plans & events don't have any automation, but might do this later if there's any interest or need.

### 1.1.8

* Added the [Orthodox Herbetarian](http://www.kullwahad.com/?p=264) fonts for the menu.
* Added a chat font that is similar to the font used in the Movie from 1984.

### 1.1.7

* Game will now take into account if any player has lost a petition in the past when they try to start a new one, and warn them.
* More robustness in the petitioning/bidding process
* Changed the name and moved the position of the Bid process. Now it's called "Petition: Start/End/Bid/Pass" and it is supposed to be **the** action to use in regards to petitions. This action can be called from both actions and table.
* Tweaked deployment points a bit again
* Fixed a few bugs with the payment of petitions

### 1.1.6

* Fixed bug in bidding contest when bid is called with no card targeted.
* Now Automated Closing Phase autorefills your assembly.
* New function to set your imperial assembly limit
* Fixed bug in the placement on top player.


### 1.1.5

* Fixed bug where you could not play 0-cost cards from hand
* Now decks are properly checked for allegiance legality and allegiances are properly stored. Favour should now be removed correctly for out-of-house imperial cards.
* Put the deployment cost of the card in the Place Bid window.
* New action to add marker to make a card an assembly card, since it was very common that people would try to move the card and remove the marker instead.
* When contesting a petition, the notification about the house which cannot start new petitions was wrong. Now points to card.owner.
* Opening phase will clear the shared variables, just as a security measure
* Events now stack on the opposite side than before and give even more space between them while on the Y-axis
* Created function to discard cards from the top of your house deck.
* Now programs will not receive deferment tokens until you deploy them for the first time.
* New action to reset the Guild Bank and/or CROE
* House placement for bottom player on the Y-axis now should leave a bit more space for holding and personas.

### 1.1.4

* Created a robust petitioning process. Start a petition with the subdue/deploy/petition card action. You bid on it with the a table action. If all other players have passed, the program will assume you have won and take action.
* Now Holdings and Personas are played next to each other on the table. 
* Moved around the starting positions a bit.

### 1.1.3

* Fixed Native Personas not deploying when subdued.
* Added option to play a card with less deferments than its cost, for no cost.
* Added counter labels on the player's summary
* Spice & CROE set appropriately for more than 2 players
* Setup action will now prompt for the amount of spice and favour to buy
* Closing interval will now not discard face-down but peeked at duration effects (eg, events)
* Fixed the wrong cost for the starting spice (Should be CROE+1)
* Starting a petition now sets your Bid counter
* If you have to draw cards but can't, the game notes that you probably lost.
* The Buying/Selling Solaris dialogue now informs how much the CROE is and how many Spice are left
* Added Program Tokens and relevant markers and scripts to add them on cards. (Required the new v1.0.4 markers file)
* Using the default action (i.e. double-click) on a face-down assembly card now will start a petition, rather than just engage it.
* Cancelling a Favor or CHOAM Exchange now informs of the fact.


### 1.1.2

* Events that have X deployment cost and 0 deferment tokens will not warn you before deploying
* Programs should now be placed better at start and also take 1 Solaris per program. Programs also stacked so that they're all visible.
* Event stacking should now leave a bit more space between them
* Fixed a bug with the allegiances code after making all cards with no allegiance have "None" in the Allegiances card property.

### 1.1.1

* Fixed not being able to petition cards for 0 solaris when that is their cost

### 1.1.0

Because of the changes below all existing sets at v0.0 are now incompatible with the current definition. Please download the available v1.0 sets or wait for the patch.

* Modified the card properties so that there is now only one property signifying the deck type of the card. Containing a value of either "Imperial" or "House". 
* Removed the card property "number" which seemingly has no purpose.

### 1.0.9

* Modified the card placements to make setup work for 3 and 4 players. 
* Added "Inspect Card" action to allow you to check cards with bad scans.
* Made the table much bigger. This means cards might seem smaller (you can zoom in to fix that) but this was necessary to provide enough space for 3-4 player games.

### 1.0.8

* Minor capitalization changes in card properties to make game compatible with the recent OCTGN Betas.

### 1.0.7 

* Made it so that the 2nd player's placement in a 2-sided table is shifted one card's height to their side. 
* Fixed the annoying initiative counter being bigger than the others.
* When starting a petition, the game will now ask you for your starting bid, and announce it to everyone.
* When petitioning a card, a small check to see that the player has enough solaris to start it.


### 1.0.6 

* Game will now check that for uniqueness on deployment as well
* Deck checking for Adversaries now works
* Removed debug notification from adversary checking.
* When playing a House card, the game will now check that you have at least one card of the same allegiance in your Imperial deck and want/announce it otherwise.
* If the player has placed Dune by mistake in their Imperial Deck, it will be automatically placed on their discard pile during Setup and player will be iformed
* Now when deploying an event, the game will check to see if you have the prerequisites (Homeworld for Imperium events, Dune fief for Dune events) and confirm/notify if you bypass.
* Small tweak so that events don't fall on top of each other.
* Game will check for Natives' prerequisites (dune fiefs) during deployment from being subdued as well and will confirm/notify.


### 1.0.5 (Untested)

* Removed some debug notifications during the setup phase
* Going to the pre-game setup phase will now reset your counters
* During the setup phase, the game will check your imperial deck for Allegiances conflicts and inform if your deck is illegal.
* When playing a native aide or petitioning a native Persona, the game will ask you to confirm, in case you do not control a Dune Fief
* When petiotining an Assembly card, the game will check if another player has the same card in the game, and will prevent you from petitioning it.
* When petitioning game will remind you if you need to lose favor, or if you can reduce the cost by discarding favor

### 1.0.4

* Added CHOAM Exchange functions for buying and selling Spice. This automatically stops players form doing 2 CHOAM Exchanges per turn, or buying/selling more than 3 spice per exchange, or from buying/selling when there is not  enough Solaris or Spice. These functions also automatically reset the CROE when the Guild Hoard is modified.
* Automatic Opening Interval functions (card disengage, adding deferal tokens, assign initiative)
* Automatic Closing Interval functions (hand refresh)
* Added Table option to Engage a card to produce X spice directly into the guild hoard, as it's a common function
* Added discard functions for table and hand
* Added action to mark cards as "Does not Disengage" and they will be ignored during the automated Opening Interval.
* Implemented function "Engage to produce spice in the Guild Hoard" for all those deserts.
* Made it so that Events are automatically played face-down (and the player is not charged their deployment cost)
* Made it so that Nexus events are automatically played with enough deferment tokens equal to their deployment cost, and the player is not charged their deployment cost either.
* When deploying events, the game will now note down and check if they are of the Imperium or Dune subtype. If the player has played one of the same subtype already, they will need to confirm the deployment and the notification will make it obvious as well.
* F1 - F3 now Jump between the 3 phases of each turn.

### 1.0.3

* Added Global Phase counter and made the phases global. Reduced phases to 3. Phases now change with ENTER
* Added player initiative counter. This will eventually be set automatically during the opening interval
* Added some (unimplemented) puchase/sell Spice and buy favor table actions. Purchase spice will automatically pay as much as the CROE and reset it afterwards
* Set the OCTGN required version to 3.0.0.8 since I'm using OCTGN3-only functions
* Added some complex functions for card placement regardless of card size. This will keep the same setup, even if I later decide to change card sizes.
* Created table setup script for the start. it automatically sets up your homeworld and Dune (even if you don't have it in your hand), shuffles both decks, draws 7 cards in your hand and performs the imperial assembly setup.
* Setup action requires the player to be on the "Pre-Game Setup phase"
* Removed the Assembly Setup action, since it's not required anymore
* Refresh All function now only works during the opening phase

### 1.0.2

* Removed the Add and Remove Solaris and Favour markers. As far as I know, there is no effect that would make you put solaris or favour markers on a card so these just clutter the menu.
* Fixed bug when adding deferment token and the notice said that you added a Favor token.
* Made the CROE and SPICE banks global and removed them from each player
* Playing a card from hand, automatically pays its cost if it has any, or notifies everyone if the player doesn't have enough money.
* Changed the subdue action name to "subdue/deploy/petition"
* Replaced the "draw card" function of the Imperial deck with a "Imperial Draw" function which puts the card immediately on the play area face down. with a special "Assembly" token on it.
* Replaced the "draw many" function of the Imperial deck with a "Setup Assembly" function which puts 3 imperial cards on the assuembly face down with the special "Assembly" token.
* Petitioning a facedown card with the Assembly card marker, will inform everyone that the card is up for petition. If successful, the player should move the card to his play area. Petitioning a face up card with an Assembly marker, will turn it face down again and inform that the petition was unsuccessful.
* Deploying a face down card (that doesn't have an "Assembly" marker) with less deferment tokens than its deployment cost will ask the player to pay the difference. It will also notify everyone is a player deploys something with 0 deferment tokens
* The "refresh all" function will remove Assembly markers from face up cards. This way, you can see which cards have just been put in from the assembly this turn.


Roadmap
-------

- Need to fix the sets
-- Remove the word 'Event' from card subtypes