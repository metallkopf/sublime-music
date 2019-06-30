from typing import Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, GObject

from . import albums, artists, playlists, more, player_controls
from libremsonic.server import Server
from libremsonic.state_manager import ApplicationState


class MainWindow(Gtk.ApplicationWindow):
    """Defines the main window for LibremSonic."""
    __gsignals__ = {
        'song-clicked': (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
                         (str, object)),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(1100, 768)

        self.panels = {
            'Albums': albums.AlbumsPanel(),
            'Artists': artists.ArtistsPanel(),
            'Playlists': playlists.PlaylistsPanel(),
            'More': more.MorePanel(),
        }

        # Create the stack
        self.stack = self.create_stack(**self.panels)
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self.titlebar = self.create_headerbar(self.stack)
        self.set_titlebar(self.titlebar)

        self.player_controls = player_controls.PlayerControls()

        flowbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        flowbox.pack_start(self.stack, True, True, 0)
        flowbox.pack_start(self.player_controls, False, True, 0)
        self.add(flowbox)

    def update(self, state: ApplicationState):
        # Update the Connected to label on the popup menu.
        if state.config.current_server >= 0:
            server_name = state.config.servers[
                state.config.current_server].name
            self.connected_to_label.set_markup(
                f'<b>Connected to {server_name}</b>')
        else:
            self.connected_to_label.set_markup(
                f'<span style="italic">Not Connected to a Server</span>')

        active_panel = self.stack.get_visible_child()
        if hasattr(active_panel, 'update'):
            active_panel.update(state)

        self.player_controls.update(state)

    def on_song_clicked(self, panel, song, queue):
        self.emit('song-clicked', song, queue)

    def create_stack(self, **kwargs):
        stack = Gtk.Stack()
        for name, child in kwargs.items():
            child.connect('song-clicked', self.on_song_clicked)
            stack.add_titled(child, name.lower(), name)
        return stack

    def create_headerbar(self, stack):
        """
        Configure the header bar for the window.
        """
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = 'LibremSonic'

        # Search
        search = Gtk.SearchEntry()
        header.pack_start(search)

        # Stack switcher
        switcher = Gtk.StackSwitcher(stack=stack)
        header.set_custom_title(switcher)

        # Menu button
        button = Gtk.MenuButton()
        button.set_use_popover(True)
        button.set_popover(self.create_menu())
        button.connect('clicked', self.on_menu_click)

        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)

        header.pack_end(button)

        return header

    def create_menu(self):
        self.menu = Gtk.PopoverMenu()

        self.connected_to_label = Gtk.Label(name='connected-to-label')
        self.connected_to_label.set_markup(
            f'<span style="italic">Not Connected to a Server</span>')

        menu_items = [
            (None, self.connected_to_label),
            ('app.configure-servers', Gtk.ModelButton('Connect to Server')),
        ]

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        for name, item in menu_items:
            if name:
                item.set_action_name(name)
            vbox.pack_start(item, False, True, 10)
        self.menu.add(vbox)

        return self.menu

    # ========== Event Listeners ==========
    def on_menu_click(self, button):
        self.menu.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()
