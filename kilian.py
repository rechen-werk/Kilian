"""
    File name: kilian.py
    Author: Adrian Vinojcic, Tobias Pilz
    This part is responsible for everything related to the discord api.
"""

import argparse
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
        try:
            guild_id = str(ctx.guild_id)
            current_semester = uni.current_semester()
            student = uni.student(str(ctx.author.id), link, studentnumber)
            database.insert(student)

            await ctx.send("Welcome on board " + ctx.author.name + "!")

            guild_course_names = database.get_server_courses(guild_id, current_semester)
            new_courses = database.get_added_courses(student.discord_id, current_semester)
            missing_courses_by_name = dict()
            for course in new_courses:
                if course.lva_name in guild_course_names:
                    continue
                if course.lva_name not in missing_courses_by_name.keys():
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
                database.set_cagegory(guild_id, str(category.id))

            added_roles = Roles()
            for course_name in missing_courses_by_name:
                role = await ctx.guild.create_role(course_name)
                channel = await ctx.guild.create_channel(
                    name=course_name,
                    type=interactions.ChannelType.GUILD_TEXT,
                    parent_id=category)
                added_roles.add((course_name, uni.current_semester(), guild_id, str(role.id), str(channel.id)))

            database.insert(added_roles)
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

        await ctx.send(ping_string + "\n" + content)

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

        link = database.get_link(discord_id)
        student = uni.student(discord_id, link)
        courses = student.courses
        lva_nrs = map(lambda c: c.lva_nr, courses)

        database.insert(StudentCourse(discord_id, semester, lva_nr, 0))

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
        lva_nr = database.get_lva_nr(lva_name, semester)

        await ctx.send(f"{ctx.author.name} left the channel.", ephemeral=True)

        channel = ctx.channel
        permission_overwrites = channel.permission_overwrites
        permission_overwrites = list(filter(lambda po: po.id != ctx.author.id, permission_overwrites))
        await channel.modify(permission_overwrites=permission_overwrites)

        database.delete_student_role(discord_id, lva_nr, semester)



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

        guild = await message.get_guild()
        guild_id = str(guild.id)
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

        await message.reply(ping_string)


    @bot.event()
    async def on_start():
        print("Good morning daddy!")


    bot.start()
