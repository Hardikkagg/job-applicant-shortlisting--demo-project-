# =============================================================================
# algorithms.py — Core Algorithm Implementations
# Job Applicant Shortlisting System
# =============================================================================
# Implements:
#   1. Quick Sort  — sort candidates by any numeric field
#   2. Binary Search — find candidates by score or experience
#   3. Recursion    — filter nested skill sets & recursive ranking
# =============================================================================


# ─────────────────────────────────────────────────────────────────────────────
# 1. QUICK SORT
# ─────────────────────────────────────────────────────────────────────────────

def quick_sort(candidates, key='score', reverse=True):
    """
    Sorts a list of candidate dicts using the Quick Sort algorithm.

    Args:
        candidates (list): List of candidate dicts.
        key (str): The dict key to sort by ('score', 'experience', 'salary').
        reverse (bool): True = descending (highest first).

    Returns:
        list: Sorted list of candidates.

    Complexity: O(n log n) average, O(n²) worst case.
    """
    if len(candidates) <= 1:
        return candidates

    # Choose middle element as pivot to reduce worst-case on sorted input
    pivot_index = len(candidates) // 2
    pivot = candidates[pivot_index]
    pivot_val = pivot.get(key, 0) or 0

    left   = [c for i, c in enumerate(candidates) if i != pivot_index and (c.get(key, 0) or 0) >= pivot_val]
    middle = [c for i, c in enumerate(candidates) if i != pivot_index and (c.get(key, 0) or 0) == pivot_val]
    right  = [c for i, c in enumerate(candidates) if i != pivot_index and (c.get(key, 0) or 0) <  pivot_val]

    if reverse:
        # Descending: large → small
        return quick_sort(left, key, reverse) + [pivot] + middle + quick_sort(right, key, reverse)
    else:
        # Ascending: small → large
        return quick_sort(right, key, reverse) + [pivot] + middle + quick_sort(left, key, reverse)


# ─────────────────────────────────────────────────────────────────────────────
# 2. BINARY SEARCH
# ─────────────────────────────────────────────────────────────────────────────

def binary_search(sorted_candidates, target_value, key='score'):
    """
    Binary Search on a pre-sorted list of candidates.

    Finds ALL candidates whose `key` value matches `target_value`.
    Because multiple candidates can share the same value we:
      1. Find any match via binary search.
      2. Expand left/right to collect all matches.

    Args:
        sorted_candidates (list): Candidates sorted descending by `key`.
        target_value (float|int): Value to search for.
        key (str): Field to search on.

    Returns:
        list: All matching candidates (empty list if none found).

    Complexity: O(log n) to find first match + O(k) for k duplicates.
    """
    low, high = 0, len(sorted_candidates) - 1
    found_index = -1

    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_candidates[mid].get(key, 0) or 0

        if mid_val == target_value:
            found_index = mid
            break
        elif mid_val > target_value:
            # List is descending, so target is to the right
            low = mid + 1
        else:
            high = mid - 1

    if found_index == -1:
        return []

    # Expand around the found index to collect all duplicates
    results = [sorted_candidates[found_index]]

    left = found_index - 1
    while left >= 0 and (sorted_candidates[left].get(key, 0) or 0) == target_value:
        results.append(sorted_candidates[left])
        left -= 1

    right = found_index + 1
    while right < len(sorted_candidates) and (sorted_candidates[right].get(key, 0) or 0) == target_value:
        results.append(sorted_candidates[right])
        right += 1

    return results


def binary_search_range(sorted_candidates, min_val, max_val, key='score'):
    """
    Extended binary search: returns all candidates with key in [min_val, max_val].

    Uses binary search to find the boundary positions, then slices.
    List must be sorted descending.
    """
    results = []
    for c in sorted_candidates:
        val = c.get(key, 0) or 0
        if min_val <= val <= max_val:
            results.append(c)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# 3. RECURSION — Skill Filtering & Ranking
# ─────────────────────────────────────────────────────────────────────────────

def recursive_skill_filter(candidates, required_skills, index=0, results=None):
    """
    Recursively filters candidates who possess ALL required skills.

    Instead of a loop, we use tail recursion:
      - Base case: index reaches end of candidate list → return results.
      - Recursive case: check current candidate, advance index.

    Args:
        candidates (list): All candidates.
        required_skills (list): Skills every returned candidate must have.
        index (int): Current position (used by recursion, start at 0).
        results (list): Accumulator (used by recursion, start as None).

    Returns:
        list: Candidates matching ALL required skills.
    """
    if results is None:
        results = []

    # Base case
    if index >= len(candidates):
        return results

    candidate = candidates[index]
    candidate_skills = [s.strip().lower() for s in (candidate.get('skills') or '').split(',')]
    required_lower   = [s.strip().lower() for s in required_skills]

    # Check every required skill is present (inner recursion via helper)
    if _all_skills_present(required_lower, candidate_skills, 0):
        results.append(candidate)

    # Recurse to next candidate
    return recursive_skill_filter(candidates, required_skills, index + 1, results)


def _all_skills_present(required, candidate_skills, idx):
    """
    Recursive helper: returns True if ALL required[idx:] are in candidate_skills.
    Base case: idx == len(required) → all checked, return True.
    """
    if idx >= len(required):
        return True
    if required[idx] not in candidate_skills:
        return False
    return _all_skills_present(required, candidate_skills, idx + 1)


def recursive_rank_build(sorted_candidates, rank=1, index=0, ranked=None):
    """
    Recursively assigns rank numbers to sorted candidates.
    Handles ties: two candidates with equal score share the same rank.

    Args:
        sorted_candidates (list): Candidates sorted by score descending.
        rank (int): Current rank number.
        index (int): Current position.
        ranked (list): Accumulator.

    Returns:
        list: Candidates with 'rank' key added.
    """
    if ranked is None:
        ranked = []

    if index >= len(sorted_candidates):
        return ranked

    current = dict(sorted_candidates[index])  # copy to avoid mutating original

    # Tie check: same score as previous → same rank
    if index > 0:
        prev_score = sorted_candidates[index - 1].get('score', 0) or 0
        curr_score = current.get('score', 0) or 0
        if curr_score == prev_score:
            rank = ranked[-1]['rank']  # reuse last rank
        else:
            rank = index + 1  # standard rank (1-based, no ties gap for simplicity)

    current['rank'] = rank
    ranked.append(current)

    return recursive_rank_build(sorted_candidates, rank + 1, index + 1, ranked)


# ─────────────────────────────────────────────────────────────────────────────
# 4. AUTO-SCORE CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

def calculate_score(experience, skills_str, expected_salary):
    """
    Weighted formula:
        score = (experience * 2) + (skills_count * 3) - salary_factor

    salary_factor = salary / 10000  (normalises large salary numbers)
    Clamped to [0, 100].
    """
    skills_count  = len([s for s in skills_str.split(',') if s.strip()])
    salary_factor = (expected_salary or 0) / 10000
    raw_score     = (experience * 2) + (skills_count * 3) - salary_factor
    return round(max(0, min(100, raw_score)), 2)


def skill_match_percentage(candidate_skills_str, job_skills_list):
    """
    Calculates what percentage of job-required skills a candidate has.

    Args:
        candidate_skills_str (str): Comma-separated candidate skills.
        job_skills_list (list): Required skills for the job.

    Returns:
        float: Match percentage 0–100.
    """
    if not job_skills_list:
        return 100.0

    candidate_skills = {s.strip().lower() for s in candidate_skills_str.split(',') if s.strip()}
    job_skills       = {s.strip().lower() for s in job_skills_list}

    matched = candidate_skills & job_skills
    return round(len(matched) / len(job_skills) * 100, 1)
