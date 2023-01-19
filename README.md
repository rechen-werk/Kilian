# Kilian

Kilian is a Discord Bot that manages channels and roles. 
He was forged to meet the requirements for our BigBrains Server, but he likes to join and manage other servers aswell.
His main purpose is to manage invisible roles on Discord.

Why invisible roles you ask? - Great question.

On our server we have a lot of roles to decide which user should see which channel. 
Now if a user is visiting 15 courses they have these 15 roles + some vanity roles.
But no one wants to see this wall of roles when clicking on a user so we decided to hide them.
Another advantage of letting Kilian hide the roles is that he automatically manages the roles of all users which want to see the uni-channels and we do not have to move a finger anymore. 

## Usage

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

The `studid`-Command returns the student id of the user if they provided it with their link.

## Implementation Details

## Requirements

Requirements are listed and can be installed with `pip install -r requirements.txt`