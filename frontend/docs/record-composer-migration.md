# Record Composer Migration Note

Before this change, `LifeRecordView` and `PlazaView` each owned a separate record publishing form.

The new structure keeps one record source:

- `RecordComposer` owns record creation, visibility, media upload, and submit state.
- `LifeRecordView` uses it with private visibility by default and displays all records.
- `PlazaView` uses it with public visibility by default and refreshes the public plaza feed after public posts.
- Both flows submit through `createLifeRecord`.
