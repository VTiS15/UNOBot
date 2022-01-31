# UNOBot <img align="right" src="https://user-images.githubusercontent.com/73805050/130341782-78d30da7-0313-44f5-889c-06ab7eb8de9a.png">
Improved from [Exium's work](https://top.gg/bot/565305035592957954), this is a Python bot that incorporates the popular card game, **UNO**, into your Discord server, because frankly their bot sucks.\
It allows Discord servers to play the game completely within text channels. Challenge your friends and climb the leaderboard!

# Features💡
* Play UNO! with your friends completely within text channels on Discord!
* Various optional game rules, including **StackCards** and **7-0**
* Two fun game modes - Original **UNO!** and **UNO FLIP!**
* Local and global **leaderboards**
* Check and show off your **stats**.
* Highly customizable player options, game and command settings

# Usage and Commands🛠️
Type the following `/u-` command to start a game of UNO.
```
/u-sg
# Starts a game, allowing users to join the game by reacting.
```
The bot will send a message to the your server. Users can react to the message to join the game in 30 seconds.\
After 30 seconds, if there are enough (>1) players, a text channel for every player will be created and players can use their channels to play their hands.\
<br/>
If you want to view command usage, read an in-depth guide on using the bot, or read the rules of UNO, type `/u.help` in your Discord server.
## Command Usage
The UNOBot uses the prefix `/u-` for commands.
| Command | Arguments | Description | Example |
| ------- | --------- | ----------- | ------- |
| `/u-help` | None | Prints **help info** |
| `/u-rules` | None | [UNO Rules](#rule) |
| `/u-guide`| (`start/play/commands/settings/options`) | Gives you a **guide** on using bot | `/u-guide start` |
| `/u-sg` | (@user mentions), (game settings) | **Starts a game** in the server | `/u-sg @VTiS @Dong Flip`| 
| `/u-eg` || **Ends the ongoing game** in the server |
| `/u-alerts` | `on/off/view` | Turns your **alerts** on or off | `/u.alerts on` |
| `/u-kick` | @user mention | **Kicks** a player from a game | `/u-kick @VTiS` |
| `/u-stats` | (@user mention) | Gives you a user's **stats** only from the current Discord server. Gives you your stats if no user is mentioned | `/u-stats @VTiS` |
| `/u-gstats` | (@user mention) | Gives you a user's **global stats** only from all Discord servers. Gives you your global stats if no user is mentioned | `/u-gstats @VTiS`|
| `/u-lb` | None | Gives you a **leaderboard** only from the current Discord server |
| `/u-glb` | None | Gives you a **global leaderboard** from all Discord servers |
| `/u-settings` | Variable arguments | Change the **settings** for each commands `commands`, modify the default game settings `defaultgamesettings/dgs`, or reset the bot `reset` | `/u-settings commands allowalerts off`, `/u-settings dgs Flip on`, `/u-settings dgs StartingCards 15`, `/u-settings reset` |

# <a name="rule">Game Rules📃</a>
## <img align="right" src="https://user-images.githubusercontent.com/73805050/130345109-413d6558-77d6-42cf-962c-1cb9eaad750e.png" width="100" height="69.2"> Original UNO!
### Setup
Each player is dealt 7 cards. A top card is randomly chosen to let the game begin. The top card cannot be a Wild or a Wild Draw 4.
### Gameplay
Match the top card on the DISCARD pile either by number, color or word.

For example, if the card is a Green 7, you must play a Green card or any color 7. Or, you may play any Wild card or a Wild Draw 4 card. If you don't have anything that matches, you must pick a card from the DRAW pile and lose your turn by entering `draw` in your uno-channel. Each player can only play one card in their turn.

Play a card by entering `<color><value>` in your uno-channel. For example, if you wish to play a Green 7, enter `green7` in your uno-channel.
Play a Wild Draw 4 by entering `<color>+4`.

You may choose not to play a playable card from your hand. If so, you must draw a card.

You win by getting rid of all your cards first. The last card can be a special card.
### Special 7-0 Rule
When the 7-0 Rule is applied, a player must switch hands with another designated player when they play a 7 (by entering `<color>7 <username>`, and everyone in the game must switch hands in the direction of play when a 0 is played.\
For example, if the order of play is A -> B -> C -> A …, and if Player A plays a 0, then A must give their hand to B and B gives to C, and then C to A.
## <img align="right" src="https://user-images.githubusercontent.com/73805050/130345601-ec333b6a-2fb0-472b-85dc-e1d53b845269.png" width="94.6656" height="69.2"> UNO FLIP!
The fundamental rules of UNO FLIP! is similar to that of the original UNO!, but a double-sided deck and hence new special cards are introduced in this game mode.
### Setup
Each player is dealt 7 cards. You hold the cards with the Light Side facing yourself and the Dark Side facing your opponents.\
A top card with Light Side up is randomly chosen to let the game begin. The top card cannot be a Wild or a Wild Draw 2.
### Gameplay
The gameplay is basically the same as the original UNO!.

There are 4 new colors in the Dark Side, Pink(`p`), Teal(`t`), Orange(`o`), Purple(`z`). *(Probably should be "pp" instead of "z" lol)*

If you play a Flip card, everything flips from the Light Side to the Dark Side (if it's a Light Side Flip) or from the Dark Side to the Light Side (if it's a Dark Side Flip).\
The Discard Pile is flipped first, then the Draw Pile, and finally everyone's hand must flip to the other side.

Play a Skip Everyone card by entering `<color>skip`, just like what you'd enter for a normal skip.\
Play a Wild Draw Color Card by entering `<color>+color`.

# Similar Project📑
* [UNOBot by Exium](https://top.gg/bot/565305035592957954): The inspiration of this bot. It works in almost the exact same way as this bot does. However, it only features the original game of UNO!. It's a public bot and the frequent lags, bugs, and downtime are the crux of the matter. It's what pushed me to create this bot.
