"""
    File name: kilian.py
    Author: Adrian Vinojcic
    This part is responsible for everything related to the discord api.
"""

import argparse
import interactions
import kusss as uni


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

    bot = interactions.Client(token=bot_token, intents=interactions.Intents.ALL)

    @bot.command()
    @interactions.option(description="Provide the calendar link from KUSSS here.")
    @interactions.option(description="Optionally provide your matriculation number here.")
    async def kusss(ctx: interactions.CommandContext, link: str, studentnumber: str = None):
        """Take advantage of the features provided by Kilian™."""
        try:
            student = uni.student(str(ctx.author.id), link, studentnumber)
            user_id = ctx.author.id

            # TODO: save *user_id* and *user_token* into database
            # TODO: map anonymous roles to user

            await ctx.send("Welcome on board " + ctx.author.name + "!")
        except uni.InvalidURLException as ex:
            await ctx.send(ex.message, ephemeral=True)

    @bot.command()
    async def unkusss(ctx: interactions.CommandContext):
        """Unsubscribe from the awesome features provided by Kilian™."""
        user_id = ctx.author.id

        # TODO: delete all rows which contain *user_id* from the database
        # TODO: delete anonymous role mappings from user

        await ctx.send("A pity to see you leave " + ctx.author.name + ". You can join the club anytime with `/kusss`!")

    @bot.command()
    @interactions.option(description="Role you want to ping.")
    @interactions.option(description="Message content goes here.")
    async def ping(ctx: interactions.CommandContext, role: interactions.Role, content: str = ""):
        """Ping everyone partaking that subject."""
        role_id = role.id

        # TODO: check if said role is a managed role and send an ephemeral errormessage otherwise
        # TODO: get all users mapped to said *role_id*
        users_with_anonymous_role = set()

        # TODO: ping all users with said role in one message
        ping_string = ""
        for user in users_with_anonymous_role:
            yield

        message = await ctx.send(ping_string)
        await message.edit(role.mention + "\n" + content)

        # POSSIBLE ERROR: too many users, so that not all pings fit in one message
        # POSSIBLE SOLUTION TO ERROR: give all pinged users the role temporarily, ping them, and remove the role

    @bot.command()
    @interactions.option(description="The user you want the student id of.")
    async def studid(ctx: interactions.CommandContext, member: interactions.Member):
        """Get student id of the specified user."""
        member_id = member.id
        student_id = "get id"
        await ctx.send(student_id, ephemeral=True)


    @bot.event()
    async def on_message_create(message: interactions.Message):
        if message.author.id == bot.me.id:
            return
        mentioned_roles = message.mention_roles
        if len(mentioned_roles) == 0:
            return

        # TODO: check if a role is a managed role
        # TODO: get all users mapped to said *role_id*
        users_with_anonymous_role = set()

        # TODO: ping all users with said role in one message
        await message.reply("ok ok")

    @bot.event()
    async def on_guild_create(guild: interactions.Guild):
        print(guild.member_count)


    @bot.event()
    async def on_start():
        print("on_start")
        for g in bot.guilds:
            print(g.name)


    bot.start()
