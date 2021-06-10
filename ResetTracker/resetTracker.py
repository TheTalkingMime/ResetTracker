try:
    import json

    import sys
    import time
    from datetime import datetime

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    from Sheets import *
    from Buffer import Buffer
    from multiprocessing import Process
    import asyncio
    import traceback

    # TO DO
    # Update raw data after every pause
    #
    loop = asyncio.get_event_loop()

    class Saves(FileSystemEventHandler):
        buffer = None
        sessionStart = None
        buffer_observer = None
        prev = None
        queue = []

        def on_created(self, event):
            if not event.is_directory:
                # print("not a directory")
                return
            # try:
            #     loop = asyncio.get_event_loop()
            #     print("Got loop")
            # except:
            #     loop = asyncio.new_event_loop()
            #     asyncio.set_event_loop(loop)
            #     print("made loop")
            loop.run_until_complete(self.file_created(event))
            # asyncio.run(self.file_created(event), debug=True)

        async def file_created(self, event):
            print("something's created")
            src_path = event.src_path

            if self.sessionStart == None:
                self.sessionStart = datetime.now()
            copy = None
            if self.buffer_observer != None:
                copy = self.buffer.getRun()
                print("Stopping old observers")
                self.buffer.stop()
                self.buffer_observer.stop()
                if self.buffer.stats.getRun()[0] != None:

                    # print(self.buffer.path)
                    await push_data(copy)
                    # new_queue = []
                    # for i in range(0, len(self.queue)):
                    #     try:
                    #         push_data(self.queue[i])
                    #     except:
                    #         print("failed to push", self.queue[i])
                    #         print("will try again next time")
                    #         new_queue.append(self.queue[i])
                    # self.queue = new_queue
                    print("Pushed")
                else:
                    print("First entry is empty... weird")
            else:
                print("I guess there was no buffer observer")

            self.buffer = Buffer()
            self.buffer_observer = Observer()
            self.buffer_observer.schedule(self.buffer, src_path, recursive=False)

            try:
                self.buffer_observer.start()
                print("New world created", src_path)
            except Exception as e:
                print("Failed to start observer")
                print(e)
                pass
            # time.sleep(1)
            # try:
            #     push_data(copy)
            # except:
            #     print("failed to push")

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

        # asyncio.set_event_loop(loop)
        loop.run_until_complete(setup())
        # loop.close()

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
