"""
Show (indeterminate) progress by animating ASCII chars on stdout.
"""

from itertools import cycle
from sys import stdout
from threading import Event
from threading import Thread
from time import sleep


_counter = 0


def _newname(template="Thread-{}"):
    """Generate a new thread name."""
    global _counter
    _counter += 1
    return template.format(_counter)


FRAMES = {
    'arrow':  ['^', '>', 'v', '<'],
    'dots': ['...', 'o..', '.o.', '..o'],
    'ligatures': ['bq', 'dp', 'qb', 'pd'],
    'lines': [' ', '-', '=', '#', '=', '-'],
    'slash':  ['-', '\\', '|', '/'],
}


class TextProgress(Thread):
    """Show progress for a long-running operation on the command-line."""

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        name = name or _newname("TextProgress-Thread-{}")
        style = kwargs.get('style', 'dots')
        super(TextProgress, self).__init__(
            group, target, name, args, kwargs)
        self.daemon = True
        self.cancelled = Event()
        self.frames = cycle(FRAMES[style])

    def run(self):
        """Write ASCII progress animation frames to stdout."""
        sleep(0.5)
        self._write_frame(self.frames.next(), erase=False)
        while not self.cancelled.is_set():
            sleep(0.4)
            self._write_frame(self.frames.next())
        # clear the animation
        self._write_frame(' ' * (len(self.frames.next())))

    def cancel(self):
        """Set the animation thread as cancelled."""
        self.cancelled.set()

    def _write_frame(self, frame, erase=True):
        if erase:
            backspaces = '\b' * (len(frame) + 2)
        else:
            backspaces = ''
        stdout.write("{} {} ".format(backspaces, frame))
        # flush stdout or we won't see the frame
        stdout.flush()


if __name__ == '__main__':
    # Run a 5-second demo of each style
    for style in sorted(FRAMES):
        stdout.write("\r{} ".format(style))
        stdout.flush()
        progress = TextProgress(kwargs={'style': style})
        progress.start()
        sleep(5)
        progress.cancel()
        sleep(0.2)
        stdout.write('\r                ')
    stdout.write('\n')
