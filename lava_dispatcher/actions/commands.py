# Copyright (C) 2017 Linaro Limited
#
# Author: Remi Duraffort <remi.duraffort@linaro.org>
#
# This file is part of LAVA Dispatcher.
#
# LAVA Dispatcher is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LAVA Dispatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along
# with this program; if not, see <http://www.gnu.org/licenses>.

from lava_dispatcher.action import Action
from lava_common.exceptions import ConfigurationError


class CommandAction(Action):

    compatibility = 1
    name = "user-command"
    description = "execute one of the commands listed by the admin"
    summary = "execute commands"

    def __init__(self):
        super().__init__()
        self.section = "command"
        self.cmd = None
        self.ran = False

    def validate(self):
        super().validate()
        cmd_name = self.parameters["name"]
        try:
            user_commands = self.job.device["commands"]["users"]
        except KeyError:
            raise ConfigurationError("Unable to get device.commands.users dictionary")

        try:
            self.cmd = user_commands[cmd_name]
            if not isinstance(self.cmd["do"], str) or not isinstance(
                self.cmd.get("undo", ""), str
            ):
                raise ConfigurationError(
                    'User command "%s" is invalid: '
                    "'do' and 'undo' should be strings" % cmd_name
                )
            return True
        except KeyError:
            self.errors = "Unknown user command '%s'" % cmd_name
            return False

    def run(self, connection, max_end_time):
        connection = super().run(connection, max_end_time)

        self.logger.info("Running user command '%s'", self.parameters["name"])
        self.ran = True
        self.run_cmd(self.cmd["do"])
        return connection

    def cleanup(self, connection):
        if not self.ran:
            self.logger.debug("Skipping %s 'undo' as 'do' was not called", self.name)
            return

        if self.cmd is not None and "undo" in self.cmd:
            self.logger.info(
                "Running cleanup for user command '%s'", self.parameters["name"]
            )
            self.run_cmd(self.cmd["undo"])
