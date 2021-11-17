#!/usr/bin/env python3
import os
from pygments import formatters, highlight, lexers
from pygments.util import ClassNotFound
import subprocess
import time
from simple_term_menu import TerminalMenu

GLOBAL_TOKEN = None
GLOBAL_URL = None

def list_files(directory="."):
    return (os.path.join(directory, file) for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file)) and file.endswith(".py") and not file.startswith("__"))

def highlight_file(filepath):
    with open(filepath, "r") as f:
        file_content = f.read()
    try:
        lexer = lexers.get_lexer_for_filename(filepath, stripnl=False, stripall=False)
    except ClassNotFound:
        lexer = lexers.get_lexer_by_name("text", stripnl=False, stripall=False)
    formatter = formatters.TerminalFormatter(bg="dark")  # dark or light
    highlighted_file_content = highlight(file_content, lexer, formatter)
    return highlighted_file_content

def show_preview(prompt):
  return f"Current Settings:\n\
  - url: {GLOBAL_URL}\n\
  - token: {GLOBAL_TOKEN}\n"

def main():
    global GLOBAL_TOKEN
    global GLOBAL_URL
    main_menu_entries = ["Set Cloud URL", "Set Script Token", "Run Example", "Quit"]

    main_menu_exit = False
    main_menu = TerminalMenu(
        menu_entries=main_menu_entries, 
        title="Example Scripts",
        preview_command=show_preview, 
        clear_screen=True,
        preview_size=0.75)

    cloud_menu_entries = ["app.majortom.cloud", "app.azure.majortom.cloud", "host.docker.internal:3001", "custom"]
    cloud_menu = TerminalMenu(
        menu_entries=cloud_menu_entries, 
        title="Example Scripts",
        preview_command=show_preview, 
        # clear_screen=True,
        preview_size=0.75)

    run_menu_entries = list(list_files("./python"))
    run_menu = TerminalMenu(
        menu_entries=run_menu_entries, 
        title="Select an Example to Run",
        preview_command=highlight_file, 
        clear_screen=True,
        preview_size=0.75)

    while not main_menu_exit:
        main_sel = main_menu.show()

        if main_sel == 0:
            cloud_menu_sel = cloud_menu.show()
            if cloud_menu_sel == len(cloud_menu_entries)-1:
              GLOBAL_URL = input("Cloud url: ")
            else:
              GLOBAL_URL = cloud_menu_entries[cloud_menu_sel]

        elif main_sel == 1:
            GLOBAL_TOKEN = input("Script Token: ")

        elif main_sel == 2:
            run_menu_sel = run_menu.show()
            if run_menu_sel is not None:
                selected_file = run_menu_entries[run_menu_sel]
                http = "--scheme=http" if "internal" in GLOBAL_URL else ""
                cmdline = f"python3 {selected_file} {GLOBAL_URL} {GLOBAL_TOKEN} {http}"
                print(cmdline)
                try:
                    proc = subprocess.run(args=[cmdline], shell=True)
                    time.sleep(2)
                except KeyboardInterrupt:
                    pass

        elif main_sel == 3:
            main_menu_exit = True

if __name__ == "__main__":
    main()