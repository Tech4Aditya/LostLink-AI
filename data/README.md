# Dataset workspace

Do not commit private user photos here.

Use the public datasets described in `docs/ML_DATASET.md` according to their individual licenses/terms.

For your own data, store metadata in `manifest.csv` and keep images in private storage.

Required fields:

```text
object_id
incident_id
report_type
image_path
description
category
color
location_id
event_time
match_group
is_positive
source
split
```

A physical object must never appear in both train and test.
