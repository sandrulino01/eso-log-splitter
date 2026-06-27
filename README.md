## Credits
Based on [ESO Log Splitter](https://github.com/sea-unicorn/eso-log-splitter) by sea-unicorn, released under GPL-3.0.

### Changes from the original
- Each `ZONE_CHANGED` event now creates a separate log file, regardless of party composition
- All `ABILITY_INFO` and `EFFECT_INFO` definitions are collected from the entire log and prepended to every split file, making each file self-contained for parsers that require ability definitions to be present at the top of the log
