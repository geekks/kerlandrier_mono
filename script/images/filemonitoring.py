'''
Script to check for new images to send them to Mistral script
Should be used with Docker
'''
import time, sys
import os

from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
from watchdog.observers import Observer
from mistral_images import getMistralImageEvent, postMistralEventToOa

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example log message
logger.info("Application started")
current_path = os.getcwd()
logger.info(f"Current working directory: {current_path}")

src_path = sys.argv[1] if len(sys.argv) > 1 else '.'
class CreatedHandler(FileSystemEventHandler):
    def on_created (self, event: FileCreatedEvent| FileMovedEvent) -> None:
        logger.info(event.event_type)
        logger.info(event.src_path)
        if ".crdownload" in event.src_path:
            logger.info("waiting for download to finish")
            time.sleep(1)
            return
        try:
            event = getMistralImageEvent(event.src_path)
        except Exception as e:
            logger.exception(e)
            return
        postMistralEventToOa(event)

event_handler = CreatedHandler()
observer = Observer()

observer.schedule(event_handler, src_path, recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()