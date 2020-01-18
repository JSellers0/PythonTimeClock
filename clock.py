from clock_database import ClockDatabase
from clock_ui import ClockUI
from TimeClock import TimeClock


def run():
    tc = TimeClock()
    tc.run(ClockDatabase("timekeeping.sqlite"), ClockUI())

if __name__ == "__main__":
    run()