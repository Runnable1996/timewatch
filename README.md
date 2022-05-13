
## timewatch

Tired of reporting work hours every day/month?
Your boss trusts you with your time, but HR demands you fill timewatch's form?
You're too preoccupied with work, and forget filling up timewatch.co.il?

We've all been there, just set up a monthly timewatch cron and get back to work!

### What is this?
This script automatically sets default working hours for all work days using timewatch.co.il's web interface.
It reads expected work hours for each day and automatically sets each day's work to that amount.
It is therefor handling govt. off days and weekends, and is quite configurable.

## Usage
To report required working hours for the current month, simply execute
```timewatch [OPTIONS] COMPANY_ID ID PASSWORD```

### Full usage and functionality

```
Usage: timewatch [OPTIONS] COMPANY_ID ID PASSWORD

Arguments:
  COMPANY_ID  [required]
  ID          [required]
  PASSWORD    [required]



Automatic work hours reporting for timewatch.co.il

positional arguments:
  COMPANY_ID               Company ID
  ID                  user name/id
  PASSWORD              user password

Options:
  -m, --month TEXT                [default: {{current month}}]
  -y, --year TEXT                 [default: {{current year}}]
  --help                          Show this message and exit.
```

### Installation

```
git clone https://github.com/Runnable1996/timewatch.git
cd timewatch
pip install .
```

### Known issues
* Doesn't sign the doc (I suggest you do it manually after reviewing there are no bugs in the report).
