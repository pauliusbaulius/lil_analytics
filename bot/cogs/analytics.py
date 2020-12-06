import datetime
from timeit import default_timer

import discord
import discord.errors
from discord.ext import commands

import bot as db
import bot.dql as query
from bot import plotting as plot
import bot.utils as utils
from bot.decorators import timer


class Analysis(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def index(self, ctx):
        """Indexes all messages in a server that can be read by the bot.

        Goes over all channels and reads history from newest to oldest available message.
        Adds messages and their metadata to the database in 500 message bulk insertions.
        """
        print(f"lil_analytics: Started indexing {ctx.guild.name}.")
        if utils.is_owner(ctx.message.author.id):
            start = default_timer()
            msg, channels = await db.background_parse_history(self.client, ctx.guild.id)
            end = default_timer()
            await ctx.send(f"History indexing done in {str(datetime.timedelta(seconds=end - start))}. "
                           f"Indexed {msg} messages in: {channels}.")

    @commands.command()
    async def user(self, ctx, member: discord.Member, *, timezone: int = 0):
        """Displays detailed user statistics for given user.
        If no user is given, assumes that caller wants his statistics.
        """
        embed, file, time = _user(gid=ctx.guild.id, tz=timezone, member=member)
        embed.set_footer(text=time)
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def userchannel(self, ctx, member: discord.Member, channel: discord.TextChannel, *, timezone: int = 0):
        """Displays information about user in given channel.

        type: what info scope

        plot: message growth 7 days channel
        plot: message growth 30 days channel
        plot: message growth since join channel
        plot: messages per hour 7 days channel
        plot: messages per hour since join channel

        info: total messages for user channel
        info: first message date for user channel
        info: latest message date for user channel
        info: amount of reactions given by user channel
        info: amount of reactions received by user channel
        info: top 5 given reactions by user channel
        info: top 5 received reactions by user channel
        """
        # TODO implement.
        print(member, channel, timezone)
        await ctx.send("Not implemented yet...")

    @commands.command()
    async def channel(self, ctx, channel: discord.TextChannel, *, timezone: int = 0):
        """Displays detailed channel statistics for given channel.
        If no channel is given, assumes that caller wants current channel statistics.
        """
        embed, file, time = _channel(tz=timezone, guild=ctx.guild, channel=channel)
        embed.set_footer(text=time)
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def server(self, ctx, timezone: int = 0):
        """Displays detailed server statistics."""
        embed, file, time = _server(tz=timezone, guild=ctx.guild)
        embed.set_footer(text=time)
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def today(self, ctx, timezone: int = 0):
        """Displays detailed server statistics."""
        embed, file, time = _today(tz=timezone, guild=ctx.guild)
        embed.set_footer(text=time)
        await ctx.send(file=file, embed=embed)


@timer
def _user(gid, tz: int, member: discord.Member):
    start = default_timer()

    # Generate plots.
    p1 = plot.plot_message_times(guild_id=gid, user_id=member.id, timezone=tz)
    p2 = plot.plot_growth_message_days(guild_id=gid, user_id=member.id, days=7)
    p3 = plot.plot_growth_message_days(guild_id=gid, user_id=member.id, days=30)
    p4 = plot.plot_growth_message_days(guild_id=gid, user_id=member.id, days=-1)
    p5 = plot.barh_user_channel_activity(guild_id=gid, author_id=member.id, author_name=member.name)
    p6 = plot.barh_message_days(guild_id=gid, user_id=member.id, days=7)
    p7 = plot.plot_histogram_message_length(guild_id=gid, user_id=member.id)
    p8 = plot.plot_bar_messages_weekday(guild_id=gid, user_id=member.id)

    # Join plots into single large image.
    image_path = utils.pillow_join_grid(50, 50, 50, 50, [p1, p2, p3, p4], [p8, p6, p7, p5])

    total_messages = query.get_messages_total(guild_id=gid, user_id=member.id)
    first_message = query.get_user_message_date(guild_id=gid, user_id=member.id, tz=tz, order="ASC")
    last_message = query.get_user_message_date(guild_id=gid, user_id=member.id, tz=tz)
    top_given = query.get_reaction_given_counts(guild_id=gid, user_id=member.id)
    top_received = query.get_reaction_received_counts(guild_id=gid, user_id=member.id)
    total_given = sum([x[0] for x in top_given])
    total_received = sum([x[0] for x in top_received])

    # Extract top given/received as nice string.
    top_given = "\n".join([f"{x[0]} {x[1]}" for x in top_given[:5]])
    top_received = "\n".join([f"{x[0]} {x[1]}" for x in top_received[:5]])

    # Dirty cast datetime to string and remove seconds and milliseconds.
    join_date = member.joined_at
    join_date = str(join_date)[:10]

    embed = discord.Embed(title="", color=member.color)
    embed.set_image(url="attachment://image.png")
    embed.add_field(name="Username:", value=member.name)
    embed.add_field(name="Joined:", value=join_date)
    embed.add_field(name="Top role:", value=member.top_role)
    embed.add_field(name="Messages:", value=str(total_messages) if not None else "Not enough data.")
    embed.add_field(inline=False, name="First message:", value=first_message if not None else "Not enough data.")
    embed.add_field(inline=False, name="Latest message:", value=last_message if not None else "Not enough data.")
    embed.add_field(name="Reactions given:", value=total_given)
    embed.add_field(name="Reactions received:", value=total_received)
    if top_given: embed.add_field(inline=False, name="Top given reactions:", value=top_given)
    if top_received: embed.add_field(inline=False, name="Top received reactions:", value=top_received)
    embed.set_author(name="USER ANALYTICS")
    embed.set_thumbnail(url=member.avatar_url)

    file = discord.File(image_path, filename="image.png")
    # Close image in memory.
    image_path.close()
    end = default_timer()
    time = "It took me {:.2f} seconds to complete this function.".format(end - start)
    return embed, file, time


@timer
def _channel(tz: int, channel: discord.TextChannel, guild: discord.Guild):
    start = default_timer()
    gid = guild.id
    cid = channel.id

    # Generate plots.
    p1 = plot.plot_message_times(guild_id=gid, timezone=tz)
    mgd7 = plot.plot_growth_message_days(guild_id=gid, channel_id=cid, days=7)
    mgd30 = plot.plot_growth_message_days(guild_id=gid, channel_id=cid, days=30)
    mgdall = plot.plot_growth_message_days(guild_id=gid, channel_id=cid, days=-1)
    pmd7 = plot.barh_message_days(guild_id=gid, channel_id=cid, days=7)
    pmd30 = plot.barh_message_days(guild_id=gid, channel_id=cid, days=30)
    phml = plot.plot_histogram_message_length(guild_id=gid, channel_id=cid)
    pbmw = plot.plot_bar_messages_weekday(guild_id=gid, channel_id=cid)
    psma = plot.plot_server_most_active(guild_id=gid, channel_id=cid, amount=30, days=-1)
    psm7 = plot.plot_server_most_active(guild_id=gid, channel_id=cid, amount=30, days=7)
    psm30 = plot.plot_server_most_active(guild_id=gid, channel_id=cid, amount=30, days=30)
    phum = plot.plot_histogram_users_messages(guild_id=gid, channel_id=cid)
    phum2 = plot.plot_histogram_users_messages(guild_id=gid, channel_id=cid, cumulative=False)

    image_path = utils.pillow_join_grid(50, 50, 50, 50, [p1, pbmw, phml, phum], [pmd7, pmd30, phum2],
                                        [mgd7, mgd30, mgdall], [psm7, psm30, psma])

    total_messages = query.get_messages_total(guild_id=gid, channel_id=cid)
    top_given = query.get_reaction_given_counts(guild_id=gid, channel_id=cid)
    total_given = sum([x[0] for x in top_given])
    top_given_reactions = "\n".join([f"{x[0]} {x[1]}" for x in top_given[:7]])

    embed = discord.Embed(title="")
    embed.set_image(url="attachment://image.png")
    embed.set_author(name="CHANNEL ANALYTICS")
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Name:", value=str(channel.name))
    embed.add_field(name="Created:", value=str(channel.created_at), inline=False)
    embed.add_field(name="Position:", value=channel.position)
    embed.add_field(name="Category:", value=str(channel.category))
    if total_messages: embed.add_field(name="Messages:", value=str(total_messages))
    if top_given: embed.add_field(inline=False, name="Reactions given:", value=total_given)
    if top_given_reactions: embed.add_field(inline=False, name="Top given reactions:", value=top_given_reactions)

    file = discord.File(image_path, filename="image.png")
    # Close image in memory.
    image_path.close()
    end = default_timer()
    time = "It took me {:.2f} seconds to complete this function.".format(end - start)
    return embed, file, time


@timer
def _server(tz: int, guild):
    start = default_timer()
    gid = guild.id

    # Generate plots.
    p1 = plot.plot_message_times(guild_id=gid, timezone=tz)
    mgd7 = plot.plot_growth_message_days(guild_id=gid, days=7)
    mgd30 = plot.plot_growth_message_days(guild_id=gid, days=30)
    mgdall = plot.plot_growth_message_days(guild_id=gid, days=-1)
    pmd7 = plot.barh_message_days(guild_id=gid, days=7)
    pmd30 = plot.barh_message_days(guild_id=gid, days=30)
    phml = plot.plot_histogram_message_length(guild_id=gid)
    pbmw = plot.plot_bar_messages_weekday(guild_id=gid)
    pcmall = plot.plot_server_channels_messages(guild_id=gid, amount=30)
    pcm7 = plot.plot_server_channels_messages(guild_id=gid, amount=30, days=7)
    pcm30 = plot.plot_server_channels_messages(guild_id=gid, amount=30, days=30)
    psma = plot.plot_server_most_active(guild_id=gid, amount=30, days=-1)
    psm7 = plot.plot_server_most_active(guild_id=gid, amount=30, days=7)
    psm30 = plot.plot_server_most_active(guild_id=gid, amount=30, days=30)
    phum = plot.plot_histogram_users_messages(guild_id=gid)
    phum2 = plot.plot_histogram_users_messages(guild_id=gid, cumulative=False)

    image_path = utils.pillow_join_grid(50, 50, 50, 50, [p1, pbmw, phml, phum], [pmd7, pmd30, phum2, psma],
                                        [mgd7, mgd30, mgdall, psm7], [pcm7, pcm30, pcmall, psm30])

    total_messages = query.get_messages_total(guild_id=gid)
    top_given = query.get_reaction_given_counts(guild_id=gid)
    total_given = sum([x[0] for x in top_given])
    top_given = "\n".join([f"{x[0]} {x[1]}" for x in top_given[:7]])
    total_users = len(guild.members)

    embed = discord.Embed(title="")
    embed.set_image(url="attachment://image.png")
    embed.add_field(inline=False, name="Description:", value=guild.description)
    embed.add_field(inline=False, name="Owner:", value=str(guild.owner))
    embed.add_field(name="Messages:", value=str(total_messages))
    embed.add_field(name="Users:", value=str(total_users))
    embed.add_field(name="Boosters:", value=str(guild.premium_subscription_count))
    embed.add_field(name="Channels:", value=str(len(guild.channels)))
    embed.add_field(name="Text channels:", value=str(len(guild.text_channels)))
    embed.add_field(name="Voice channels:", value=str(len(guild.voice_channels)))
    embed.add_field(inline=False, name="Reactions given:", value=total_given)
    embed.add_field(inline=False, name="Top given reactions:", value=top_given)
    embed.set_author(name="SERVER ANALYTICS")
    embed.set_thumbnail(url=guild.icon_url)

    file = discord.File(image_path, filename="image.png")
    # Close image in memory.
    image_path.close()
    end = default_timer()
    time = "It took me {:.2f} seconds to complete this function.".format(end - start)
    return embed, file, time


@timer
def _today(tz: int, guild):
    start = default_timer()

    # Create embed for the visual statistics.
    embed = discord.Embed(title="")
    embed.set_author(name="DAILY ANALYTICS")
    embed.set_image(url="attachment://image.png")
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(inline=False, name="Date:", value=str(datetime.datetime.today().strftime('%Y-%m-%d')))
    embed.add_field(name="Messages:", value=f"+{query.get_messages_total_today(guild_id=guild.id)}")
    embed.add_field(name="Reactions:", value=f"+{sum([x[0] for x in query.get_reactions_today(guild_id=guild.id)])}")

    # Get some plots in here.
    p1 = plot.plot_message_times_today(guild_id=guild.id, timezone=tz)
    p2 = plot.plot_server_channels_messages_today(guild_id=guild.id, amount=20)
    p3 = plot.plot_server_most_active_today(guild_id=guild.id, amount=20)

    image_path = utils.pillow_join_grid(50, 50, 50, 50, [p1, p2, p3])
    file = discord.File(image_path, filename="image.png")
    end = default_timer()
    time = "It took me {:.2f} seconds to complete this function.".format(end - start)
    return embed, file, time


def setup(client):
    client.add_cog(Analysis(client))
