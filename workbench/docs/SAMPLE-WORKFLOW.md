# Sample Workflow (Synthetic Only)

This walkthrough demonstrates the record flow; it performs no live search or network request.

1. Create an empty workspace:

   ```sh
   python3 manage.py bootstrap ./case-demo
   ```

2. Human defines a narrow question and bounds in `scope.json`. The demo question is: “Did fictional `shop-a.example.com` link to fictional `shop-b.example.com` in one made-up capture?” The scope excludes real targets and stops after that fictional capture.

3. A human registers each public source in `sources.csv`, including original URL/reference, observation time, capture method, page locator, source lineage, and limitations. Keep raw files outside the repository.

4. Record only direct observations in `observations.csv`. Example: “the fictional footer displayed a link to the fictional returns page.” Do not write “same operator” in the observation field.

5. Draft claims in `claims.jsonl` with existing observation IDs, contrary-evidence IDs, at least one alternative explanation, rationale, and qualitative confidence. An agent proposal remains `author_type: agent-proposal` and `state: proposed`.

6. A human may record a separate disposition in `reviews.csv` with reviewer name, time, rationale, and an allowed disposition. The prototype checks that these fields exist and are linked; it cannot authenticate the reviewer or prevent someone from editing the file.

7. Run:

   ```sh
   python3 manage.py validate ./case-demo
   python3 manage.py status ./case-demo --json
   ```

8. Write the final human-reviewed summary using `templates/report.md`. For this example, the observation may be reported as part of the fictional record, while common control remains low-confidence/unresolved. No fraud finding is supported.

The included `examples/synthetic/` workspace is already populated to show this structure. It is not a real-world observation and should never be fetched.
