from dearpygui import dearpygui as dpg

from conversion import converter, inverter

# ----------- Definitions (and theme) ------------
# In a dearpygui program it's nice when you don't have to
# dig for the tags and there meaning, so I thought I should provide them here:
#
# 1. "input"   : the input text box
# 2. "output"  : the output text box
# 3. "input_load_file_dialog" : the file dialog item for loading files into the input
# 4. "output_save_file_dialog" : the file dialog item for saving files from the output
# 5. "main_window" : the window in which it all happens, and also the primary window

SUPPORTED_EXTENSIONS = [
    ".py",
    ".tex",
]  # I wish it were possible to say 'all of them please', but alas.


def theme():
    with dpg.font_registry():
        default_font = dpg.add_font("RobotoMono-VariableFont_wght.ttf", 20)
        dpg.bind_font(default_font)

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            # this essentially applies a tokyo night theme
            # see: https://github.com/folke/tokyonight.nvim/blob/main/extras/ghostty/tokyonight_night
            dpg.add_theme_color(
                dpg.mvThemeCol_FrameBg,
                (40, 52, 87),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_WindowBg,
                (26, 27, 38),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_MenuBarBg, (40, 52, 87), category=dpg.mvThemeCat_Core
            )

            # adding rounding to windows frames and popups
            dpg.add_theme_style(
                dpg.mvStyleVar_WindowRounding, 5, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_PopupRounding, 5, category=dpg.mvThemeCat_Core
            )

    dpg.bind_theme(global_theme)


# -------------------- Errors --------------------


# currently errors are just print statements, but a popup would be neater
# hence why there is some styling in place already (in the theme function)
def throw_error(error_message: str) -> None:
    print(error_message)


# ------------------ Callbacks -------------------


def input_callback(_sender, app_data: str, _user_data) -> None:
    """Executes the conversion when the input text box is modified"""
    try:
        dpg.set_value("output", converter(app_data))
    except NotImplementedError:
        throw_error("Conversion operation not implemented.")
    except Exception as e:
        throw_error(f"Error in conversion function: \n{e}")  # probably in conversion...


def output_callback(_sender, app_data: str, _user_data) -> None:
    """Executes the inversion when the output text box is modified"""
    try:
        dpg.set_value("input", inverter(app_data))
    except NotImplementedError:
        throw_error("Inversion operation not implemented.")
    except Exception as e:
        throw_error(f"Error in inversion function: \n{e}")  # probably in inversion...


def viewport_resize_callback(*args, **kwargs) -> None:
    """Resizes the text boxes when the viewport is resized"""
    width = dpg.get_viewport_width() - 19
    height = dpg.get_viewport_height() // 2 - 23
    dpg.set_item_height("input", height)
    dpg.set_item_height("output", height)
    dpg.set_item_width("input", width)
    dpg.set_item_width("output", width)


def load_input_callback(_sender, app_data: dict, _user_data) -> None:
    """Loads a file to the input cell"""
    if len(app_data["selections"]) > 1:
        throw_error("Selecting multiple files is not supported.")
        return

    file_path = app_data["file_path_name"]
    with open(file_path, "r") as file:
        file_data = file.read()
    dpg.set_value("input", file_data)
    input_callback(None, file_data, None)


def save_output_callback(_sender, app_data: dict, _user_data) -> None:
    """
    Saves the output cell to a file.

    Notice: The `x` in the `open` function indicates you can't overwrite a file.
            I thought this might be sensible.
    """
    if len(app_data["selections"]) > 1:
        throw_error("Selecting multiple files is not supported.")
        return

    file_path = app_data["file_path_name"]
    with open(file_path, "x") as file:
        file.write(dpg.get_value("output"))


# ---------------- Declarations ------------------


def menubar():
    with dpg.menu_bar():
        with dpg.menu(label="Files"):
            with dpg.file_dialog(
                label="Open file",
                width=700,
                height=400,
                show=False,
                callback=lambda s, a, u: load_input_callback(s, a, u),
                tag="input_load_file_dialog",
            ) as load_input:
                for i in SUPPORTED_EXTENSIONS:
                    dpg.add_file_extension(i, color=(255, 255, 255, 255))
            dpg.add_menu_item(
                label="Open new file",
                callback=lambda s, a, u: dpg.show_item(load_input),
            )

            with dpg.file_dialog(
                label="Save file",
                width=700,
                height=400,
                show=False,
                callback=lambda s, a, u: save_output_callback(s, a, u),
                tag="output_save_file_dialog",
            ) as save_output:
                for i in SUPPORTED_EXTENSIONS:
                    dpg.add_file_extension(i, color=(255, 255, 255, 255))
            dpg.add_menu_item(
                label="Save output",
                callback=lambda s, a, u: dpg.show_item(save_output),
            )


def text_boxes():
    dpg.add_input_text(
        tag="input",
        multiline=True,
        default_value="input text",
        callback=input_callback,
        tab_input=True,
    )
    dpg.add_input_text(
        tag="output",
        multiline=True,
        default_value="output text",
        callback=output_callback,
        tab_input=True,
    )
    # because the text boxes don't initialize to the right size
    viewport_resize_callback()


def main():
    theme()
    with dpg.window(
        tag="main_window", label="Input to Output", menubar=True, no_scrollbar=True
    ):
        menubar()
        text_boxes()

    dpg.set_viewport_resize_callback(viewport_resize_callback)


if "__main__" in __name__:
    dpg.create_context()
    dpg.create_viewport(title="Text to Text", width=800, height=600)

    main()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
