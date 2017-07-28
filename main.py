# -*- coding: utf-8 -*-

# main.py
# @author Ryan Malacina
# @SnoringNinja - https://snoring.ninja
# Built on discord.py
# Above files not included
# 

# TODO : clean up everything

# Note : plugins are different than modules

import discord
import asyncio
import random

# Import the plugins folder
# TODO : config to enable / disable plugin files to be imported
import plugins

# Import the commands folder
# TODO : config to enable / disable command files to be imported
import commands

# this needs to be cleaned up
from resources import database
from resources.error import error_logging

from discord.ext import commands

import os
import sys

from commands.utils import checks

from resources.config import ConfigLoader

# Not sure we still need this
description = ConfigLoader().load_config_setting('BotSettings', 'description')

# Load the command prefix from the core yaml
command_prefix = ConfigLoader().load_config_setting('BotSettings', 'command_prefix')

# Load the bot token from the core yaml
bot_token = ConfigLoader().load_config_setting('BotSettings', 'bot_token')

# Set the game name from the core yaml
game_name = ConfigLoader().load_config_setting('BotSettings', 'game_name')

# load the database name from the core yaml
database_name = ConfigLoader().load_config_setting('BotSettings', 'sqlite')

# Create the plugin list, which is built from the core yaml file
extension_list = ConfigLoader().load_config_setting('BotSettings', 'enabled_plugins')

client = commands.Bot(command_prefix=command_prefix, description=description)

# processes messages and checks if a command
@client.event
async def on_message(message):
    await client.process_commands(message)

# discord.py on_ready -> print out a bunch of information when the bot launches
@client.event
async def on_ready():
    print('------')
    print('Logged in as {0}; Client ID: {1}'.format(str(client.user.name), str(client.user.id)))
    print('Command prefix is: {0}'.format(str(command_prefix)))
    print('Setting game to: {0}'.format(game_name))
    print('Loaded extensions: {0}'.format(extension_list))
    print('Database name: {0}'.format(database_name))
    await client.change_presence(game=discord.Game(name=game_name))
    print('------')

# discord.py on_member_join -> when a member joins a server, check if the server has a channel configured
# and if they have the member_join plugin enabled
@client.event
async def on_member_join(member):
    server = member.server
    await plugins.JoinLeaveHandler(client).welcomeUser(server.id, member, server)

@client.event
async def on_member_remove(member):
    server = member.server
    await plugins.JoinLeaveHandler(client).goodbyeUser(server.id, member)

if __name__ == "__main__":
    print('------')
    print('Connecting...')
    error_logging().create_directory()
    try:
        database.DatabaseHandler().connected_to_sqlite()
        print('Connection successful.')
        print('Testing select statement...')
        res = database.DatabaseHandler().selectOneResultParam("SELECT username FROM credit_bet WHERE id=?", (2, ))
        res2 = database.DatabaseHandler().test()
        print(res)
        print(res2)

        # @TODO : we need to load all plugins at launch, since per-server configs are going to control plugin access
        startup_extensions = []
        for plugin in extension_list.split():
            startup_extensions.append(plugin)

        for extension in startup_extensions:
            try:
                client.load_extension(extension)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))
        client.run(bot_token)
    except Exception as e:
        # TODO : log error for looking at later
        print('Startup error encountered.')
        print(e)
        print('Exception: {0}: {1}'.format(type(e).__name__, e))
        client.logout()
        sys.exit(0)
