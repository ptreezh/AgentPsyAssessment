Title: Portable PsyAgent Per-Question Scoring and Trait Mapping Spec
Version: 1.0
Status: Proposed
Owner: Portable PsyAgent Team
Date: 2025-09-24

1. Executive Summary
- Goal: Produce per-question Big Five scores across 50 items, aggregate to final Big Five, and map to MBTI and Belbin roles, using two-question segments to fit context limits.
- Outcome: Deterministic JSON/MD outputs per file; robust evaluator pipeline; batch processing over results/results.

2. Scope
- In scope: Question extraction, 2-question segmentation, per-question Big Five scoring, aggregation to Big Five, MBTI mapping, Belbin role mapping, logs/artifacts.
- Out of scope: UI, cloud provider changes, data collection.

3. Constraints & Principles
- Pyramid principle: Clear top-line outputs; supporting analyses; details.
- KISS: Minimal modules, straightforward data flow.
- YAGNI: Only features to meet acceptance tests.
- SOLID: Single-responsibility for scoring, aggregation, and mapping.
- TDD: Write tests before implementation; green-only merges.

4. Inputs & Outputs
- Input: results/results/*.json assessment files containing questions and agent_response; variable schemas supported by existing extractors.
- Intermediate: Per-segment JSON: {"question_scores": [{question_id, dimension, big_five_scores:{trait:{score,evidence,quality}}}]}
- Final Outputs per input file:
  - <stem>_segmented_analysis.json: {
      "big_five": {trait:{score,raw_score,evidence_count,weight,evidence_quality,key_evidence}},
      "mbti": {type,confidence,big_five_basis},
      "belbin": {primary_role, secondary_role, rationale}
    }
  - Logs in logs/<stem>.log
  - Optional MD summary

5. Processing Pipeline
- Extract questions
- Segment into groups of 2 respecting max size
- For each segment: call evaluator; obtain question_scores JSON
- Accumulate question-level scores safely (range clamp 1..10; null→5 inferred)
- Aggregate to final Big Five (weighted mean)
- Map MBTI and Belbin
- Persist artifacts

6. Algorithms
6.1 Per-question scoring (LLM prompt contract)
- For each question, return scores for all five traits with evidence/quality in 1..10.
- Quality: direct|inferred.

6.2 Big Five aggregation
- Weighted mean across questions per trait; normalized to 1..10, one decimal.

6.3 MBTI mapping (from Big Five)
- E/I: extraversion vs (10−extraversion)+neuroticism/2 → preference E or I; confidence = |diff|/10.
- S/N: openness → N if openness>S score; confidence = |diff|/10.
- T/F: agreeableness → F if agreeableness>5 else T; confidence = |diff|/10.
- J/P: conscientiousness → J if conscientiousness>5 else P; confidence = |diff|/10.
- Type = concat(EI,SN,TF,JP). Overall confidence = mean of four.

6.4 Belbin role mapping (from Big Five; minimal deterministic rules)
- Roles: Plant(PL), Resource Investigator(RI), Coordinator(CO), Shaper(SH), Monitor Evaluator(ME), Teamworker(TW), Implementer(IMP), Completer Finisher(CF), Specialist(SP).
- Scoring vector R for each role using traits:
  - PL: high O, mid A, low C
  - RI: high E, high O
  - CO: high E, high A
  - SH: high E, low A, low N
  - ME: high C, low E, low N
  - TW: high A, mid E
  - IMP: high C, low O
  - CF: high C, high N (detail vigilance)
  - SP: mid C, mid O
- Compute role_score = wO*O + wC*C + wE*E + wA*A + wN*(10−N or N) per role; choose weights:
  - PL: O:0.5 A:0.2 C:-0.3
  - RI: E:0.5 O:0.4
  - CO: E:0.4 A:0.4
  - SH: E:0.4 A:-0.3 N:-0.2
  - ME: C:0.5 E:-0.3 N:-0.2
  - TW: A:0.5 E:0.2
  - IMP: C:0.5 O:-0.3
  - CF: C:0.4 N:0.3
  - SP: C:0.3 O:0.3
- Primary_role = argmax(role_score); Secondary_role = next-highest.
- Rationale: top contributing traits.

7. Acceptance Criteria (Contract)
- AC1: For any valid input, persist per-question scores for all 50 questions across segments.
- AC2: Final JSON contains Big Five with scores and metadata.
- AC3: MBTI type and confidence present; deterministic given Big Five.
- AC4: Belbin primary/secondary present; rationale includes trait contributions.
- AC5: Batch run over results/results completes without crashes; logs written per file.
- AC6: Lint passes (flake8 .); tests pass (pytest -q).

8. TDD Test Plan
- test_extract_questions_variants: supports all known schemas.
- test_segment_two_questions: segments size==2 and respects max_segment_size.
- test_llm_response_contract_mock: validate question_scores schema.
- test_accumulate_scores_nulls_and_ranges: clamps to 1..10; null→5 inferred.
- test_big_five_aggregation_weighted_mean: correct rounding and metadata.
- test_mbti_mapping_determinism: stable type for given inputs.
- test_belbin_mapping_selection: chooses expected role for synthetic Big Five vectors.
- test_persist_outputs: writes *_segmented_analysis.json and logs.
- test_batch_runner_results_dir: iterates results/results and completes.

9. Risks & Mitigations
- LLM JSON validity: enforce strict schema; retry or fail fast.
- Context size: segmentation + truncation safeguards.
- Data variability: extractor handles multiple formats.

10. Rollout
- Phase 1: Implement per-question persistence + tests.
- Phase 2: Add Belbin mapping + tests.
- Phase 3: Batch execution; verify artifacts.

11. Metrics
- Coverage of questions (should be 50/50).
- Error rate per file.
- Batch completion percentage.
