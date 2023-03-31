"""
    File name: kilian.py
    Author: Adrian Vinojcic, Tobias Pilz
    This part is responsible for everything related to the discord api.
"""

import argparse
import interactions
import kusss as uni
from database import Database, Roles, StudentCourse, Archive, Archivesniffer
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token", type=str, required=False, dest='token',
        help="Provide the Discord Bot Token as string.")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    with open("config.json", 'r') as f:
        data = json.load(f)
        bot_token = args.token if args.token is not None else data['token']
        dads = data['dads']

    database = Database()

    bot = interactions.Client(token=bot_token, intents=interactions.Intents.ALL)


    @bot.command()
    @interactions.option(description="Provide the calendar link from KUSSS here.")
    @interactions.option(description="Optionally provide your matriculation number here.")
    async def kusss(ctx: interactions.CommandContext, link: str, studentnumber: str = None):
        """Take advantage of the features provided by Kilian™."""
        await ctx.defer(ephemeral=True)

        try:
            guild_id = str(ctx.guild_id)
            current_semester = uni.current_semester()
            student = uni.student(str(ctx.author.id), link, studentnumber)

            if database.is_kusss(str(ctx.author.id)):
                await ctx.send(f"Your courses will be updated {ctx.author.name}!")
            else:
                await ctx.send(f"Welcome on board {ctx.author.name}!")

            database.insert(student)

            await database.lock.acquire()

            guild_course_names = database.get_server_courses(guild_id, current_semester)
            new_courses = database.get_added_courses(student.discord_id, current_semester)
            missing_courses_by_name = dict()
            for course in new_courses:
                if course.lva_name in guild_course_names:
                    continue
                if course.lva_name not in missing_courses_by_name.keys() or database.is_archived(guild_id,
                                                                                                 course.lva_name):
                    missing_courses_by_name[course.lva_name] = set()
                missing_courses_by_name[course.lva_name].add(course)

            if database.has_category(guild_id):
                category = database.get_category(guild_id)
            else:
                everyone_id = next(filter(lambda x: x.name == "@everyone", await ctx.guild.get_all_roles())).id
                category = await ctx.guild.create_channel(
                    name=uni.current_semester(), type=interactions.ChannelType.GUILD_CATEGORY,
                    permission_overwrites=[
                        interactions.Overwrite(
                            id=str(everyone_id),
                            type=0,
                            deny=interactions.Permissions.VIEW_CHANNEL,
                            allow=interactions.Permissions.MENTION_EVERYONE |
                                  interactions.Permissions.USE_APPLICATION_COMMANDS
                        )])
                archive_cat = await ctx.guild.create_channel(
                    name="Archive", type=interactions.ChannelType.GUILD_CATEGORY,
                    permission_overwrites=[
                        interactions.Overwrite(
                            id=str(everyone_id),
                            type=0,
                            deny=interactions.Permissions.VIEW_CHANNEL |
                                 interactions.Permissions.SEND_MESSAGES,
                            allow=interactions.Permissions.MENTION_EVERYONE |
                                  interactions.Permissions.USE_APPLICATION_COMMANDS
                        )])
                database.set_category(guild_id, str(category.id), str(archive_cat.id))

            added_roles = Roles()
            for course_name in missing_courses_by_name:
                role = await ctx.guild.create_role(course_name[:95] if len(course_name) > 95 else course_name)

                channel = await ctx.guild.create_channel(
                    name=(course_name[:95] if len(course_name) > 95 else course_name),
                    type=interactions.ChannelType.GUILD_TEXT,
                    parent_id=category)
                added_roles.add((course_name, uni.current_semester(), guild_id, str(role.id), str(channel.id)))

            database.insert(added_roles)

            database.lock.release()

            all_channels = await ctx.guild.get_all_channels()
            new_user_channels = set[interactions.Channel]()
            for course in new_courses:
                channel_id = database.get_channel(guild_id, course.lva_name, course.semester)
                for channel in all_channels:
                    if channel.id == channel_id:
                        new_user_channels.add(channel)
                        await channel.modify(parent_id=database.get_category(guild_id))
                        if database.is_archived(guild_id, course.lva_name):
                            database.delete_archive(guild_id, str(channel.id))
                        break

            from interactions import Permissions as p
            new_rule = interactions.Overwrite(
                id=str(ctx.author.id),
                type=1,
                allow=p.VIEW_CHANNEL | p.READ_MESSAGE_HISTORY)
            for channel in new_user_channels:
                await channel.modify(permission_overwrites=channel.permission_overwrites + [new_rule])

        except uni.InvalidURLException as ex:
            await ctx.send(ex.message, ephemeral=True)


    @bot.command()
    async def unkusss(ctx: interactions.CommandContext):
        """Unsubscribe from the awesome features provided by Kilian™."""
        await ctx.defer(ephemeral=True)

        if not database.is_kusss(str(ctx.author.id)):
            await ctx.send(f"Seems that your are not registered {ctx.author.name}! You can join the club anytime with "
                           f"`/kusss`!")
            return

        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild_id)
        courses = database.get_added_courses(user_id, uni.current_semester())
        database.delete_student(user_id)

        courses = {database.get_role_and_channel(guild_id, course.lva_name, course.semester) for course in courses}

        all_guild_channels = await ctx.guild.get_all_channels()
        channel_ids = set(map(lambda rolechannel: rolechannel[1], courses))
        all_user_channels = set(filter(lambda c: str(c.id) in channel_ids, all_guild_channels))

        for channel in all_user_channels:
            permission_overwrites = channel.permission_overwrites
            permission_overwrites = list(filter(lambda po: po.id != ctx.author.id, permission_overwrites))
            await channel.modify(permission_overwrites=permission_overwrites)
            await archive(ctx.guild, channel)

        await ctx.send("A pity to see you leave " + ctx.author.name + ". You can join the club anytime with "
                                                                      "`/kusss`!")


    @bot.command()
    @interactions.option(description="Role you want to ping.")
    @interactions.option(description="Message content goes here.")
    async def ping(ctx: interactions.CommandContext, role: interactions.Role, content: str = ""):
        """Ping everyone partaking that subject."""
        await ctx.defer(ephemeral=True)
        role_id = str(role.id)
        guild_id = str(ctx.guild_id)

        if database.is_managed_role(guild_id, role_id):
            users_with_anonymous_role = database.get_role_members(guild_id, role_id)
        else:
            await ctx.send("This is not a uni-role, just ping it directly!")
            return

        ping_string = ""
        for user_id in users_with_anonymous_role:
            user = (await ctx.guild.get_member(int(user_id))).user
            ping_string += user.mention

        if len(ping_string) > 0:
            await ctx.send(ping_string + "\n" + content)
        else:
            await ctx.send("Nobody to ping", ephemeral=True)

        # POSSIBLE ERROR: too many users, so that not all pings fit in one message
        # POSSIBLE SOLUTION TO ERROR: multiple messages


    @bot.command()
    @interactions.option(description="The user you want the student id of.")
    async def studid(ctx: interactions.CommandContext, member: interactions.Member):
        """Get student id of the specified user."""
        await ctx.defer(ephemeral=True)
        if not database.get_matr_nr(str(member.id)):
            await ctx.send(f"{member.name} hasn't registered a student id in Kilian", ephemeral=True)
            return
        await ctx.send(database.get_matr_nr(str(member.id)), ephemeral=True)


    @bot.command()
    @interactions.option(description="Course chat you want to join.")
    async def join(ctx: interactions.CommandContext, course: interactions.Role):
        """Join a course chat."""
        await ctx.defer(ephemeral=True)
        role_id = str(course.id)
        guild_id = str(ctx.guild_id)

        if not database.is_kusss(str(ctx.author.id)):
            await ctx.send("You have to be subscribed to Kilian services to use Kilian features.", ephemeral=True)
            return

        if not database.is_managed_role(guild_id, role_id):
            await ctx.send("This course does not exist!", ephemeral=True)
            return

        discord_id = str(ctx.author.id)
        semester = uni.current_semester()
        lva_name = database.get_lva_name_by_role_id(semester, guild_id, role_id)
        lva_nr = database.get_lva_nr(lva_name, semester)

        if database.student_has_course(discord_id, semester, lva_name):
            await ctx.send("Already joined the course chat.", ephemeral=True)
            return

        student = uni.student(discord_id, database.get_link(discord_id))
        student_lva_nrs = set(map(lambda c: c.lva_nr, student.courses))
        course_lva_nrs = database.get_lva_nrs(lva_name, semester)

        intersection = student_lva_nrs & course_lva_nrs

        if len(intersection) > 0:
            for lva_nr_runner in intersection:
                database.insert(StudentCourse(discord_id, semester, lva_nr_runner, True))
        else:
            database.insert(StudentCourse(discord_id, semester, lva_nr, False))

        if database.is_archived(guild_id, lva_name):
            channel_id = database.get_archived(guild_id, lva_name)
            database.delete_archive(guild_id, channel_id)
        else:
            channel_id = database.get_channel_id(guild_id, role_id)

        from interactions import Permissions as p
        new_rule = interactions.Overwrite(
            id=str(ctx.author.id),
            type=1,
            allow=p.VIEW_CHANNEL | p.READ_MESSAGE_HISTORY)
        channel = await interactions.get(bot, interactions.Channel, object_id=channel_id)
        await channel.modify(permission_overwrites=channel.permission_overwrites + [new_rule],
                             parent_id=database.get_category(guild_id))

        await ctx.send(f"Welcome to {lva_name}, {ctx.author.name}.", ephemeral=True)


    @bot.command()
    async def leave(ctx: interactions.CommandContext):
        """Leave this channel."""
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild_id)
        discord_id = str(ctx.author.id)
        semester = uni.current_semester()
        channel_id = str(ctx.channel_id)

        if not database.is_managed_channel(channel_id):
            await ctx.send("Cannot leave non-uni channels.", ephemeral=True)
            return

        lva_name = database.get_lva_name_by_channel_id(semester, guild_id, channel_id)
        lva_nrs = database.get_lva_nrs(lva_name, semester)

        await ctx.send(f"{ctx.author.name} left the channel.", ephemeral=True)

        channel = ctx.channel
        permission_overwrites = channel.permission_overwrites
        permission_overwrites = list(filter(lambda po: po.id != ctx.author.id, permission_overwrites))
        await channel.modify(permission_overwrites=permission_overwrites)

        for lva_nr in lva_nrs:
            database.delete_student_role(discord_id, lva_nr, semester)

        await archive(ctx.guild, channel)


    @bot.command()
    async def toggleping(ctx: interactions.CommandContext):
        await ctx.defer(ephemeral=True)
        discord_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        semester = uni.current_semester()
        channel_id = str(ctx.channel.id)

        if not database.is_managed_channel(channel_id):
            await ctx.send("Cannot disable pings non-uni channels.", ephemeral=True)
            return

        lva_name = database.get_lva_name_by_channel_id(semester, guild_id, channel_id)
        lva_nrs = database.get_lva_nrs(lva_name, semester)

        change = False
        now_active = False
        for lva_nr in lva_nrs:
            if database.has_course(discord_id, lva_nr, semester):
                if database.is_active(discord_id, lva_nr, semester):
                    database.toggle_active(False, discord_id, lva_nr, semester)
                    change = True
                    now_active = False
                else:
                    database.toggle_active(True, discord_id, lva_nr, semester)
                    change = True
                    now_active = True

        if change:
            if now_active:
                await ctx.send("You will now be pinged.", ephemeral=True)
            else:
                await ctx.send("You will no longer be pinged.", ephemeral=True)


    async def archive(guild: interactions.Guild, channel: interactions.Channel):
        """Method for checking if a channel should be archived or deleted"""
        guild_id = str(guild.id)
        semester = uni.current_semester()
        channel_id = str(channel.id)
        lva_name = database.get_lva_name_by_channel_id(semester, guild_id, channel_id)
        lva_nr = database.get_lva_nr(lva_name, semester)
        role_id = database.get_role_id_by_channel_id(channel_id)
        role = await guild.get_role(int(role_id))

        if channel.last_message_id is None and not database.course_has_members(lva_nr):
            database.delete_role(guild_id, role_id)
            await role.delete(guild.id)
            await channel.delete()
        elif channel.last_message_id is not None and not database.course_has_members(lva_nr):
            database.insert(Archive(guild_id, channel_id, lva_name))
            category_id = database.get_archive(guild_id)
            await channel.modify(parent_id=int(category_id))


    @bot.command()
    async def sleep(ctx: interactions.CommandContext):
        """Make Kilian go nighty night."""
        await ctx.defer(ephemeral=True)
        if dads.count(ctx.author.id):
            await ctx.send("Good night, daddy!", ephemeral=True)
            await bot._stop()
        else:
            await ctx.send("You are not my daddy!", ephemeral=True)


    @bot.command()
    async def op(ctx: interactions.CommandContext):
        """Kilian will grant you the rank of "op".
        It can be revoked by using /deop"""
        await ctx.defer(ephemeral=True)
        user = ctx.author

        if not dads.count(ctx.author.id):
            await ctx.send("You are not my daddy!", ephemeral=True)
            return

        # Check if a role with a similar name already exists
        role = None
        for r in ctx.guild.roles:
            if str(r.name).lower() == "op":
                role = r
                break

        if role is None:
            from interactions import Permissions as p
            role = await ctx.guild.create_role(name="op", permissions=p.ADMINISTRATOR)

        # Give the user the admin role
        await user.add_role(role)
        await ctx.send("You are now op!", ephemeral=True)


    @bot.command()
    async def deop(ctx: interactions.CommandContext):
        """Kilian will revoke your "op" rank."""
        await ctx.defer(ephemeral=True)
        user = ctx.author

        if not dads.count(ctx.author.id):
            await ctx.send("You are not my daddy!", ephemeral=True)
            return

        # Check if the user has a role with a similar name
        role = None
        for id in user.roles:
            r = await ctx.guild.get_role(id)
            if str(r.name).lower() == "op":
                role = r
                break

        if role is None:
            await ctx.send("You are not op!", ephemeral=True)
            return

        # Give the user the admin role
        await user.remove_role(role)
        await ctx.send("You are no longer op!", ephemeral=True)

    @bot.command()
    async def archivesniffer(ctx: interactions.CommandContext):
        """Check out archived channels."""
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild.id)
        discord_id = str(ctx.author.id)

        channel_ids = database.get_all_archived()
        archived_channels = list()

#        Doesn't work?
#        for channel_id in channel_ids:
#            archived_channels.append(interactions.ChannelRequest.get_channel(int(channel_id)))

        if database.is_archivesniffer(guild_id, discord_id):
            database.delete_archivesniffer(guild_id, discord_id)
        else:
            database.insert(Archivesniffer(guild_id, discord_id))


    # All new commands which are below help won't be listed inside the help choices
    @bot.command()
    @interactions.option(type=interactions.OptionType.STRING,
                         description="Subcategory of Help",
                         required=False,
                         choices=[interactions.Choice(name=com.name, value="/" + com.name) for com in bot._commands]
                         )
    async def help(ctx: interactions.CommandContext, subcategory: str = None):
        """Commands supported by Kilian"""
        embeded = interactions.Embed(title="Help Menu", color=0x701473)
        help_dict = {
            "/kusss": {"params": {"<link>": "link of your KUSSS calender\nis obtained via KUSSS"},
                       "optional_params": {
                           "[student-id]": "your matrikelnumber\nis optional and used for other commands "},
                       "details": "You can get your link from:\nhttps://www.kusss.jku.at/kusss/ical-multi-form-sz.action\nClick \"Create\" if the link is not there yet.",
                       "description": "Subscribe to Kilian services.", "inline": False},
            "/unkusss": {"params": {}, "optional_params": {},
                         "details": "",
                         "description": "Ping a course chat", "inline": False},
            "/ping": {"params": {"<@ManagedRole>": "the roles of course which should get pinged"},
                      "optional_params": {"[content]": "the message attached to the ping"},
                      "details": "",
                      "description": "Ping a course chat.", "inline": True},
            "/join": {"params": {"<channel>": "The role with the same name as the course channel you want to join "},
                      "optional_params": {},
                      "details": "",
                      "description": "Join another course chat managed by Kilian", "inline": True},
            "/leave": {"params": {}, "optional_params": {},
                       "details": "",
                       "description": "Leave the channel managed by Kilian", "inline": True},
            "/toggleping": {"params": {}, "optional_params": {},
                            "details": "Enable or disable pings for a channel.\nPings are enabled default if you are "
                                       "registered for the course",
                            "description": "Enable or disable pings for a channel.", "inline": True},
            "/studid": {"params": {"<@User>": "The user you want the studid of"}, "optional_params": {},
                        "details": "Only possible if the student has entered his id on /kusss\nYou can still update "
                                   "your studid with /kusss",
                        "description": "Get the student id of other users.", "inline": True},
            "/archivesniffer": {"params": {}, "optional_params": {},
                                "details": "",
                                "description": "Gain permissions for viewing archived channels", "inline": True},
        }
        if not subcategory:
            for command in help_dict.keys():
                params_keys = help_dict[command]['params'].keys()
                optional_params_keys = help_dict[command]['optional_params'].keys()
                params_text = f"*{' '.join(params_keys)}*" if len(params_keys) > 0 else ""
                optional_params_text = f"*{' '.join(optional_params_keys)}*" if len(optional_params_keys) > 0 else ""

                embeded.add_field(f"**{command} {params_text} {optional_params_text} **",
                                  help_dict[command]['description'],
                                  inline=help_dict[command]['inline'])
        else:
            if list(help_dict.keys()).count(subcategory) == 0:
                await ctx.send(
                    content=f"We are sorry the help for the command {subcategory} isn't implemented yet!\nFor further information contact a developer!",
                    ephemeral=True)
                return

            embeded.title = embeded.title + " - " + subcategory
            params_keys = help_dict[subcategory]['params'].keys()
            optional_params_keys = help_dict[subcategory]['optional_params'].keys()
            params_text = f"*{' '.join(params_keys)}*" if len(params_keys) > 0 else ""
            optional_params_text = f"*{' '.join(optional_params_keys)}*" if len(optional_params_keys) > 0 else ""
            embeded.description = f"**{subcategory} {params_text} {optional_params_text} **"
            for param in params_keys:
                embeded.add_field(f"*{param}*", f"{help_dict[subcategory]['params'][param]}", inline=True)
            for param in optional_params_keys:
                embeded.add_field(f"*{param}*", f"{help_dict[subcategory]['optional_params'][param]}", inline=True)
            if help_dict[subcategory]['details'] != "":
                embeded.add_field("Details", help_dict[subcategory]['details'])

        await ctx.send(embeds=embeded, ephemeral=True)


    @bot.event()
    async def on_message_create(message: interactions.Message):
        """
        Checks if a message contains a managed mention
        If yes: pings all users by replying to the message sent
        If no: returns
        """

        if message.author.id == bot.me.id:
            return

        guild_id = message.guild_id
        if guild_id is None:
            return
        guild = await message.get_guild()
        guild_id = str(guild_id)
        mentioned_roles = [role_id for role_id in message.mention_roles if database.is_managed_role(guild_id, role_id)]
        if len(mentioned_roles) == 0:
            return

        users_with_anonymous_role = set()
        for role_id in mentioned_roles:
            users_with_anonymous_role = users_with_anonymous_role | database.get_role_members(guild_id, role_id)

        ping_string = ""
        for user_id in users_with_anonymous_role:
            user = (await guild.get_member(int(user_id))).user
            ping_string += user.mention

        if len(ping_string) > 0:
            await message.reply(ping_string)


    @bot.event()
    async def on_start():
        print("Good morning daddy!")


    bot.start()
