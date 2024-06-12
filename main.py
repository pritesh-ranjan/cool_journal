import atexit
import threading
from datetime import datetime
from time import sleep

import keyboard
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from database_utilities.db_utils import DBConnection
from nlp_utilities import NlpUtils

console = Console()
db_conn = DBConnection()

esc_pressed = False
in_special_mode = False



def detect_escape_key():
    global esc_pressed, in_special_mode
    while True:
        keyboard.wait('esc')
        if not in_special_mode:
            esc_pressed = True


def exit_method():
    try:
        db_conn.close_connection()
    except:
        console.print("error in db")
    finally:
        console.print("... Goodbye!", style="bold red")
    exit(0)


def main():
    global esc_pressed, in_special_mode
    set_up_interface()
    register_triggers()

    try:
        while True:
            if esc_pressed:
                special_commands()
            else:
                user_input = Prompt.ask(">>>")
                if user_input.strip():
                    db_conn.insert_new_entry(str(user_input).strip())
                    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    console.print(Text(f"--[{time_now}]", style="bold green"))
                else:
                    sleep(0.1)
    except EOFError:
        exit_method()


def set_up_interface():
    result = db_conn.load_last_entry()
    today_str = datetime.today().date().strftime('%Y-%m-%d')
    if not result:
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(
            Panel(f"[bold green]{time_now}[/bold green]",
                  title="Welcome!!", border_style="yellow"))
    elif result[6] == 0 and result[0] == today_str:
        console.print(Panel(f"[bold yellow]Recovered entry from the last session.[/bold yellow]\n\n{result[5]}",
                            title=f"Recovered Entry @ {result[1]}", border_style="yellow"))
    else:
        nlp_utilities = NlpUtils(result[5])
        sentiment, score = nlp_utilities.emotional_analysis()
        summary = nlp_utilities.summarize()
        title = nlp_utilities.generate_title()
        db_conn.insert_new_entry(result[5], title, summary, sentiment)
        feedback_panel = Panel(
            f"[bold magenta]Date:[/bold magenta] {result[1]}\n\n"
            f"[bold magenta]Date:[/bold magenta] {title}\n\n"
            f"[bold magenta]Content:[/bold magenta]\n{result[5]}"
            f"[bold magenta]Sentiment:[/bold magenta] {sentiment} (score: {score:.2f})\n\n",
            title="Last Journal Entry Analysis",
            border_style="cyan"
        )
        console.print(feedback_panel)


def special_commands():
    global esc_pressed, in_special_mode
    in_special_mode = True
    menu_title = Text("Options Menu", style="bold green")
    menu_content = "\n".join(
        f"- {option}" for option in ["q- quit app", "c - cancel", "prev - show previous entry", "search"])
    console.print(Panel(menu_title + "\n" + menu_content))
    user_input = Prompt.ask(":")
    if user_input:
        if user_input == "q":
            exit_method()
        elif user_input == "c":
            return
        elif user_input == "prev":
            result = db_conn.load_last_entry()
            feedback_panel = Panel(
                f"Yesterday's entry @ {result[0]}"
                f"[bold magenta]Date:[/bold magenta] {result[1]}\n\n"
                f"[bold magenta]Date:[/bold magenta] {result[2]}\n\n"
                f"[bold magenta]Content:[/bold magenta]\n{result[5]}"
                f"[bold magenta]Sentiment:[/bold magenta] {result[4]}\n\n",
                title="Last Journal Entry Analysis",
                border_style="cyan"
            )
            console.print(feedback_panel)


def register_triggers():
    # keyboard.on_press_key("esc", lambda _: create_options_panel())
    threading.Thread(target=detect_escape_key, daemon=True).start()
    console.print("Press ESC to enter special commands mode.")
    # atexit.register(exit_method)


if __name__ == '__main__':
    main()
