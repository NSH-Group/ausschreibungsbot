Generate connectors for open APIs/RSS: TED, UNGM, World Bank, ADB, AfDB.
- Implement fetch_<source>() functions returning normalized dicts
- Handle pagination, rate limits, retries
- Normalize fields: title, description, url, country, language, cpv, budget, deadline, published_at, external_id, source
- Write to Postgres via ORM repository
- Provide tests with recorded fixtures 