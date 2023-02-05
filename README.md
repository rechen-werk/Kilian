![bot_banner.png](/img/bot_banner.png)
# Kilian

Kilian is a Discord Bot that manages channels and roles. 
He was forged to meet the requirements for our **BigBrains** Server, but he likes to join and manage other servers aswell.
His main purpose is to manage invisible roles on Discord.

Why invisible roles you ask? - Great question.

On our server we have a lot of roles to decide which user should see which channel. 
Now if a user is visiting 15 courses they have these 15 roles + some vanity roles.
But no one wants to see this wall of roles when clicking on a user so we decided to hide them.
Another advantage of letting Kilian hide the roles is that he automatically manages the roles of all users which want to see the uni-channels and we do not have to move a finger anymore. 

## Usage
### Start

Use `python kilian.py` to start the bot. 
At every startup, Kilian will pull all courses of the current semester from KUSSS. This can take a few moments.
When everything is done, Kilian will greet you properly in the commandline.

### /kusss

The command `/kusss <link> [student-id]` subscribes to the Kilian™ services.
Parameter `link` is the link for the calender file in [KUSSS](https://www.kusss.jku.at/kusss).
The proper link can be obtained from [here](https://www.kusss.jku.at/kusss/ical-multi-form-sz.action) by clicking Create and copying the link.
Optional parameter `student-id` is the users student id and may be provided so others can check it if they need it for a group project for example.

### /unkusss

`/unkusss` unsubscribes you from all Kilian™ services and removes all related collected data.

### /ping | @ManagedRole

`/ping <@ManagedRole> [Content]` lets you ping all users which attend the course, just like @ManagedRole does.
The Advantage of pinging such a managed role is, that these Managed roles are not visible in Discord at all.
Further information on that can be found in the Implementation Details.

### /studid

The `studid <@User>`-Command returns the student id of the user if they provided it with their link.

### /sleep

`/sleep` shuts Kilian down properly. 
This command can only be run by Kilians dads, so make sure to be one of them!


## Implementation Details

## Requirements

Requirements are listed and can be installed with `pip install -r requirements.txt`

Get a working discord bot: 
  * follow [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) to get your bot 
  * set all "Priviledged Gateway Intents" to true
  * add the bot to your server with "Administrator" permissions
  * reset and copy your bot token!

Fill out `config.json`
  * paste your bot-token into the corresponding field
  * paste your discord-id as string into the "dads" list (to turn Kilian off properly)
  
## Known issues and errors

### AuditLog error messages in the command line

Don't worry about those error messages, they are from the [`interactions.py`](https://github.com/interactions-py/interactions.py) package and to us, these are completely normal.

### Scalability issues
  * if two or more persons use Kilians `/kusss`-Command at the same time, courses are generate more than once.
  * if 250 roles are generated in less than 48 hours, discord will block your bot for 24 hours. ([source](https://support.discord.com/hc/en-us/community/posts/360050533812-Extreme-rate-limits-on-the-role-create-endpoint))

## Future ideas
  * use more bots at the same time as "creating-slaves" to get rid of discord blocking the bot.
  * deleting unused roles and channels on `/unkusss`
  * add an "Archivesniffer"-Role to give people permissions to view older channels
  * add a "Veteran"-Role to give people permissions to get into channels and help others
  * `/studygroup`: create a private voicechannel for - hmm.. well - studygroups
  * `/hiderole <@Role>`: hide a already existent role and provide Kilians standard features for it
  * `/showrole <@Role>`: reverse `/hiderole`
