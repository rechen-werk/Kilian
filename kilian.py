"""
    File name: kilian.py
    Author: Adrian Vinojcic
    This part is responsible for everything related to the discord api.
"""

import argparse
import interactions
import kusss as uni
from database import Database


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token",
        type=str,
        required=False,
        dest='token',
        help="Provide the Discord Bot Token as string."
    )
    return parser.parse_args()


def read_token_file():
    with open("secrets", 'r') as f:
        return f.readlines()[0].strip()


if __name__ == '__main__':
    args = parse_args()
    bot_token = args.token if args.token is not None else read_token_file()

    database = Database()

    bot = interactions.Client(token=bot_token, intents=interactions.Intents.ALL)

    @bot.command()
    @interactions.option(description="Provide the calendar link from KUSSS here.")
    @interactions.option(description="Optionally provide your matriculation number here.")
    async def kusss(ctx: interactions.CommandContext, link: str, studentnumber: str = None):
        """Take advantage of the features provided by Kilian™."""
        try:
            student = uni.student(str(ctx.author.id), link, studentnumber)
            database.insert(student)
            for course_key in student.courses:
                for guild in bot.guilds:
                    course: uni.Course = None # get course from key in course_key

                    # if role does not exist on this server
                    # role = await guild.create_role(name=course.lva_name, color=0xD8E4FF)
                    guild_id = guild.id
                    # role_id = role.id
                    # database.insert()

            await ctx.send("Welcome on board " + ctx.author.name + "!")
        except uni.InvalidURLException as ex:
            await ctx.send(ex.message, ephemeral=True)

    @bot.command()
    async def unkusss(ctx: interactions.CommandContext):
        """Unsubscribe from the awesome features provided by Kilian™."""
        user_id = ctx.author.id

        # TODO: delete all roles (archive/delete channels) from server that only this user had
        database.delete_student(str(user_id))

        await ctx.send("A pity to see you leave " + ctx.author.name + ". You can join the club anytime with `/kusss`!")

    @bot.command()
    @interactions.option(description="Role you want to ping.")
    @interactions.option(description="Message content goes here.")
    async def ping(ctx: interactions.CommandContext, role: interactions.Role, content: str = ""):
        """Ping everyone partaking that subject."""
        role_id = str(role.id)
        guild_id = str(ctx.guild_id)


        # DONE: check if said role is a managed role and send an ephemeral errormessage otherwise
        # DONE: get all users mapped to said *role_id*
        users_with_anonymous_role = set()
        if database.is_managed_role(guild_id, role_id):
            users_with_anonymous_role = database.get_role_members(guild_id, role_id)

        ping_string = ""
        for user_id in users_with_anonymous_role:
            user = (await ctx.guild.get_member(int(user_id))).user
            ping_string += user.mention

        # DONE: ping all users with said role in one message

        message = await ctx.send(ping_string + "\n" + content)
        # await message.edit(role.mention + "\n" + content)

        # POSSIBLE ERROR: too many users, so that not all pings fit in one message
        # POSSIBLE SOLUTION TO ERROR: give all pinged users the role temporarily, ping them, and remove the role

    @bot.command()
    @interactions.option(description="The user you want the student id of.")
    async def studid(ctx: interactions.CommandContext, member: interactions.Member):
        """Get student id of the specified user."""
        member_id = member.id
        student_id = "get id"
        await ctx.send(student_id, ephemeral=True)


    @bot.command()
    async def sleep(ctx: interactions.CommandContext):
        """Make Kilian go nighty night."""

        def is_dad(user_id: str):
            with open("dads", 'r') as dads:
                for line in dads.readlines():
                    if line[:-1] == user_id:
                        return True
            return False

        if is_dad(str(ctx.author.id)):
            await ctx.send("Good night, daddy!", ephemeral=True)
        else:
            await ctx.send("You are not my daddy!", ephemeral=True)


    @bot.event()
    async def on_message_create(message: interactions.Message):
        if message.author.id == bot.me.id:
            return

        guild = await message.get_guild()
        guild_id = str(guild.id)
        mentioned_roles = [role_id for role_id in message.mention_roles if database.is_managed_role(guild_id, role_id)]
        if len(mentioned_roles) == 0:
            return

        # DONE: check if a role is a managed role
        # DONE: get all users mapped to said *role_id*

        users_with_anonymous_role = set()
        for role_id in mentioned_roles:
            users_with_anonymous_role = users_with_anonymous_role | database.get_role_members(guild_id, role_id)

        # DONE: ping all users with said role in one message
        await message.reply("ok ok")

        ping_string = ""
        for user_id in users_with_anonymous_role:
            user = (await guild.get_member(int(user_id))).user
            ping_string += user.mention

        channel = await message.get_channel()

        content = message.content
        # await message.delete()
        message = await channel.send(ping_string)
        await message.edit(content)

    @bot.event()
    async def on_guild_create(guild: interactions.Guild):
        for member in guild.members:
            user_id = member.id



    @bot.event()
    async def on_start():
        print("Good morning master!")


    bot.start()
