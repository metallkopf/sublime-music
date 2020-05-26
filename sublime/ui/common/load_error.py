from gi.repository import Gtk


class LoadError(Gtk.Box):
    def __init__(
        self, entity_name: str, action: str, has_data: bool, offline_mode: bool
    ):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.pack_start(Gtk.Box(), True, True, 0)

        inner_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, name="load-error-box"
        )

        inner_box.pack_start(Gtk.Box(), True, True, 0)

        error_description_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        if offline_mode:
            icon_name = "cloud-offline-symbolic"
            label = f"{entity_name} may be incomplete.\n" if has_data else ""
            label += f"Go online to {action}."
        else:
            icon_name = "network-error-symbolic"
            label = f"Error attempting to {action}."

        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        image.set_name("load-error-image")
        error_description_box.add(image)

        error_description_box.add(
            Gtk.Label(
                label=label, justify=Gtk.Justification.CENTER, name="load-error-label"
            )
        )

        box = Gtk.Box()
        box.pack_start(Gtk.Box(), True, True, 0)

        if offline_mode:
            go_online_button = Gtk.Button(label="Go Online")
            go_online_button.set_action_name("app.go-online")
            box.add(go_online_button)
        else:
            retry_button = Gtk.Button(label="Retry")
            retry_button.set_action_name("app.refresh-window")
            box.add(retry_button)

        box.pack_start(Gtk.Box(), True, True, 0)
        error_description_box.add(box)

        inner_box.add(error_description_box)

        inner_box.pack_start(Gtk.Box(), True, True, 0)

        self.add(inner_box)

        self.pack_start(Gtk.Box(), True, True, 0)
