import discord
from discord.ext import commands

from src import utils
import definitions

class ToolsGeneral(commands.Cog):

    # Allows to access client within methods
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["help", "h"])
    async def functions(self, ctx):
        embed = discord.Embed(title="General Commands", description=f'You can find out more [here]({definitions.github_link}).',
                              color=0x008000)
        embed.add_field(name="info", value="Information about lil analytics.")
        embed.add_field(name="functions/help/h", value="Prints this message.")
        embed.add_field(name="avatar", value="Avatars of tagged user(s), empty call returns your picture.")
        embed.add_field(name="userinfo", value="Information about tagged user(s).")
        await ctx.send(embed=embed)

        # Fun commands
        embed = discord.Embed(title="Fun Commands",
                              description=f'You can find out more [here]({definitions.github_link}).',
                              color=0x0000ff)
        embed.add_field(name="b", value="Makes bot say your text in next generation caps.")
        embed.add_field(name="choose/c", value="Random pick from your inputs separated by ';'.")
        embed.add_field(name="8ball", value="The classic 8ball game, is there more to say?")
        await ctx.send(embed=embed)

        # Administration commands
        embed = discord.Embed(title="Administration Commands",
                              description=f'You can find out more [here]({definitions.github_link}).',
                              color=0xff0000)
        embed.add_field(name="kick", value="Kicks mentioned user. Can pass a reason.")
        embed.add_field(name="ban", value="Bans mentioned user. Can pass a reason.")
        embed.add_field(name="clear", value="Takes number or 'all' as argument. Deletes messages.")
        embed.add_field(name="gdpr", value="Deletes all messages in the channel made by the mentioned user.")
        embed.add_field(name="export", value="Exports all messages in the server made by the mentioned user. "
                                             "Can give be given a limit. Otherwise exports all messages.")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def info(self, ctx):
        """Prints information about the bot. Sends an embedded message."""
        # TODO add info how many commands executed in total!
        # Get links from settings.json
        desc = "Message metadata analytics for your server! Type .help or .h to see all available commands."
        embed = discord.Embed(title="lil analytics", description=desc, color=0xffff00)
        embed.add_field(name="Author:", value="pauliusbaulius", inline=False)
        # Shows the number of servers the bot is member of.
        embed.add_field(name="Server count:", value=f"{len(self.client.guilds)}", inline=False)
        embed.add_field(name="Invite me:", value=f'[>click me<]({definitions.invite_link})', inline=False)
        embed.add_field(name="Source code:", value=f'[>click me<]({definitions.github_link})', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx):
        """
        Posts embedded message in callers channel with profile pictures of mentioned users.
        If nobody is mentioned, it will post callers profile picture.
        If multiple profiles are mentioned, it will send embedded message for each one.
        Does not post duplicates of profiles.
        """
        # If nobody got mentioned, send senders avatar.
        if not ctx.message.mentions:
            mentioned_id = ctx.message.author
            await send_avatar(ctx, mentioned_id)
        if len(ctx.message.mentions) >= 1:
            # Otherwise pick all mentions.
            mentioned_id = ctx.message.mentions
            for mention in mentioned_id:
                await send_avatar(ctx, mention)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def userinfo(self, ctx):
        """
        Posts embedded message in callers channel with profile pictures of mentioned users.
        If nobody is mentioned, it will post callers profile picture.
        If multiple profiles are mentioned, it will send embedded message for each one.
        Does not post duplicates of profiles.
        """
        # If nobody got mentioned, send senders avatar.
        if not ctx.message.mentions:
            mentioned_id = ctx.message.author
            await send_user(ctx, mentioned_id)
        if len(ctx.message.mentions) >= 1:
            # Otherwise pick all mentions.
            mentioned_id = ctx.message.mentions
            for mention in mentioned_id:
                await send_user(ctx, mention)


async def send_avatar(ctx, mentioned_id):
    """Helper method of avatar() function. Takes ctx and id of user.
    Sends embedded message with profile pic in callers channel.
    """
    embed = discord.Embed(title=f"{mentioned_id}")
    embed.set_image(url=mentioned_id.avatar_url)
    await ctx.send(embed=embed)


async def send_user(ctx, mentioned_id):
    # Parse roles in readable format.
    roles = [role.name for role in mentioned_id.roles]
    # Parse permissions.
    permissions = []
    activity = iter(mentioned_id.guild_permissions)
    for i in activity:
        permissions.append(i[0])

    # Dirty cast datetime to string and remove seconds and milliseconds.
    join_date = mentioned_id.joined_at
    join_date = str(join_date)[:16]

    created_date = mentioned_id.created_at
    created_date = str(created_date)[:16]

    status_message = f"Desktop: {mentioned_id.desktop_status}\n " \
                     f"Mobile: {mentioned_id.mobile_status}\n " \
                     f"Web: {mentioned_id.web_status}"

    # Create embedding.
    embed = discord.Embed(title=f"{mentioned_id}", color=mentioned_id.colour)
    embed.add_field(name="Online?", value=status_message, inline=False)
    embed.add_field(name="Display name:", value=mentioned_id.display_name, inline=False)
    embed.add_field(name="Created account:", value=created_date, inline=False)
    embed.add_field(name="Joined this server:", value=join_date, inline=False)
    embed.add_field(name="Has roles:", value=", ".join(roles), inline=False)
    embed.add_field(name="Top role:", value=mentioned_id.top_role, inline=False)
    # Handle different activities
    for activity in mentioned_id.activities:
        # if activity.type is discord.ActivityType.listening:
        #     embed.add_field(name="Spotify:", value=get_spotify_song(activity), inline=False)
        if activity.type is discord.ActivityType.playing:
            embed.add_field(name="Game:", value=activity.name)
        elif activity.type is discord.ActivityType.streaming:
            print(activity.name, activity.game, activity.url, activity.twitch_name)
        elif activity.type is discord.ActivityType.watching:
            print(activity.name)
        elif activity.type is discord.ActivityType.custom:
            embed.add_field(name="Custom status:", value=f"{activity.emoji} {activity.name}", inline=False)
    embed.set_image(url=mentioned_id.avatar_url)
    await ctx.send(embed=embed)


# Add cog to client.
def setup(client):
    client.add_cog(ToolsGeneral(client))
