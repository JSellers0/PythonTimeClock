import os

from timeclock.clock_database import ClockDatabase
from timeclock.clock_ui import ClockUI
from timeclock.timeclock import TimeClock


def run():
    tc = TimeClock()
    tc.run(ClockDatabase("timekeeping.sqlite"), ClockUI(os.getcwd()))

if __name__ == "__main__":
    run()