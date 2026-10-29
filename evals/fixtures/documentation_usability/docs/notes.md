# Notes

## Detail 7

To pause new intake, use `lantern intake pause --queue QUEUE`. Already claimed
jobs continue. Resume with `lantern intake resume --queue QUEUE`.
The implementation entry point is `src/intake/control.py::pause_queue`.
These commands are reference syntax; execution has not been verified here.
