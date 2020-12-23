from discord.ext import commands


class ErrorHandler(commands.Cog):

    # Allows to access client within methods
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return

        ignored = commands.UserInputError
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return await ctx.send("You gave me bad arguments!")

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"This command is on a cooldown. Try again in {int(error.retry_after)} second(s).")

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send("You do not have the permission to use this command.")

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.BadArgument):
            return await ctx.send("You gave me bad arguments!")

        elif isinstance(error, commands.CommandInvokeError):
            return await ctx.send("Bad argument, try again.")


# Add cog to client.
def setup(client):
    client.add_cog(ErrorHandler(client))
