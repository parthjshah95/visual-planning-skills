# Plan: Add CSV export to the Reports page

**Goal:** Let a user download the report they are currently looking at as a CSV file, respecting the filters they have applied. Risk: low. Steps: 5.

## Background

The Reports page (`ReportsView.tsx`) renders a filtered table from `GET /api/reports/:id`.
Users have asked to pull the same rows into a spreadsheet. Today they copy-paste out of the
table, which loses columns and breaks on more than a screenful of rows.

## Approach

Add an **Export CSV** button next to the existing filter bar. When clicked, it calls a new
backend endpoint that runs the same query the table uses, serializes the rows to CSV, and
streams the file back with a `Content-Disposition: attachment` header so the browser downloads
it. The export must respect the currently active filters, so the frontend passes the same filter
query string it already builds for the table request.

## Implementation steps

1. **Backend — export endpoint.** Add `GET /api/reports/:id/export?format=csv` in
   `reports_controller.py`. Reuse `build_report_query(report_id, filters)` — the same function the
   table endpoint calls — so the exported rows always match the on-screen rows. Return a streaming
   response with `Content-Type: text/csv` and `Content-Disposition: attachment; filename=...`.
2. **Backend — CSV serializer.** Add `rows_to_csv(rows, columns)` in `reports/serializers.py`.
   Use the standard library `csv` module. Quote fields, handle commas and newlines inside values,
   and write a header row from the column labels.
3. **Frontend — the button.** Add an `ExportButton` to `ReportsView.tsx` beside the filter bar.
   On click, it hits the export URL with the current filter query string and lets the browser
   handle the download. Show a spinner while the request is in flight; disable the button on empty
   results.
4. **Filters parity.** The frontend already builds a `filters` query string for the table request
   in `useReportFilters()`. Pass the identical string to the export URL so the two never diverge.
5. **Tests.** Unit-test `rows_to_csv` (commas, quotes, newlines, empty set, unicode). Integration-test
   the endpoint (filtered vs unfiltered, correct headers, row count matches the table endpoint).

## Open decision — large reports

Most reports are a few hundred rows and stream in well under a second. A small number of reports
have tens of thousands of rows. Streaming a very large report synchronously risks holding the
request open long enough to hit the 30-second gateway timeout.

Three options were considered:

- **(A) Stream synchronously, with a row cap.** Export up to 50,000 rows in the request. Above that,
  return a clear message asking the user to narrow their filters. Simplest; ships now; covers every
  report we actually have today.
- **(B) Background job + emailed link.** For large reports, enqueue a job, generate the file
  asynchronously, store it, and email the user a download link. Robust for any size, but adds a queue,
  a worker, object storage, and an email template — none of which exist for this feature yet.
- **(C) Paginated client-side assembly.** The browser fetches pages and stitches the CSV together.
  Avoids the timeout but moves complexity into the client and breaks if the tab is closed mid-export.

**Recommendation: (A).** No report in production today exceeds the cap, so (B)'s machinery would sit
unused. The endpoint is written so a background path can be added later behind the same URL if real
usage ever crosses the cap — that is the seam. We build (A) now and revisit only if the "narrow your
filters" message actually starts firing.

## Dev verification

- Run the API locally. Open the Reports page, apply a filter, click **Export CSV**.
- Confirm the downloaded file opens in a spreadsheet, has a header row, and its row count matches
  the filtered table exactly.
- Re-run with no filter and confirm the full set exports.
- Check the row-cap path: point at a seeded 60,000-row report and confirm the "narrow your filters"
  message, not a timeout.

## Testing checklist

- [ ] `rows_to_csv` unit tests pass (commas, quotes, newlines, empty, unicode).
- [ ] Endpoint integration test: filtered export row count == table endpoint row count.
- [ ] Endpoint returns `text/csv` and an `attachment` filename.
- [ ] Over-cap request returns the guidance message, not a 500 or a timeout.
- [ ] Button disabled on empty results; spinner shows during the request.

## Deliberately not built

- **Background export + email link (option B).** Seam: the export endpoint URL is stable, so a large
  report can route to an async path later without changing the frontend. Signal to build it: the
  row-cap message starts appearing in logs for real users.
- **Other formats (XLSX, JSON).** Only CSV was asked for. The serializer is per-format, so adding one
  later is additive.
