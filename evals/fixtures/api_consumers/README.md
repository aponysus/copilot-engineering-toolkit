# Item counts

`service.response` returns a JSON object with a required integer `count`.
`destinations` supplies the dashboard and, when `export_enabled` from
`settings.json` is true, the CSV exporter. The default configuration disables
export; some deployments enable it.

The fictional Archive Reader also consumes this payload nightly. Its source is
maintained in a separate repository and is not included here. Changes to the
wire contract must account for that consumer.
