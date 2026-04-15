# =============================================================================
# app.py — Flask Application Entry Point
# Job Applicant Shortlisting System
# =============================================================================

from flask import Flask, request, jsonify, render_template, send_file
from models import init_db, add_candidate, get_all_candidates, delete_candidate, update_candidate, get_candidate_by_id
from algorithms import (
    quick_sort,
    binary_search,
    binary_search_range,
    recursive_skill_filter,
    recursive_rank_build,
    calculate_score,
    skill_match_percentage,
)
import io
import csv

app = Flask(__name__)

# Initialise database (create tables + seed demo data)
init_db()


# ─────────────────────────────────────────────────────────────────────────────
# FRONTEND ROUTE
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the main single-page dashboard."""
    return render_template('index.html')


# ─────────────────────────────────────────────────────────────────────────────
# API: Add Candidate
# POST /add_candidate
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/add_candidate', methods=['POST'])
def api_add_candidate():
    """
    Add a new candidate to the database.
    Accepts JSON body with fields:
        name, skills, experience, expected_salary, score (optional)
    Auto-calculates score if not provided.
    """
    data = request.get_json(force=True)

    name            = (data.get('name') or '').strip()
    skills          = (data.get('skills') or '').strip()
    experience      = float(data.get('experience') or 0)
    expected_salary = float(data.get('expected_salary') or 0)

    if not name or not skills:
        return jsonify({'success': False, 'error': 'Name and skills are required.'}), 400

    # Use provided score OR auto-calculate
    raw_score = data.get('score')
    if raw_score is None or raw_score == '':
        score = calculate_score(experience, skills, expected_salary)
    else:
        score = float(raw_score)

    new_id = add_candidate(name, skills, experience, expected_salary, score)
    return jsonify({'success': True, 'id': new_id, 'score': score}), 201


# ─────────────────────────────────────────────────────────────────────────────
# API: Get All Candidates
# GET /get_candidates
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/get_candidates', methods=['GET'])
def api_get_candidates():
    """
    Return all candidates, sorted by score descending by default.
    Applies recursive_rank_build to attach rank numbers.
    """
    candidates = get_all_candidates()
    # Sort by score descending (Quick Sort)
    sorted_candidates = quick_sort(candidates, key='score', reverse=True)
    # Attach rank numbers recursively
    ranked = recursive_rank_build(sorted_candidates)
    return jsonify({'success': True, 'candidates': ranked, 'count': len(ranked)})


# ─────────────────────────────────────────────────────────────────────────────
# API: Sort Candidates
# GET /sort_candidates?key=score&order=desc
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/sort_candidates', methods=['GET'])
def api_sort_candidates():
    """
    Sort all candidates using Quick Sort.

    Query params:
        key   : score | experience | expected_salary  (default: score)
        order : asc | desc                            (default: desc)
    """
    key   = request.args.get('key', 'score')
    order = request.args.get('order', 'desc')

    valid_keys = {'score', 'experience', 'expected_salary'}
    if key not in valid_keys:
        return jsonify({'success': False, 'error': f'Invalid key. Choose from: {valid_keys}'}), 400

    candidates = get_all_candidates()
    reverse    = (order.lower() == 'desc')
    sorted_c   = quick_sort(candidates, key=key, reverse=reverse)
    ranked     = recursive_rank_build(sorted_c)

    return jsonify({'success': True, 'candidates': ranked, 'sorted_by': key, 'order': order})


# ─────────────────────────────────────────────────────────────────────────────
# API: Search Candidate
# GET /search_candidate?field=score&value=85
#                      ?field=experience&value=5
#                      ?field=score&min=60&max=80   (range search)
#                      ?skill=Python                 (skill filter via recursion)
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/search_candidate', methods=['GET'])
def api_search_candidate():
    """
    Search candidates using Binary Search (numeric fields) or
    Recursive Skill Filter (skill field).
    """
    field = request.args.get('field', 'score')
    value = request.args.get('value')
    min_v = request.args.get('min')
    max_v = request.args.get('max')
    skill = request.args.get('skill')
    name  = request.args.get('name', '').strip().lower()

    candidates = get_all_candidates()

    # ── Skill search (recursive) ──────────────────────────────────────────
    if skill:
        required = [s.strip() for s in skill.split(',') if s.strip()]
        results  = recursive_skill_filter(candidates, required)
        return jsonify({'success': True, 'candidates': results, 'count': len(results), 'method': 'Recursive Skill Filter'})

    # ── Name search (linear, no algorithm constraint) ─────────────────────
    if name:
        results = [c for c in candidates if name in c.get('name', '').lower()]
        return jsonify({'success': True, 'candidates': results, 'count': len(results), 'method': 'Name Search'})

    # ── Binary search (numeric) ───────────────────────────────────────────
    valid_fields = {'score', 'experience', 'expected_salary'}
    if field not in valid_fields:
        return jsonify({'success': False, 'error': f'Invalid field. Choose from: {valid_fields}'}), 400

    # Pre-sort descending (required for our binary search implementation)
    sorted_c = quick_sort(candidates, key=field, reverse=True)

    if min_v is not None and max_v is not None:
        results = binary_search_range(sorted_c, float(min_v), float(max_v), key=field)
        method  = 'Binary Search (range)'
    elif value is not None:
        results = binary_search(sorted_c, float(value), key=field)
        method  = 'Binary Search (exact)'
    else:
        return jsonify({'success': False, 'error': 'Provide value or min+max params.'}), 400

    return jsonify({'success': True, 'candidates': results, 'count': len(results), 'method': method})


# ─────────────────────────────────────────────────────────────────────────────
# API: Shortlist Top N Candidates
# GET /shortlist_candidates?n=5&skill=Python
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/shortlist_candidates', methods=['GET'])
def api_shortlist():
    """
    Return the top N candidates by score.
    Optionally filter by required skills (recursive filter) before taking top N.

    Query params:
        n     : number of candidates to return (default 5)
        skill : comma-separated required skills (optional)
    """
    n     = int(request.args.get('n', 5))
    skill = request.args.get('skill', '')

    candidates = get_all_candidates()

    # Apply skill filter recursively if requested
    if skill:
        required   = [s.strip() for s in skill.split(',') if s.strip()]
        candidates = recursive_skill_filter(candidates, required)

    # Sort by score descending using Quick Sort
    sorted_c  = quick_sort(candidates, key='score', reverse=True)
    shortlist = sorted_c[:n]
    ranked    = recursive_rank_build(shortlist)

    return jsonify({'success': True, 'shortlist': ranked, 'count': len(ranked), 'requested_n': n})


# ─────────────────────────────────────────────────────────────────────────────
# API: Delete Candidate
# DELETE /delete_candidate/<id>
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/delete_candidate/<int:candidate_id>', methods=['DELETE'])
def api_delete_candidate(candidate_id):
    success = delete_candidate(candidate_id)
    if success:
        return jsonify({'success': True, 'message': f'Candidate {candidate_id} deleted.'})
    return jsonify({'success': False, 'error': 'Candidate not found.'}), 404


# ─────────────────────────────────────────────────────────────────────────────
# API: Update Candidate
# PUT /update_candidate/<id>
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/update_candidate/<int:candidate_id>', methods=['PUT'])
def api_update_candidate(candidate_id):
    data            = request.get_json(force=True)
    name            = (data.get('name') or '').strip()
    skills          = (data.get('skills') or '').strip()
    experience      = float(data.get('experience') or 0)
    expected_salary = float(data.get('expected_salary') or 0)
    raw_score       = data.get('score')

    if raw_score is None or raw_score == '':
        score = calculate_score(experience, skills, expected_salary)
    else:
        score = float(raw_score)

    success = update_candidate(candidate_id, name, skills, experience, expected_salary, score)
    if success:
        return jsonify({'success': True, 'score': score})
    return jsonify({'success': False, 'error': 'Candidate not found.'}), 404


# ─────────────────────────────────────────────────────────────────────────────
# API: Skill Match
# GET /skill_match/<id>?job_skills=Python,Django,REST
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/skill_match/<int:candidate_id>', methods=['GET'])
def api_skill_match(candidate_id):
    job_skills_str = request.args.get('job_skills', '')
    job_skills     = [s.strip() for s in job_skills_str.split(',') if s.strip()]
    candidate      = get_candidate_by_id(candidate_id)

    if not candidate:
        return jsonify({'success': False, 'error': 'Candidate not found.'}), 404

    pct = skill_match_percentage(candidate['skills'], job_skills)
    return jsonify({'success': True, 'match_percentage': pct, 'candidate': candidate})


# ─────────────────────────────────────────────────────────────────────────────
# API: Export to CSV
# GET /export_csv
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/export_csv', methods=['GET'])
def api_export_csv():
    """Export all candidates as a downloadable CSV file."""
    candidates = get_all_candidates()
    sorted_c   = quick_sort(candidates, key='score', reverse=True)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'name', 'skills', 'experience', 'expected_salary', 'score', 'created_at'])
    writer.writeheader()
    for c in sorted_c:
        writer.writerow(c)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='candidates.csv'
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
