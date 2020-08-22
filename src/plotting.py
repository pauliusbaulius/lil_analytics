import io

<<<<<<< HEAD
=======
import numpy as np
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter

import src.dql as db
from src.decorators import timer
from src.dql import (get_channels_messages, get_messages_growth_days,
                     get_user_channel_activity, get_user_most_active)
from src.utils import shift_hour


"""
    This module generates Matplotlib graphs and returns their path on the system the bot is running on.
    User interface module calls those functions and then posts plots in Discord.
    
    This is the worst code, since I am new to Matplotlib - there will be a ton of code copying and bad code.
    DRY dies here. Rip.
"""

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_growth_message_days(guild_id: int, days: int, channel_id=None, user_id: int = None) -> "path to plot image":
    """Plots message growth per day for given amount of days. Can be done for server, channel, user or user
    in a channel.

    If days are passed as -1 or 0, all messages in db are queried.
    """
    data = db.get_messages_growth_days(guild_id=guild_id, days=days, channel_id=channel_id, user_id=user_id)
    if data:
        x_val = [x[0] for x in data]
        y_val = [x[1] for x in data]

        # Do not show x labels if they would get too crammed!
        show_x = False if days > 30 or days == -1 else True
        title = f"Message growth for last {days} days" if days > 0 else f"Message growth all time"

        path = generate_plot(x_val,
                             y_val,
                             ylabel="Messages",
                             title=title,
                             show_x=show_x)
        return path

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_message_times(guild_id: int, channel_id: int = None, user_id: int = None, timezone: int = 0) -> "path to " \
                                                                                                         "plot image":
    """Plots user messages per hour. Considers all messages from all channels. Generates a plot for 7, 30 and all days.

    shift_hour() shifts UTC time by given integer, so time in Berlin is UTC+2, Vilnius is UTC+3.
    """
    # Build plot of of 2 subplots for messages per hour for last 7 days and all time in server.
    fig, axs = plt.subplots(3, constrained_layout=True)
    fig.suptitle(f"Messages per hour for timezone UTC+{timezone}")

    data = db.get_messages_by_hour_days(guild_id=guild_id, channel_id=channel_id, user_id=user_id, days=7)
    x_val = [shift_hour(x[0], timezone) for x in data]
    y_val = [x[1] for x in data]
    axs[0].plot(x_val, y_val)
    axs[0].set_title("Last 7 days")
    axs[0].tick_params(labelrotation=45)
    axs[0].fill_between(x_val, y_val, color="blue", alpha=1)

    data = db.get_messages_by_hour_days(guild_id=guild_id, channel_id=channel_id, user_id=user_id, days=30)
    x_val = [shift_hour(x[0], timezone) for x in data]
    y_val = [x[1] for x in data]
    axs[1].plot(x_val, y_val)
    axs[1].set_title("Last 30 days")
    axs[1].tick_params(labelrotation=45)
    axs[1].fill_between(x_val, y_val, color="blue", alpha=1)

    data = db.get_messages_by_hour(guild_id=guild_id, channel_id=channel_id, user_id=user_id)
    x_val = [shift_hour(x[0], timezone) for x in data]
    y_val = [x[1] for x in data]
    axs[2].plot(x_val, y_val)
    axs[2].set_title("All time")
    axs[2].tick_params(labelrotation=45)
    axs[2].fill_between(x_val, y_val, color="blue", alpha=1)

    for ax in axs.flat:
        ax.set(ylabel='Messages')

    return finish_plt(plt)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def barh_message_days(guild_id, days, channel_id=None, user_id=None) -> "path to plot image":
    data = db.get_messages_per_day(guild_id=guild_id, channel_id=channel_id, user_id=user_id, days=days)
    if data:
        y_val = [x[0] for x in data]
        x_val = [x[1] for x in data]
        return generate_barh(x_val, y_val, title=f"Messages last {days} days", xlabel="Messages")

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_histogram_message_length(guild_id, channel_id=None, user_id=None) -> "path to plot":
    """Generate histogram form message length distribution.
    Does it for server, channel, user or user in a channel.

    Divides data into 4 sets, messages with length under 100, 250, 500 and all messages.
    This allows closer look into distributions of most messages, since most of them will be under 500
    characters long. All messages will have some occasional messages with thousands of characters.
    """

    data = db.get_messages_length(guild_id=guild_id, channel_id=channel_id, user_id=user_id)
    if data:
        x_val = [x[0] for x in data]

        fig, axs = plt.subplots(2, 2)
        fig.suptitle("Msg len. distribution", fontsize=13)

        axs[0, 0].hist([x for x in x_val if x <= 100], bins=30, color="blue")
        axs[0, 0].set_title("<= 100", fontsize=8)

        axs[0, 1].hist([x for x in x_val if x <= 250], bins=30, color="blue")
        axs[0, 1].set_title("<= 250", fontsize=8)

        axs[1, 0].hist([x for x in x_val if x <= 500], bins=30, color="blue")
        axs[1, 0].set_title("<= 500", fontsize=10)

        axs[1, 1].hist(x_val, bins=30, color="blue")
        axs[1, 1].set_title("All lengths", fontsize=8)

        plt.tight_layout()

        return finish_plt(plt)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_histogram_users_messages(guild_id: int, channel_id: int = None, cumulative: bool = True):
    """Generate user message distribution histogram. Can be done for the whole server or a channel."""
    data = db.get_user_most_active(guild_id=guild_id, channel_id=channel_id, amount=-1)
    if data:
        x_val = [x[0] for x in data]

        if cumulative:
            plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
            plt.hist(x_val, density=True, cumulative=True, bins=100, color="blue")
            plt.title("Message distribution for users cumulative")
        else:
            plt.hist(x_val, color="blue")
            plt.title("Message distribution for users")

        plt.ylabel("Amount of users")
        plt.xlabel("Amount of messages")

        return finish_plt(plt)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_bar_messages_weekday(guild_id: int, user_id: int = None, channel_id: int = None) -> "path to plot":
    # Build plot of of 2 subplots for messages per hour for last 7 days and all time in server.
    fig, axs = plt.subplots(3, constrained_layout=True)
    fig.suptitle(f"Messages per day")

    data = db.get_messages_by_weekday_days(guild_id=guild_id, days=7, channel_id=channel_id, user_id=user_id)
    x_val = [str(x[0][:2]) for x in data]
    y_val = [x[1] for x in data]
    axs[0].plot(x_val, y_val)
    axs[0].set_title("Last 7 days")
    axs[0].fill_between(x_val, y_val, color="blue", alpha=1)

    data = db.get_messages_by_weekday_days(guild_id=guild_id, days=30, channel_id=channel_id, user_id=user_id)
    x_val = [str(x[0][:2]) for x in data]
    y_val = [x[1] for x in data]
    axs[1].plot(x_val, y_val)
    axs[1].set_title("Last 30 days")
    axs[1].fill_between(x_val, y_val, color="blue", alpha=1)

    data = db.get_messages_by_weekday_days(guild_id=guild_id, days=-1, channel_id=channel_id, user_id=user_id)
    x_val = [str(x[0][:2]) for x in data]
    y_val = [x[1] for x in data]
    axs[2].plot(x_val, y_val)
    axs[2].set_title("All time")
    axs[2].fill_between(x_val, y_val, color="blue", alpha=1)

    for ax in axs.flat:
        ax.set(ylabel='Messages')

    return finish_plt(plt)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_server_most_active(guild_id: int, amount: int, days: int = None, channel_id: int = None):
    data = get_user_most_active(guild_id=guild_id, amount=amount, days=days, channel_id=channel_id)
    if data:
        x_val = [x[0] for x in data]
        y_val = [x[1] for x in data]
        title = f"Top {amount} users by messages {days} days" if days > 0 else f"Top {amount} users by messages"
        xlabel = "Messages"
        return generate_barh(x_val, y_val, title, xlabel)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_server_channels_messages(guild_id: int, amount: int = -1, days: int = -1):
    data = get_channels_messages(guild_id=guild_id, amount=amount, days=days)
    if data:
        x_val = [x[0] for x in data]
        y_val = [x[1] for x in data]

        title = f"Channels by total messages for last {days} days" if days > 0 else f"Channels by total messages"
        xlabel = "Messages"
        return generate_barh(x_val, y_val, title, xlabel)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def barh_user_channel_activity(guild_id, author_id, author_name):
    data = get_user_channel_activity(guild_id, author_id)
    if data:
        x_val = [x[0] for x in data]
        y_val = [x[1] for x in data]
        title = f"{author_name} messages by channel"
        xlabel = "Messages"
        return generate_barh(x_val, y_val, title, xlabel)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_server_growth_messages_days(guild_id, days):
    """

    """
    data = get_messages_growth_days(guild_id, days)
    if data:
        x_val = [x[0] for x in data]
        y_val = [x[1] for x in data]
        title = f"Messages per day for last {days} days" if days >= 1 else "Messages per day for all time"
        ylabel = "Messages"
        return generate_plot(x_val, y_val, title, ylabel, show_x=False if days == -1 else True)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def generate_plot(x, y, title, ylabel, show_x=True):
    plt.plot(x, y)
    plt.title(title)

    plt.ylabel(ylabel)

    if show_x:
        plt.xticks(rotation=60, fontsize=8)
    else:
        plt.xticks([])

    # Design
    plt.fill_between(x, y, color="blue", alpha=1)
    plt.tight_layout()

    return finish_plt(plt)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def generate_barh(x, y, title, xlabel) -> "Path to graph image":
    """Generate a horizontal bar chart from given values. Decreases copy
    pasting of boilerplate between similar functions."""
    # Set custom styling from library.
    # plt.style.use('grayscale')
    # Create horizontal bar chart.
    plt.barh(y, x, color="blue")
    fig = plt.gcf()

    # Add annotations.
    for i in range(len(y)):
        plt.annotate(x[i], xy=(1, y[i]))

    # TODO make it a func that somehow makes shit responsive
    if int(len(y)) >= 20:
        fig.set_figheight(int(len(y)) / 5)

    # Show values from highest to lowest in desc order.
    plt.gca().invert_yaxis()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.tight_layout()

    return finish_plt(plt)

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def finish_plt(plt: plt) -> "path to plot in mem":
    """Saves plot in memory and returns location to caller."""
    # Save plot in memory.
    graph_location = io.BytesIO()
    plt.savefig(graph_location, format="png")
    # Close figure to reset settings!
    plt.close()
    graph_location.seek(0)
    return graph_location

<<<<<<< HEAD

=======
>>>>>>> a7bb1b60ec419f897e1495a811aec29579830000
@timer
def plot_message_hour_weekday_heatmap(guild_id: int, channel_id: int = None, user_id: int = None):
    data = db.get_message_hour_weekday_heatmap(guild_id=guild_id, channel_id=channel_id, user_id=user_id)
    z = []
    for i in range(0, 24):
        tmp = []
        for tuple in data:
            if int(tuple[0]) == i: tmp.append(int(tuple[2]))
        z.append(tmp)
    print(z)
    return data


if __name__ == "__main__":
    # Values for manual testing :|
    terminalas_gid = 686598539136073780
    general_cid = 686598539677270168
    my_uid = 656942502498271275

    z = plot_message_hour_weekday_heatmap(guild_id=terminalas_gid)

    plt.matshow(z)
    plt.show()