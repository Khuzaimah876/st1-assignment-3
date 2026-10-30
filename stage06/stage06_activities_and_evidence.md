# Stage 6 activities and evidence

Complete this one group record. Link actual issues, diffs, tests and reviews; avoid copying entire histories. Blank fields are intentional. Duplicate rows as needed. Use synthetic data only. Every member records their own meaningful contribution. Do not invent results, reviews or Copilot use.

- Group/tutorial: [FILL tutorial day/time and group name]
- Members, GitHub usernames and cohorts: Aditya Vungarala (u3321194, UG); Khuzaimah (Khuzaimah876, [FILL cohort]); Manit Mahajan (CEOOFINDIA, [FILL cohort])
- Repository URL: https://github.com/Khuzaimah876/st1-assignment-3
- Starting SHA: 93c299639fddc887cb9be7e6663b0e5abad2be33 (baseline: `python3 -m pytest` in `project/` → 8 passed)

## A Requirement to issue activities

### FR-02 Patient Search

- Title: FR-02 Patient Search by ID
- Context: The clinic needs a reliable way to locate patient records by patient ID. Staff must quickly retrieve the correct record when managing appointments and patient information; without it, finding records is slow and error-prone.
- Requirement: FR-02 – Find a patient by patient ID and return the stored patient record when the ID exists.
- Acceptance criteria: A valid existing ID returns the actual stored Patient object (same object, no replacement). An unknown valid ID raises LookupError. A blank or invalid ID raises ValueError. IDs are trimmed and case-sensitive (' P1 ' finds P1; 'p1' does not).
- Scope: Included — lookup by patient ID, using the store's existing ID validation, LookupError/ValueError handling, unit tests. Excluded — creating, updating or deleting patients; searching by name or other attributes.
- Definition of Done: find_patient() meets every acceptance criterion; tests covering each criterion pass alongside the 8 supplied tests; another member reviewed the actual diff and approved; feedback resolved; merged to main and verified on main.
- Owner: u3321194
- Actual issue link: https://github.com/Khuzaimah876/st1-assignment-3/issues/1

### FR-06 Appointment Cancellation with FR-07 retained history

- Title: FR-06 Appointment Cancellation with FR-07 Retained History
- Context: The clinic needs a reliable way to cancel appointments while keeping an accurate history. Staff must be able to cancel scheduled appointments without losing records, so cancellations remain visible and traceable during the current session.
- Requirement: FR-06 – Only a SCHEDULED appointment can be cancelled. FR-07 – Cancellation retains the same appointment record with status CANCELLED, and it remains retrievable.
- Acceptance criteria: Cancelling a SCHEDULED appointment returns the same stored Appointment object with status CANCELLED. A cancelled appointment remains retrievable with CANCELLED status. Repeated cancellation raises ValueError and leaves state unchanged. Cancelling a COMPLETED appointment raises ValueError and leaves state unchanged. An unknown valid ID raises LookupError. A blank or invalid ID raises ValueError. Cancellation does not delete or replace the appointment object.
- Scope: Included — cancel_appointment(), lookup of the stored appointment before cancelling, domain-owned transition rules, retained history, unit tests for outcomes and errors. Excluded — deleting, rescheduling or completing appointments; changes to patient or practitioner records; unrelated booking features.
- Definition of Done: cancel_appointment() meets every acceptance criterion; tests covering each criterion pass alongside existing tests; another member reviews the actual diff and approves; feedback addressed; merged to main and verified on main.
- Owner: u3321194
- Actual issue link: https://github.com/Khuzaimah876/st1-assignment-3/issues/3

## B Commit quality

| Original example | Strong or Weak | Reason |
|---|---|---|
| changes | Weak | Vague; does not describe what was changed or why. |
| final version | Weak | Describes a stage of work rather than the actual change made. |
| Add patient search by ID | Strong | Names the specific feature added, in the imperative. |
| fix stuff | Weak | Too generic; a reviewer cannot tell what was fixed. |
| Prevent cancellation of completed appointments | Strong | Describes a specific behavioural change in the system. |

## C Over scoped PR review

A cancellation PR also renames unrelated patient fields, restructures unrelated code and adds a new dependency.

- Scope concerns: The PR mixes appointment cancellation with unrelated changes — renaming patient fields, restructuring unrelated code and adding a dependency. This makes review harder because reviewers must assess several independent changes at once, and it becomes difficult to revert only the cancellation work if another change causes problems.
- Responsibility and architecture concerns: Renaming patient fields affects a different part of the system and is unrelated to appointment cancellation. Adding a new dependency is outside the scope of FR-06 and FR-07 and conflicts with the A3 constraint that the application needs only the standard library; it also adds maintenance and compatibility risk without supporting the requirement.
- Testing and review concerns: Passing tests only show that the tested behaviour currently works; they do not prove that unrelated renames or restructuring are safe. Reviewers would need separate evidence and tests for those changes because they affect different responsibilities and may introduce hidden regressions.
- Changes to remove or separate, with reasons: Keep only the cancellation implementation and its directly related tests in this PR. Move the patient-field renames, code restructuring and dependency addition into separate PRs (or remove the dependency) so each change can be reviewed, tested and reverted independently.

## D Challenge a weak Copilot review

GitHub Copilot says: "Looks good; tests pass."

- Missing evidence: The review gives a conclusion with no evidence. It does not state which requirements or acceptance criteria were checked, which tests passed, whether test output was actually seen, which parts of the diff were examined, or what risks were considered.
- Follow-up review question 1: Which FR-06 and FR-07 acceptance criteria did you check, and where in the diff is the evidence for each one?
- Follow-up review question 2: Show the specific test cases that support your conclusion and explain which requirement each test covers.
- Follow-up review question 3: How does the review know the tests passed, and what test output was actually observed?
- Follow-up review question 4: What about behaviour implemented outside the diff, such as code in domain.py or data_store.py that was not visible during the review?
- Follow-up review question 5: Which risks, missing tests or responsibility-boundary issues did you consider before concluding the PR looked good?
- Additional questions if useful: Show the exact diff lines that prove the same object is returned after lookup or cancellation. How does the review distinguish verified evidence from assumptions? What unrelated changes, if any, were found? Were any acceptance criteria left unverified because the required code was outside the diff?

## E Team workflow agreement

| Practice | Team agreement |
|---|---|
| Branch naming | `feature/<requirement-id>-<short-topic>`, e.g. `feature/fr02-fr03-lookups`, `feature/fr06-fr07-cancel` |
| Commit message convention | Imperative, describes the behaviour or test intention, e.g. "Implement patient and practitioner lookup with tests" |
| PR size | One issue/requirement group per PR, small enough for one member to review the full diff |
| Another-member review requirement | A different member reviews the actual diff and approves on GitHub; self-review does not count |
| Merge rule | Merge only after tests pass in `project/`, review feedback is resolved and another member has approved |
| Significant Copilot disclosure rule | Disclose significant AI assistance in the PR description and record it in Section H with decision and verification |

## F Issue and backlog index

Create at least two focused issues. Add a linked practitioner-lookup issue or an explicit supporting criterion with the tutor if needed to cover all three service targets.

| Issue link | Requirement | Owner | Acceptance criteria or precise link | Status |
|---|---|---|---|---|
| https://github.com/Khuzaimah876/st1-assignment-3/issues/1 | FR-02 Patient search by ID (AC-02.1, AC-02.2) | u3321194 | Known ID returns the stored Patient; unknown ID raises LookupError; blank/invalid ID raises ValueError; no replacement object | Closed by PR #4 |
| https://github.com/Khuzaimah876/st1-assignment-3/issues/2 | FR-03 supporting practitioner lookup | u3321194 | Known ID returns the stored Practitioner; unknown ID raises LookupError; blank/invalid ID raises ValueError; no replacement object | Closed by PR #4 |
| https://github.com/Khuzaimah876/st1-assignment-3/issues/3 | FR-06, FR-07 (AC-05.1, AC-05.2, AC-05.3) | u3321194 | Only SCHEDULED can be cancelled; same object returned with CANCELLED status and still retrievable; repeated/COMPLETED cancel raises ValueError with state unchanged; unknown ID LookupError; blank ID ValueError | Closed by PR #5 |

## G Pull request evidence

### PR #4

- PR link and title: https://github.com/Khuzaimah876/st1-assignment-3/pull/4 — Implement patient and practitioner lookup (FR-02, FR-03 support)
- Linked issue and requirement: #1 (FR-02), #2 (FR-03 supporting lookup)
- Feature branch: `feature/fr02-fr03-lookups`
- Changed behaviour: `PatientService.find_patient` and `PractitionerService.find_practitioner` return the actual stored object; unknown ID raises LookupError; blank/invalid ID raises ValueError via the store's `required_text` validation.
- Meaningful commits: 214f2c4 (lookups + tests), 819d04c (restore end-of-file newline after review), 7dc1ba5 (non-string ID tests after Copilot review)
- Test command, directory and observed result: `python3 -m pytest` in `project/` → 18 passed at 214f2c4; 20 passed at 7dc1ba5
- Another-member reviewer: CEOOFINDIA (Manit)
- Human observations recorded before Copilot: PR #4 review comments by CEOOFINDIA on `services.py` (LookupError path, same-object return, practitioner lookup, end-of-file newline) — https://github.com/Khuzaimah876/st1-assignment-3/pull/4
- Requirement, responsibilities, test assertions and unrelated-scope checks: Reviewer checked both lookups against #1/#2, confirmed blank-ID validation stays in the store, confirmed `is` assertions prove identity, and flagged one unrelated diff line (removed end-of-file newline).
- Key feedback: Restore the end-of-file newline so the diff contains only intended changes.
- Author response/change and verification: Restored newline in 819d04c; replied on the thread; tests still 18 passed.
- Reviewer recheck and approval: CEOOFINDIA approved PR #4 — https://github.com/Khuzaimah876/st1-assignment-3/pull/4
- Merge outcome and SHA: Merged into main as 3695b8f4c6a435d8b3762dfea325c5d6abdf07a9
- Significant Copilot assistance: Copilot used by the reviewer for the required review comparison (see H and I). Implementation drafted with help from an AI assistant and disclosed in the PR description.
- Linked issue closure: #1 and #2 closed on merge
- Each member updated main: u3321194 — pulled 3695b8f, 20 passed; [FILL Khuzaimah876]; [FILL CEOOFINDIA]
- Integrated verification after merge: `python3 -m pytest` in `project/` on main → 20 passed at 3695b8f4c6a435d8b3762dfea325c5d6abdf07a9

### PR #5

- PR link and title: https://github.com/Khuzaimah876/st1-assignment-3/pull/5 — Implement appointment cancellation with retained history (FR-06, FR-07)
- Linked issue and requirement: #3 (FR-06, FR-07)
- Feature branch: `feature/fr06-fr07-cancel`
- Changed behaviour: `AppointmentService.cancel_appointment` finds the stored appointment via `find_appointment`, calls the domain's guarded `Appointment.cancel()`, and returns the same object. No deletion or replacement, so history is retained.
- Meaningful commits: 88f7fbc (cancellation + tests), f34f77d (COMPLETED cannot be cancelled test), 95b02c7 (non-string ID cancellation test after Copilot review)
- Test command, directory and observed result: `python3 -m pytest` in `project/` → 26 passed at 88f7fbc; 27 at f34f77d; 28 at 95b02c7
- Another-member reviewer: CEOOFINDIA (Manit)
- Human observations recorded before Copilot: PR #5 review comments by CEOOFINDIA (reuse of find_appointment, domain guard, same-object return, COMPLETED state unchanged) — https://github.com/Khuzaimah876/st1-assignment-3/pull/5
- Requirement, responsibilities, test assertions and unrelated-scope checks: Reviewer confirmed the state rule stays in the domain object, the same object is returned and retained (FR-07), and the COMPLETED test asserts unchanged state.
- Key feedback: Copilot comparison raised a missing non-string ID test (see H).
- Author response/change and verification: Added the test in 95b02c7; 28 passed; summary comment posted on PR #5.
- Reviewer recheck and approval: CEOOFINDIA approved PR #5 — https://github.com/Khuzaimah876/st1-assignment-3/pull/5
- Merge outcome and SHA: Merged into main as f5911be02c79c1e05c98d2e838168fca573cb9da
- Significant Copilot assistance: Copilot used by the reviewer for the required review comparison (see H and I). Implementation drafted with help from an AI assistant (Claude) and disclosed in the PR description.
- Linked issue closure: #3 closed on merge
- Each member updated main: u3321194 — pulled f5911be, 28 passed; [FILL Khuzaimah876]; [FILL CEOOFINDIA]
- Integrated verification after merge: `python3 -m pytest` in `project/` on main → 28 passed at f5911be02c79c1e05c98d2e838168fca573cb9da

## H Copilot collaboration record

### H1 — PR #4 review

- Member and task: CEOOFINDIA — required Copilot review comparison for PR #4
- Prompt/purpose and relevant issue/diff: Stage 6 Part H review prompt with FR-02/FR-03 criteria and the PR #4 diff (https://github.com/Khuzaimah876/st1-assignment-3/pull/4.diff)
- Summary of output: Rated FR-02/FR-03 "partially supported". Raised: ValueError not visible in the service; no non-blank invalid-ID test; trimming not required; use a stub store; test file missing final newline; question whether P999/DR999 are valid IDs.
- Human check against actual code, requirements and tests: Checked data_store.py (`required_text` raises ValueError for blank IDs; store returns the stored object), the A3 baseline (IDs are trimmed, non-blank, case-sensitive) and the test results.
- Decision — Accept / Modify / Reject: Accept (non-blank invalid-ID test; test-file newline). Reject (service-level ValueError concern; trimming; stub store; P999/DR999 validity).
- Reason: Validation is correctly owned by the store; trimming is required by the baseline; identity must be tested against the real shared store; P999/DR999 are valid but absent IDs.
- Verification/evidence: Added `None`-ID tests in 7dc1ba5 → 20 passed; summary comment on PR #4.

### H2 — PR #5 review

- Member and task: CEOOFINDIA — required Copilot review comparison for PR #5
- Prompt/purpose and relevant issue/diff: Stage 6 Part H prompt with FR-06/FR-07 criteria and the PR #5 diff (https://github.com/Khuzaimah876/st1-assignment-3/pull/5.diff)
- Summary of output: FR-06 "partially demonstrated", FR-07 "largely demonstrated". Raised: retention depends on the store; no non-string ID test; correctness depends on find_appointment and the hidden Appointment.cancel(); rebooking test beyond FR-06/07; unused variable; other non-SCHEDULED states; lookup tests appearing in the diff.
- Human check against actual code, requirements and tests: Checked domain.py (`cancel()` raises ValueError unless SCHEDULED, only then sets CANCELLED), data_store.py (same object held and returned), the AppointmentStatus enum and the test results.
- Decision — Accept / Modify / Reject: Accept (non-string ID test). Modify (lookup tests in the diff are a reorganisation only — explained, no code change). Reject (retention, find_appointment dependency, hidden cancel logic, rebooking scope, unused variable, other states).
- Reason: Domain and store behaviour verified directly; rebooking checks BR-05/AC-04 conflict behaviour; the variable is used; only CANCELLED and COMPLETED exist and both are tested.
- Verification/evidence: Added the test in 95b02c7 → 28 passed; summary comment on PR #5.

## I Human versus Copilot review comparison

### PR #4

- Human reviewer noticed before consulting Copilot: LookupError for unknown IDs; same-object return; blank-ID validation delegated to the store; unrelated end-of-file newline change in services.py.
- Copilot noticed: No non-blank invalid-ID test; missing final newline in test_services.py; service relies on datastore validation.
- Overlap: Both confirmed the LookupError path and the delegation of blank-ID validation to the store.
- What did the human reviewer notice that Copilot did not: The services.py newline issue (fixed before Copilot ran) and that blank-ID ValueError comes from `required_text`, which Copilot could not see.
- What did Copilot identify that the human reviewer initially missed: The missing non-blank (non-string) invalid-ID test and the test-file newline.
- Unsupported or incorrect Copilot suggestion: Trimming "not required" (the baseline requires it); stub store (the contract needs the real stored object); P999/DR999 validity doubt.
- Human judgement accepted, modified or rejected, and why: Accepted the test gap and newline; rejected the rest with evidence from data_store.py and the baseline.
- Which evidence justified merge approval: Approval by CEOOFINDIA, feedback resolved in 819d04c and 7dc1ba5, 20 passed in `project/`.

### PR #5

- Human reviewer noticed before consulting Copilot: Reuse of find_appointment for ID errors; domain-owned guard; same-object return and retained history; COMPLETED state unchanged.
- Copilot noticed: Missing non-string ID cancellation test; reorganised lookup tests appearing in the diff; dependence on the store and domain for guarantees.
- Overlap: Both confirmed the service delegates the transition to the domain object and returns the same instance.
- What did the human reviewer notice that Copilot did not: That Appointment.cancel() and the store already enforce the rules — Copilot only saw the diff and marked these as unverified.
- What did Copilot identify that the human reviewer initially missed: The non-string ID cancellation case and the test-file reorganisation showing in the diff.
- Unsupported or incorrect Copilot suggestion: "Unused variable" (it is used); rebooking "beyond requirements" (covers BR-05); other non-SCHEDULED states (only two exist, both tested).
- Human judgement accepted, modified or rejected, and why: Accepted the test gap; modified (explained) the reorganisation; rejected the rest after checking domain.py and data_store.py.
- Which evidence justified merge approval: Approval by CEOOFINDIA, Copilot findings resolved in 95b02c7, 28 passed in `project/`.

## J Contributions

- Member: u3321194 (Aditya Vungarala)
- Implementation: Implemented PatientService.find_patient, PractitionerService.find_practitioner (PR #4) and AppointmentService.cancel_appointment (PR #5); AI assistance disclosed in the PRs.
- Testing: Created project/tests/test_services.py (20 Stage 6 tests); ran the full suite before each commit and after each merge (8 → 20 → 28 passed).
- Review: Responded to review feedback on PR #4 (newline fix 819d04c) and evaluated both Copilot reviews against domain.py, data_store.py and the A3 baseline (7dc1ba5, 95b02c7).
- Issue refinement: Created issues #1, #2 and #3 with requirement links and acceptance criteria.
- Design and responsibility discussion: Kept ID validation in the store and state rules in Appointment.cancel(); services only coordinate.
- Debugging or integration: Merged PR #4 and PR #5; verified main at 3695b8f and f5911be.
- Documentation or team support: Compiled this Stage 6 record and answered sections A, B, K and L.

- Member: CEOOFINDIA (Manit Mahajan)
- Implementation: Not applicable for Stage 6.
- Testing: [FILL — e.g. pulled main and ran the suite: result]
- Review: Reviewed and approved PR #4 and PR #5 using the actual diff, with line comments before consulting Copilot.
- Issue refinement: Not applicable.
- Design and responsibility discussion: Review comments on domain-owned cancellation and store-owned validation.
- Debugging or integration: Flagged the unrelated end-of-file newline change in PR #4.
- Documentation or team support: Ran the required Copilot review comparison for PR #4 and PR #5 and shared the outputs; answered sections C and D.

- Member: Khuzaimah876
- Implementation: Not applicable for Stage 6 (Stage 7 owner).
- Testing: [FILL — pulled main and ran the suite: result, or "not yet verified"]
- Review: Not applicable.
- Issue refinement: Not applicable.
- Design and responsibility discussion: Not applicable.
- Debugging or integration: Created the shared repository, uploaded the starter and added collaborators.
- Documentation or team support: Repository owner and setup.

## K Exit question

Why is a high commit count not necessarily evidence of strong contribution?

A high commit count does not necessarily mean someone made the strongest contribution. During Stage 6, Manit made no implementation commits but reviewed both PRs, identified the unintended newline change, and completed the required Copilot comparisons that led to additional test coverage. Contribution should be judged by the value of the work, not the number of commits, because counts can be inflated by splitting small changes into many commits.

## L Stage 6 formative questions

1. What is version control?

Version control records changes to a project over time so previous states can be viewed or restored. In Git, we could return to the starting baseline at commit 93c2996 if needed.

2. Why is a feature branch useful?

A feature branch lets work be developed and tested without affecting main. We used branches such as feature/fr06-fr07-cancel so changes could be reviewed before merging.

3. What makes a commit a good engineering commit?

A good commit has one clear purpose, is small enough to review, and has a meaningful message. For example, 819d04c only restored the end-of-file newline identified during review.

4. What is a pull request?

A pull request is a proposal to merge one branch into another. PR #4 provided the diff, discussion thread, review comments and approval before the code was merged.

5. What is the purpose of code review?

Code review finds defects, requirement mismatches and unintended changes before merge. In Stage 6, review caught the unrelated newline change and the Copilot comparison led to extra tests.

6. What does a Git diff show?

A diff shows exactly what changed between versions of files: added lines with + and removed lines with -, so reviewers can inspect changes before merging.

7. What is a Definition of Done?

A Definition of Done is the shared checklist for when work is complete. Ours required meeting all acceptance criteria, passing tests, another member's approval, resolved feedback, and merge and verification on main.

8. What is the appropriate role of GitHub Copilot in pull-request review?

Copilot can suggest possible risks, missing tests and requirement gaps, but only after the human reviewer has recorded their own observations. Its suggestions must be checked against the actual code, requirements and test results; it does not approve merges, and humans remain responsible for the decision.

9. Why should individual contribution not be judged only by commit count?

Commit counts measure activity, not impact. Review, testing, issue refinement and integration can contribute significantly to quality without producing many commits.

10. What is the Stage 6 engineering rule?

Update main, create a focused issue and branch, write code and tests, inspect the diff, make a meaningful commit and push, open a PR, get another member's human review, respond to feedback and retest, obtain approval, merge, then every member updates main and verifies the integrated result.

## M Completion and handover

- Starting SHA: 93c299639fddc887cb9be7e6663b0e5abad2be33
- Final Stage 6 code SHA: f5911be02c79c1e05c98d2e838168fca573cb9da
- Test command: `python3 -m pytest`
- Working directory: `project/`
- Observed result: 28 passed (8 supplied + 20 Stage 6)
- PR and another-member reviewer: PR #4 and PR #5, both reviewed and approved by CEOOFINDIA — https://github.com/Khuzaimah876/st1-assignment-3/pull/4, https://github.com/Khuzaimah876/st1-assignment-3/pull/5
- Unresolved issue or none: [FILL — none, or note any teammate who has not yet verified main]
- Stage 7 handover status: [ready for tutor checkpoint / unresolved work]
- Final submitted SHA if later than tested SHA: Evidence-only commits after f5911be update this record and README only; no code changed after the tested SHA.

- [ ] Three Stage 6 service targets completed and checked.
- [ ] Original supplied tests retained and passing.
- [ ] At least two focused issues link requirements and acceptance criteria.
- [ ] Feature work reviewed by another member using the actual diff.
- [ ] Human-first review and required Copilot comparison recorded.
- [ ] Feedback resolved and approval recorded before merge.
- [ ] Everyone pulled main and integrated checks passed.
- [ ] Required activities, quiz responses and contribution notes completed.
- [ ] Only synthetic data included; confidential peer material kept out.
- [ ] Tutor can trace a requirement through issue, code, tests, PR and checkpoint.

