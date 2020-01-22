import os

from clock_database import ClockDatabase
from clock_ui import ClockUI
from timeclock import TimeClock


def run():
    tc = TimeClock()
    tc.run(ClockDatabase("timekeeping.sqlite"), ClockUI(os.getcwd()))

if __name__ == "__main__":
    run()