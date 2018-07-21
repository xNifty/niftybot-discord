"""
logout.py
@author Ryan Malacina
@SnoringNinja - https://snoring.ninja

Handles logging the bot out of discord
"""

from sys import platform

from discord.ext import commands
from resources.config import ConfigLoader

if platform == "linux" or platform == "linux2":
    import dbus # will only be imported if on linux
elif platform == "win32":
    pass


class Logout:
    """
    Logout cog handles exiting discord and
    shutting down.

    TODO: check if running as a systemd service, and if so, shutdown correctly using dbus
    """
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = ConfigLoader().load_config_setting_int('BotSettings', 'owner_id')

    @staticmethod
    def systemd_logout(service_name):
            sysbus = dbus.SystemBus()
            systemd = sysbus.get_object('org.freedesktop.systemd1',
                                        '/org/freedesktop/systemd1')

            manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')

            # Okay, so we'll just print out the "Shutting down, bye!" message
            # before we run this or logout
            manager.StopUnit('{0}.service'.format(service_name), 'fail')
            print("SHUTDOWN: linux environment in use, using systemd")

    @commands.command(pass_context=True, no_pm=True)
    async def logout(self, ctx):
        """
        Logs the bot out.
        This can only be used by the bot owner.

        This will not work if they are using systemd to reboot the bot on shutdown or crash.
        We need to implement the systemd_shutdown function into this if they are using systemd to manage
        """
        user_id = ctx.message.author.id

        await self.bot.say("Shutting down, bye!")

        # Try to run systemd_logout, and if that fails run the normal logout method
        # The issue here is if they are using systemd but pass in the wrong service name it'll just reboot
        # after logging out - not really our problem though, they should correct that in the bot config and try again
        # Please note: this is hardcoded right now, but it should grab the service name from the bot config
        if int(user_id) == self.owner_id:
            try:
                await self.bot.logout()
                await self.systemd_logout("niftybot")
            except TypeError:
                print("SHUTDOWN: non-linux environment, skipping systemd check")
                await self.bot.logout()

        return


def setup(bot):
    """This makes it so we can actually use it."""
    bot.add_cog(Logout(bot))
