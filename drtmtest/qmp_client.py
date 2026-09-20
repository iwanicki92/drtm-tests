# SPDX-FileCopyrightText: 2024 3mdeb <contact@3mdeb.com>
# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Adapted from Dasharo/open-source-firmware-validation's lib/QemuMonitor.py:
# https://github.com/Dasharo/open-source-firmware-validation
#
# The Robot Framework specific bits (the @library/@keyword decorators and
# robot.api.logger) were dropped since this project drives QEMU straight from
# pytest instead. The block-device hotplug keywords, not needed here, were
# dropped too.

import json
import logging
import socket

logger = logging.getLogger(__name__)


# Every socket operation is bounded by this. QEMU answers QMP in
# milliseconds when it answers at all, so a wait this long already means it
# is wedged, and blocking forever would hang the whole test session.
DEFAULT_TIMEOUT = 10.0


class QmpClient:
    """A minimal client for QEMU's QMP control socket."""

    def __init__(self, socket_path, timeout=DEFAULT_TIMEOUT):
        self.socket_path = socket_path
        self.timeout = timeout

    def _open(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect(self.socket_path)
        greeting = sock.recv(4096)
        logger.debug("QMP greeting: %r", greeting)
        return sock

    def _send_cmd(self, command, **args):
        sock = self._open()
        try:
            self._send(sock, "qmp_capabilities")
            response = self._send(sock, command, **args)
        finally:
            sock.close()
        if "error" in response:
            raise RuntimeError(
                f"QMP command '{command}' failed: {response['error']['desc']}"
            )
        return response

    def _send(self, sock, command, **args):
        msg = {"execute": command, "arguments": args}
        logger.debug("QMP command: %s", msg)
        sock.sendall(json.dumps(msg).encode())
        response = sock.recv(8192).decode()
        logger.debug("QMP response: %s", response)
        json_objects = [
            json.loads(line) for line in response.splitlines() if line.strip()
        ]
        if len(json_objects) > 1:
            return {"ack": json_objects[0], "event": json_objects[1]}
        return json_objects[0]

    def execute(self, command, **args):
        """Runs one command and returns its `return` value."""
        return self._send_cmd(command, **args)["return"]

    def human_monitor_command(self, command_line):
        return self._send_cmd("human-monitor-command", **{"command-line": command_line})

    def cont(self):
        return self._send_cmd("cont")

    def system_reset(self):
        return self._send_cmd("system_reset")

    def quit(self):
        return self._send_cmd("quit")
