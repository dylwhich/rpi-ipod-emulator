#!/usr/bin/env python3

# Dependencies:
# - python3-dbus
# - python3-gobject2

import sys
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
import serial
import time
from ipodproto.handlers.ipod import IpodProtocolHandler
from ipodproto import protocol

SERVICE_NAME = "org.bluez"
AGENT_IFACE = SERVICE_NAME + '.Agent1'
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
PLAYER_IFACE = SERVICE_NAME + '.MediaPlayer1'
TRANSPORT_IFACE = SERVICE_NAME + '.MediaTransport1'


class BluePlayer(IpodProtocolHandler):
    bus = None
    mainloop = None
    device = None
    deviceAlias = None
    player = None
    connected = None
    state = None
    _status =protocol.STATUS_STOP
    elapsed_info = (0, 0)
    track = []

    def __init__(self, *args, **kwargs):
        """Specify a signal handler, and find any connected media players"""
        super().__init__(*args, **kwargs)

        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.bus = dbus.SystemBus()

        self.bus.add_signal_receiver(self.player_handler,
                                     bus_name="org.bluez",
                                     dbus_interface="org.freedesktop.DBus.Properties",
                                     signal_name="PropertiesChanged",
                                     path_keyword="path")

        self.find_player()
        self.update_display()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value == "paused":
            self._status = protocol.STATUS_PAUSED

            # Update our elapsed info if it's now inaccurate
            if self.elapsed_info[1] != 0:
                self.elapsed_info = (self.get_elapsed_time(), 0)
        elif value == "playing":
            self._status = protocol.STATUS_PLAYING

            # Update our elapsed info if it's now inaccurate
            if self.elapsed_info[1] == 0:
                self.elapsed_info = (self.get_elapsed_time(), time.monotonic())
        elif value == "stopped":
            self._status = protocol.STATUS_STOP

            # Update our elapsed info if it's now inaccurate
            if self.elapsed_info[1] != 0:
                self.elapsed_info = (self.get_elapsed_time(), 0)
        elif value in (protocol.STATUS_PAUSED, protocol.STATUS_PLAYING, protocol.STATUS_STOP):
            self._status = value
        else:
            raise ValueError("Invalid status")

    def start(self):
        """Start the BluePlayer by running the gobject Mainloop()"""
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def end(self):
        """Stop the gobject Mainloop()"""
        if self.mainloop:
            self.mainloop.quit();

    def stop(self):
        super().stop()
        self.end()

    def find_player(self):
        """Find any current media players and associated device"""
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        player_path = None
        for path, interfaces in objects.items():
            if PLAYER_IFACE in interfaces:
                player_path = path
                break

        if player_path:
            self.connected = True
            self.get_player(player_path)
            player_properties = self.player.GetAll(PLAYER_IFACE, dbus_interface="org.freedesktop.DBus.Properties")

            for prop in player_properties:
                self.on_property_changed(prop, player_properties[prop])

    def get_player(self, path):
        """Get a media player from a dbus path, and the associated device"""
        self.player = self.bus.get_object("org.bluez", path)
        device_path = self.player.Get("org.bluez.MediaPlayer1", "Device",
                                      dbus_interface="org.freedesktop.DBus.Properties")
        self.get_device(device_path)

    def get_device(self, path):
        """Get a device from a dbus path"""
        self.device = self.bus.get_object("org.bluez", path)
        self.deviceAlias = self.device.Get(DEVICE_IFACE, "Alias", dbus_interface="org.freedesktop.DBus.Properties")

    def player_handler(self, interface, changed, invalidated, path):
        """Handle relevant property change signals"""
        iface = interface[interface.rfind(".") + 1:]
        #        print("Interface: {}; changed: {}".format(iface, changed))

        print(changed)

        if iface == "Device1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
        elif iface == "MediaControl1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
                if changed["Connected"]:
                    self.find_player()
        elif iface == "MediaPlayer1":
            for prop in changed:
                self.on_property_changed(prop, changed[prop])
            if "Track" in changed:
                self.track = changed["Track"]
                self.update_display()
            if "Status" in changed:
                self.status = changed["Status"]

    def on_property_changed(self, property, value):
        if property == "Track":
            self.track = value
        elif property == "Status":
            self.status = value
        elif property == "Position":
            if self.status == protocol.STATUS_PLAYING:
                self.elapsed_info = (value, time.monotonic())
            else:
                self.status = (value, 0)

    def update_display(self):
        if self.player:
            print(dir(self.player))
            if "Artist" in self.track:
                print(self.track["Artist"])
            if "Title" in self.track:
                print(self.track["Title"])
        else:
            print("Waiting for media player")

    def get_current_track_length(self):
        return self.track["Duration"] if self.track else 0

    def get_elapsed_time(self):
        last_elapsed, at = self.elapsed_info
        if at == 0:
            # when at is 0, last_elapsed is accurate (e.g. when we are paused)
            return int(last_elapsed)
        else:
            # Otherwise, we have to extrapolate
            return int(last_elapsed + time.monotonic() - at)

    def fast_forward(self):
        self.player.FastForward(dbus_interface=PLAYER_IFACE)

    def rewind(self):
        self.player.Rewind(dbus_interface=PLAYER_IFACE)

    def stop_ff_rw(self):
        self.play()

    def next(self):
        self.player.Next(dbus_interface=PLAYER_IFACE)

    def previous(self):
        self.player.Previous(dbus_interface=PLAYER_IFACE)

    def play(self):
        self.player.Play(dbus_interface=PLAYER_IFACE)

    def pause(self):
        self.player.Pause(dbus_interface=PLAYER_IFACE)

    def play_pause(self):
        if self.status == "playing":
            self.pause()
        elif self.status == "paused" or self.status == "idle":
            self.play()

    def repeat(self):
        if self.repeat:
            pass
