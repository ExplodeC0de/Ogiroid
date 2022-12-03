import disnake
import datetime as dt
from disnake.ext import commands, tasks
import pytz

from utils.DBhandlers import TimezoneHandler
from utils.exceptions import UserAlreadyExists, UserNotFound
from utils.shortcuts import QuickEmb, sucEmb, errorEmb
from utils.CONSTANTS import months, congrats_messages, timezones
from utils.bot import OGIROID


async def autocomplete_timezones(inter, user_input: str):
    return [tz for tz in timezones if user_input.lower() in tz.lower()]


class Timezone(commands.Cog):
    def __init__(self, bot: OGIROID):
        self.bot = bot
        self.db_timezone: TimezoneHandler = None

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready_:
            self.db_timezone: TimezoneHandler = TimezoneHandler(self.bot, self.bot.db)

    @commands.slash_command(name="timezone")
    async def timezone(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @timezone.sub_command(name="set", description="Set your timezone.")
    async def set(
        self,
        inter,
        timezone=commands.Param(
            name="timezone",
            description="Your timezone. Start typing a major city around you or a continent.",
            autocomplete=autocomplete_timezones,
        ),
    ):

        if timezone is None:
            return await errorEmb(inter, "You need to provide a timezone")
        if timezone not in timezones:
            return await errorEmb(inter, "The timezone you provided is not valid")
        try:
            await self.db_timezone.create_user(inter.author.id, timezone)
        except UserAlreadyExists:
            return await errorEmb(inter, "You already have a timezone set")

        await sucEmb(
            inter,
            f"Your timezone has been set to {timezone}. Its currently <t:{str(dt.datetime.now(pytz.timezone(timezone)).timestamp()).split('.')[0]}:t> at your location.",
        )

    @commands.has_permissions(manage_roles=True)
    @timezone.sub_command(name="edit", description="Edit your timezone.")
    async def edit(
        self,
        inter,
        timezone=commands.Param(
            name="timezone",
            description="Your timezone. Start typing a major city around you or a continent.",
            autocomplete=autocomplete_timezones,
        ),
    ):
        if timezone is None:
            return await errorEmb(inter, "You need to provide a timezone")
        if timezone not in timezones:
            return await errorEmb(inter, "The timezone you provided is not valid")
        try:
            await self.db_timezone.update_user(inter.author.id, timezone)
            return await sucEmb(
                inter,
                f"Your timezone has been set to {timezone}."
                f" Its currently <t:{str(dt.datetime.now(pytz.timezone(timezone)).timestamp()).split('.')[0]}:t>"
                f" at your location.",
            )
        except UserNotFound:
            return await errorEmb(inter, "The User doesn't have a timezone set")

    @timezone.sub_command(name="remove", description="Remove your timezone.")
    async def remove(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        try:
            await self.db_timezone.delete_user(inter.author.id)
        except UserNotFound:
            return await errorEmb(inter, "This user doesn't have a timezone set")

        await sucEmb(inter, "The timezone has been removed")

    @timezone.sub_command(name="get", description="Get the timezone of a user")
    async def get(self, inter, user: disnake.User = commands.Param(name="user", default=None)):
        if user is None:
            user = inter.author
        else:
            user = await self.bot.fetch_user(user.id)

        timezone = await self.db_timezone.get_user(user.id)
        if timezone is None:
            return await errorEmb(inter, "This user doesn't have a timezone set")
        await QuickEmb(
            inter,
            f"{user.mention}'s timezone is {timezone.timezone} .Its currently <t:{str(dt.datetime.now(pytz.timezone(timezone.timezone)).timestamp()).split('.')[0]}:t> for them",
        ).send()


def setup(bot):
    bot.add_cog(Timezone(bot))
