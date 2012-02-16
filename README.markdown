Dune CCG plugin for OCTGN
=========================

One of the most interesting and complex and deep CCGs ever devised, within the best Sci-Fi universe ever conceived. The Dune CCG is now available in OCTGN. You want more details? Then [look no further](http://boardgamegeek.com/thread/739664/god-created-dune-ccg-to-train-the-faithful-paul).

Note: This is just the game engine, you'll also need to download [the sets](http://octgn.gamersjudgement.com/viewtopic.php?f=42&t=236). If you've never played the Dune CCG before, you can find [the rulebook here](http://boardgamegeek.com/file/download/c6bw2c3cu/DuneRulebookv2.1.pdf).

Screenshots
-----------
(Click for larger size)

Sample screenshot of 1.0.6

[![](http://i.imgur.com/wTG33l.jpg)](http://i.imgur.com/wTG33.jpg)

Sample screenshot of 1.0.2

[![](http://i.imgur.com/vrLL5l.jpg)](http://i.imgur.com/vrLL5.jpg)

Changelog
---------

### 1.0.7 

* Made it so that the 2nd player's placement in a 2-sided table is shifted one card's height to their side. 
* Fixed the annoying initiative counter being bigger than the others.
* When starting a petition, the game will now ask you for your starting bid, and announce it to everyone.


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

- More testing of multiplayer setup. It *should* work OK for four player (if they remember to disable the inverted table), but without more testing I won't know.
- Need to fix the sets
-- Empty card Allegiances need to be turned to 'Neutral'
-- Imperial = 'Yes' and House ='No' is Silly. These properties need to be consolidated into one property called "Deck" or something.
-- Remove the word 'Event' from card subtypes