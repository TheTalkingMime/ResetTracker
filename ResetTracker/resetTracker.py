from Sheets import initialize_session
import traceback

try:
    import json

    import sys
    import time
    from datetime import datetime

    import gspread
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    from Sheets import push_data
    from Buffer import Buffer

    # TO DO
    # Conditional Formatting on raw data
    # Update raw data after every pause
    #

    class Saves(FileSystemEventHandler):
        buffer = None
        sessionStart = None
        buffer_observer = None
        prev = None
        # queue = []

        def on_created(self, event):
            src_path = event.src_path

            if self.sessionStart == None:
                self.sessionStart = datetime.now()

            if self.buffer_observer != None:
                self.buffer.stop()
                self.buffer_observer.stop()
                if self.buffer.stats.getRun()[0] != None:
                    # print(self.buffer.path)
                    push_data(self.buffer.getRun())
                    # new_queue = []
                    # for i in range(0, len(self.queue)):
                    #     try:
                    #         push_data(self.queue[i])
                    #     except:
                    #         print("failed to push", self.queue[i])
                    #         print("will try again next time")
                    #         new_queue.append(self.queue[i])
                    # self.queue = new_queue

            self.buffer_observer = None

            if not event.is_directory:
                return
            print("New world created", src_path)

            self.buffer = Buffer()
            self.buffer_observer = Observer()
            self.buffer_observer.schedule(self.buffer, src_path, recursive=False)

            try:
                self.buffer_observer.start()
            except Exception as e:
                pass

        def getTotalTime(self):
            return (
                self.buffer.achievements.endTime - self.sessionStart
            ).total_seconds()

    if __name__ == "__main__":
        try:
            settings_file = open("settings.json")
            settings = json.load(settings_file)
            settings_file.close()
        except Exception as e:
            print(e)
            print(
                "Could not find settings.json, make sure you have the file in the same directory as the exe, and named exactly 'settings.json'"
            )
            wait = input("")

        path = settings["path"]
        event_handler = Saves()
        savesObserver = Observer()
        savesObserver.schedule(event_handler, path, recursive=False)

        while True:
            try:
                savesObserver.schedule(event_handler, settings["path"], recursive=False)
                savesObserver.start()
            except Exception as e:
                settings["path"] = input("Path to saves directory:")
                settings_file = open("settings.json", "w")
                json.dump(settings, settings_file)
                settings_file.close()
            else:
                break
        initialize_session()
        print("Tracking...")
        print("Type 'quit' when you are done")
        live = True

        try:
            while live:
                try:
                    val = input("")
                except:
                    val = ""
                if (val == "help") or (val == "?"):
                    print("there is literally one other command and it's quit")
                if (val == "stop") or (val == "quit"):
                    print("Stopping...")
                    try:
                        push_data(event_handler.buffer.getRun())
                    except:
                        pass
                    live = False
                time.sleep(1)

        finally:
            savesObserver.stop()
            savesObserver.join()


except Exception as e:
    print("Unexpected error please send to TheTalkingMime#4431 for help")
    traceback.print_exc()
    wait = input("")
