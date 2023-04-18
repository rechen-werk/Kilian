"""
    File name: kilian.py
    Author: Adrian Vinojcic, Tobias Pilz
    This part is responsible for everything related to the discord api.
"""

import argparse
from datetime import datetime, timedelta

import interactions
import kusss as uni
from database import Database, Roles, StudentCourse
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token", type=str, required=False, dest='token',
        help="Provide the Discord Bot Token as string.")
    return parser.parse_args()


async def get_category(guild: interactions.Guild):
    guild_id = str(guild.id)
    if database.has_category(guild_id):
        category = database.get_category(guild_id)
    else:
        everyone_id = next(filter(lambda x: x.name == "@everyone", await guild.get_all_roles())).id
        category = await guild.create_channel(
            name=uni.current_semester(), type=interactions.ChannelType.GUILD_CATEGORY,
            permission_overwrites=[
                interactions.Overwrite(
                    id=str(everyone_id),
                    type=0,
                    deny=interactions.Permissions.VIEW_CHANNEL,
                    allow=interactions.Permissions.MENTION_EVERYONE |
                          interactions.Permissions.USE_APPLICATION_COMMANDS
                )])
        database.set_cagegory(guild_id, str(category.id))

    return category

def purge_inactive_voice_channels(guild: interactions.Guild, database: Database):
    all_studygroups = database.all_studygroups()
    all_studygroups

    pass


if __name__ == '__main__':
    __invite_number__ = 0
    args = parse_args()

    with open("config.json", 'r') as f:
        data = json.load(f)
        bot_token = args.token if args.token is not None else data['token']
        dads = data['dads']

    database = Database()

    bot = interactions.Client(token=bot_token, intents=interactions.Intents.ALL)

    purge_inactive_voice_channels(None, database)

    @bot.command()
    @interactions.option(description="Provide the calendar link from KUSSS here.")
    @interactions.option(description="Optionally provide your matriculation number here.")
    async def kusss(ctx: interactions.CommandContext, link: str, studentnumber: str = None):
        """Take advantage of the features provided by Kilian™."""
        try:
            guild_id = str(ctx.guild_id)
            current_semester = uni.current_semester()
            student = uni.student(str(ctx.author.id), link, studentnumber)
            database.insert(student)

            await ctx.send("Welcome on board " + ctx.author.name + "!")

            await database.lock.acquire()

            guild_course_names = database.get_server_courses(guild_id, current_semester)
            new_courses = database.get_added_courses(student.discord_id, current_semester)
            missing_courses_by_name = dict()
            for course in new_courses:
                if course.lva_name in guild_course_names:
                    continue
                if course.lva_name not in missing_courses_by_name.keys():
                    missing_courses_by_name[course.lva_name] = set()
                missing_courses_by_name[course.lva_name].add(course)

            category = await get_category(ctx.guild)

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
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild_id)

        await ctx.send("A pity to see you leave " + ctx.author.name + ". You can join the club anytime with `/kusss`!")
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


    @bot.command()
    @interactions.option(description="Role you want to ping.")
    @interactions.option(description="Message content goes here.")
    async def ping(ctx: interactions.CommandContext, role: interactions.Role, content: str = ""):
        """Ping everyone partaking that subject."""
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
        await ctx.send(database.get_matr_nr(str(member.id)), ephemeral=True)


    @bot.command()
    @interactions.option(description="Course chat you want to join.")
    async def join(ctx: interactions.CommandContext, course: interactions.Role):
        """Join a course chat."""
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

        channel_id = database.get_channel_id(guild_id, role_id)

        from interactions import Permissions as p
        new_rule = interactions.Overwrite(
            id=str(ctx.author.id),
            type=1,
            allow=p.VIEW_CHANNEL | p.READ_MESSAGE_HISTORY)
        channel = await interactions.get(bot, interactions.Channel, object_id=channel_id)
        await channel.modify(permission_overwrites=channel.permission_overwrites + [new_rule])

        await ctx.send(f"Welcome to {lva_name}, {ctx.author.name}.", ephemeral=True)


    @bot.command()
    async def leave(ctx: interactions.CommandContext):
        """Leave this channel."""
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


    @bot.command()
    async def toggleping(ctx: interactions.CommandContext):
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

    @bot.command()
    async def help(ctx: interactions.CommandContext):
        """Commands supported by Kilian"""
        commands = "**/kusss *<link>* *[student-id]* ** - Subscribe to Kilian services. \n" \
                   "\t\t*<link>* is obtained via KUSSS, *[student-id]* is optional and used for other commands \n" \
                   "\t\tYou can get your link from https://www.kusss.jku.at/kusss/ical-multi-form-sz.action. \n" \
                   "\t\tClick \"Create\" if the link is not there yet. \n" \
                   "**/ping *@ManagedRole* ** - Ping a course chat. \n" \
                   "**/join *<channel>* ** - Join another course chat managed by Kilian \n" \
                   "**/leave** - Leave the channel managed by Kilian. \n" \
                   "**/toggleping** - Enable or disable pings for a channel. \n" \
                   "\t\tPings are enabled deafult if you are registered for the course \n" \
                   "**/studid *<@User>* ** - Get the student id of other users. \n" \
                   "\t\tOnly possible if the student has entered his id on /kusss"
        await ctx.send(commands, ephemeral=True)


    @bot.command()
    async def studygroup(ctx):
        """Create or delete a study group."""
        pass

    @studygroup.subcommand()
    @interactions.option(description="Name of the group you want to create.")
    async def create(ctx: interactions.CommandContext, name: str):
        """Create a learning group. The group will be deleted automatically if not joined for 10 days."""
        await ctx.defer(ephemeral=True)
        category = await get_category(ctx.guild)
        channel = await ctx.guild.create_channel(
            name=name,
            type=interactions.ChannelType.GUILD_VOICE,
            parent_id=category)
        database.create_studygroup(str(ctx.guild_id), str(channel.id), name, str(ctx.author.id), datetime.now() + timedelta(days=10))
        await channel.add_permission_overwrites(
            [interactions.Overwrite(
                id=str(ctx.author.id),
                type=1,
                allow=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.READ_MESSAGE_HISTORY)])
        database.add_studygroup_member(str(ctx.guild_id), str(channel.id), str(ctx.author.id))
        await ctx.send("Created new study group: " + name, ephemeral=True)

    @studygroup.subcommand()
    @interactions.option(description="Channel of the learning group.")
    async def dissolve(ctx: interactions.CommandContext, channel: interactions.Channel):
        """Dissolve the learning group."""
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild_id)
        channel_id = str(channel.id)

        if not database.is_studygroup(guild_id, channel_id):
            await ctx.send("This channel is not a study group.", ephemeral=True)
            return

        command_performer_id = str(ctx.author.id)
        channel_creator = database.studygroup_creator(guild_id, channel_id)

        if command_performer_id != channel_creator:
            await ctx.send("You are not privileged to delete this study group.", ephemeral=True)
            return

        name = database.studygroup_name(guild_id, channel_id)
        database.delete_studygroup(guild_id, channel_id)
        await channel.delete()
        await ctx.send("Deleted study group: " + name, ephemeral=True)

    @studygroup.subcommand()
    @interactions.option(description="Channel of the learning group.")
    @interactions.option(description="User to invite.")
    async def invite(ctx: interactions.CommandContext, channel: interactions.Channel, user: interactions.Member):
        """Invite a user to the learning group."""
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild_id)
        channel_id = str(channel.id)

        if not database.is_studygroup(guild_id, channel_id):
            await ctx.send("This channel is not a study group.", ephemeral=True)
            return

        command_performer_id = str(ctx.author.id)
        channel_creator = database.studygroup_creator(guild_id, channel_id)

        if command_performer_id != channel_creator:
            await ctx.send("You are not privileged to invite somebody to this study group.", ephemeral=True)
            return

        user_id = str(user.id)

        if database.is_studygroup_member(guild_id, channel_id, user_id):
            await ctx.send(user.name + " is already in this study group.", ephemeral=True)
            return

        # send invitation
        accept_button = interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Accept",
            custom_id="accept_invite" + str(__invite_number__),
        )
        reject_button = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Reject",
            custom_id="reject_invite" + str(__invite_number__),
        )
        #__invite_number__ = __invite_number__ + 1
        await user.send(ctx.author.name + " invited you to their study group \"" + channel.name + "\" on " + ctx.guild.name + ".", components=[accept_button, reject_button])

        await ctx.send("Invitation sent to " + user.name + ".", ephemeral=True)

        @bot.component("accept_invite")
        async def accept_button_response(ctx: interactions.ComponentContext):
            await ctx.disable_all_components()
            from interactions import Permissions as p
            new_rule = interactions.Overwrite(
                id=user_id,
                type=1,
                allow=p.VIEW_CHANNEL | p.READ_MESSAGE_HISTORY)
            await channel.modify(permission_overwrites=channel.permission_overwrites + [new_rule])

            database.add_studygroup_member(guild_id, channel_id, user_id)

        @bot.component("reject_invite")
        async def reject_button_response(ctx: interactions.ComponentContext):
            await ctx.disable_all_components()

    @bot.command()
    async def sleep(ctx: interactions.CommandContext):
        """Make Kilian go nighty night."""

        if dads.count(str(ctx.author.id)):
            await ctx.send("Good night, daddy!", ephemeral=True)
            await bot._stop()
        else:
            await ctx.send("You are not my daddy!", ephemeral=True)


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

    @bot.event()
    async def on_voice_state_update(_, voice_state: interactions.VoiceState):
        if voice_state.joined:
            guild_id = str(voice_state.guild_id)
            channel_id = str(voice_state.channel_id)
            database.update_studygroup(datetime.now() + timedelta(days=10), guild_id, channel_id)


    bot.start()
