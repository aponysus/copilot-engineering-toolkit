# Reporting periods

All amounts in this fictional example are integer cents. Timestamps are integer
UTC seconds. A reporting period includes events at `start` and excludes events
at `end`: `[start, end)`. Adjacent periods must not double-count an event at their
shared boundary. Signed amounts are summed without rounding.
