from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
import threading

from ptop.cpu import Cpu

cpu = Cpu()

root_container = HSplit(
    [
        Window(
            always_hide_cursor=True,
            content=FormattedTextControl(
                text=lambda: f"CPU: {cpu.used_percentage:.1f}% {cpu.temperature}°C"
            ),
        ),
        Window(height=1, char="─"),
        Window(content=FormattedTextControl(text="test2")),
    ]
)

layout = Layout(root_container)
kb = KeyBindings()


@kb.add("q")
def exit_(e):
    e.app.exit()


app = Application(key_bindings=kb, layout=layout, full_screen=True, refresh_interval=1)


def main():
    threading.Thread(target=cpu.poll, daemon=True).start()
    app.run()


if __name__ == "__main__":
    main()
