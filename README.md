# UNOBot <img align="right" src="https://user-images.githubusercontent.com/73805050/130341782-78d30da7-0313-44f5-889c-06ab7eb8de9a.png">
Inspired by [Exium's work](https://top.gg/bot/565305035592957954), this is a Discord bot that incorporates the popular card game, **UNO**, into your Discord server.
It allows Discord users to play the game completely within text channels. Challenge your friends and climb the leaderboard!

<p align="center">
    <a href="https://discord.com/api/oauth2/authorize?client_id=846948720159490078&permissions=268561488&scope=bot%20applications.commands" alt="Invite me!">
        <img alt="Invite Link" src="https://img.shields.io/static/v1?label=bot&message=invite%20me&color=purple">
    </a>
</p>

# Features💡
* Play UNO! with your friends completely within text channels on Discord!
* Various optional game rules, including **StackCards** and **7-0**
* Three fun game modes - Original **UNO!**, **UNO FLIP!**, and **ONO 99**
* **Play with bots** (disables point calculation)
* Local and global **leaderboards**
* Check and show off your **stats**!

* Highly customizable player options, game and command settings

# Usage and Commands⚙️
Type the following `/u-` command to start a game of UNO.
```
/u-sg
# Starts a game, allowing users to join the game by pressing a button.
```
The bot will send a message to the your server. Users can press the Join button to join the game in 30 seconds.\
After 30 seconds, if there are enough (>1) players, a text channel for every player will be created and players can use their channels to play their hands.\
<br/>
If you want to view command usage, read an in-depth guide on using the bot, or read the rules of UNO, type `/u-help` in your Discord server.\
<br/>
**Please DO NOT spam the bot.**
## Command Usage
The UNOBot uses the prefix `/u-` for commands.
| Command | Arguments | Description | Example |
| ------- | --------- | ----------- | ------- |
| `/u-help` | None | Prints **help info** |
|`/u-cmds` | (command) | Shows you how to use UNOBot's commands. | `/u-cmds sg` |
| `/u-rules` | None | [UNO Rules](#rule) |
| `/u-guide`| (`start/play/commands/settings/options`) | Gives you a **guide** on using UNOBot | `/u-guide start` |
| `/u-sg` | (@user mentions), (game settings) | **Starts a game** in the server | `/u-sg @VTiS @Dong Flip`| 
| `/u-eg` | None | **Ends the ongoing game** in the server |
| `/u-kick` | @user mention | **Kicks** a player from a game | `/u-kick @VTiS` |
| `/u-stats` | (@user mention) | Gives you a user's **stats** only in the current Discord server. Gives you yours if no user is mentioned | `/u-stats @VTiS` |
| `/u-gstats` | (@user mention) | Gives you a user's **global stats**. Gives you yours if no user is mentioned | `/u-gstats @VTiS`|
| `/u-lb` | None | Gives you a **leaderboard** only from the current Discord server |
| `/u-glb` | None | Gives you a **global leaderboard** from all Discord servers |
| `/u-settings` | Variable | Change the **settings** for each commands `commands`, modify the default game settings `defaultgamesettings/dgs`, or reset the bot `reset` | `/u-settings commands allowalerts off`, `/u-settings dgs Flip on`, `/u-settings dgs StartingCards 15`, `/u-settings reset` |

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
#### Winning
When a player no longer has any cards and the game ends, they receive points. All opponents’ cards are given to the winner and points are counted. This also applies even if the last card is an Action card, such as a Draw Two or a Wild Draw 4 – The next player must draw the required cards which will then be tallied up.
#### Scoring
The scoring for the cards is as follows:
| Card Type | Score |
| --------- | ----- |
| Numbered cards (0-9) | Face value |
| Draw 2/Skip/Reverse | 20 pts |
| Wild/Wild Draw 4 | 50 pts |
### Special 7-0 Rule
When the 7-0 Rule is applied, a player must switch hands with another designated player when they play a 7, and everyone in the game must switch hands in the direction of play whenever a 0 is played.\
For example, if the order of play is A -> B -> C -> A …, and if Player A plays a 0, then A must give their hand to B and B gives to C, and then C to A.

## <img align="right" src="https://user-images.githubusercontent.com/73805050/130345601-ec333b6a-2fb0-472b-85dc-e1d53b845269.png" width="94.6656" height="69.2"> UNO FLIP!
The fundamental rules of UNO FLIP! is similar to that of the original UNO!, but a double-sided deck and hence new special cards are introduced in this game mode.
### Setup
Each player is dealt 7 cards. You hold the cards with the Light Side facing yourself and the Dark Side facing your opponents.\
A top card with Light Side up is randomly chosen to let the game begin. The top card cannot be a Wild or a Wild Draw 2.
### Gameplay
The gameplay is basically the same as the original UNO!.

However, there are 4 new colors in the Dark Side, Pink(`p`), Teal(`t`), Orange(`o`), Purple(`z`). *(Probably should be "pp" instead of "z" lol)*

If you play a Flip card, everything flips from the Light Side to the Dark Side (if it's a Light Side Flip) or from the Dark Side to the Light Side (if it's a Dark Side Flip).\
The Discard Pile is flipped first, then the Draw Pile, and finally everyone's hand must flip to the other side.

Play a Skip Everyone card by entering `<color>skip`, just like what you'd enter to play a normal skip.\
Play a Wild Draw Color Card by entering `<color>+color`.
#### Scoring
The scoring for the cards is as follows:
| Card Type | Score |
| --------- | ----- |
| Numbered cards (1-9) | Face value |
| Draw 1 | 10 pts |
| Draw 5/Skip/Reverse/Flip | 20 pts |
| Skip Everyone | 30 pts |
| Wild | 40 pts |
| Wild Draw 2 | 50 pts |
| Wild Draw Color | 60 pts |

## <img align="right" src="https://user-images.githubusercontent.com/73805050/177706776-05663748-1c7e-4570-9e78-e160a8032752.png" width="113.2487" height="69.2"> ONO 99
### Setup
Each player is dealt 4 cards. The number of cards each player has never changes during a game.
### Gameplay
You play cards from your hand onto the Discard Pile. Most cards have numbers on them, and as you add them to the pile the total number of the pile increases. A 3 placed onto a 7 puts the pile at 10. Add a 6 to the pile and now it's 16 and so on. As the total number of the pile builds and builds, you must keep it **UNDER 99**. If you are unable to play a card without making the total hit 99 or above, you are out of the game.\
Last man standing wins.

Since colors are unimportant, you want to enter only the value of the card every time you play.
#### Scoring
The scoring for the cards is as follows:
| Card Type | Score |
| --------- | ----- |
| Numbered cards (0-10) | Face value |
| -10/Reverse/Play 2 | 20 pts |
| ONO 99 | 99 pts |

# Troubleshooting🛠️
### There are more than one UNO games happening in my server.
Remove the extra games by deleting the text channels. If UNOBot gets stuck afterwards, end the remaining game by entering `/u-eg`.\
You should always make sure there is only **one** UNO category and maximum **one** ongoing game in a server at all times.

### UNOBot said it was my turn but not when I actually tried to play.
Simply ignore the stupid bot and try again.

### I only want people to use UNOBot's commands in a specific text channel.
Deny UNOBot the permission to read other channels. **NEVER** restrict UNOBot's command usage in your Discord server's Integrations settings page, otherwise people cannot use UNOBot's commands in their UNO channels (because a player's UNO channel only exists during a game).

### UNOBot is stuck and unresponsive!!! What do I do???
* Forcefully end the ongoing game (if there is one) using `/u-eg`; or
* Manually delete the UNO channels (and perhaps category)

before starting a new game.\
If that does not work, try resetting UNOBot by entering `/u-settings reset` and `CONFIRM` afterwards.

# Inspiration✨
* [UNOBot by Exium](https://top.gg/bot/565305035592957954): The inspiration of this bot. It works in almost the exact same way as this bot does. However, it only features the original game of UNO!. It suffers from frequent lags, bugs, and downtime, and thus motivated me to develop this bot.
