

subjects = {
    'cs':{
        'KS4':['1.1 System Architecture','1.2 Memory & Storage','1.3 Networks','1.4 Network Security',
               '1.5 System Software','1.6 ELCE','2.1 Algorithms','2.2 Programming fundamentals',
               '2.3 Producing Robust Programs','2.4 Boolean Logic','2.5 Languages and IDEs', '%', 'Rank'],
        'KS5':['1.1 IO & Storage', '1.2 Software & Development', '1.3 Exchanging Data','1.4 Datatypes & Algorithms', 
            '1.5 legal & moral issues', '2.1 Computation Thinking', '2.2 Problem Solving', '%', 'Rank']
    }
}


def analysis_table(data, ks, student, subject):
    # default returned structure if no row matches
    studentX_d = {
        'atopic1': 0,
        'atopic2': 0,
        'atopic3': 0,
        'atopic4': 0,
        'atopic5': 0,
        'atopic6': 0,
        'atopic7': 0,
        'atopic8': 0,
        'atopic9': 0,
        'atopic10': 0,
        'atopic11': 0,
        'aAv': 0,
        'aRank': 0,
    }

    keys = subjects.get(subject, {}).get(ks, [])
    if not keys or not data:
        return studentX_d

    def extract_value(row, key):
        if isinstance(row, dict):
            return row.get(key, 0)
        elif isinstance(row, (list, tuple)):
            try:
                # if key is an int-like string, try to convert; otherwise cannot map reliably
                return row[int(key)]
            except Exception:
                return 0
        return 0

    for row in data:
        # find exam id
        if isinstance(row, dict):
            exam_id_val = row.get('exam_ID') or row.get('exam_id') or row.get('examNo') or row.get('Exam ID')
        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]
        else:
            continue

        if exam_id_val is None:
            continue

        if str(exam_id_val) == str(student):
            # build the dict from keys safely
            studentX_d = {
                'atopic1': extract_value(row, keys[0]),
                'atopic2': extract_value(row, keys[1]),
                'atopic3': extract_value(row, keys[2]),
                'atopic4': extract_value(row, keys[3]),
                'atopic5': extract_value(row, keys[4]),
                'atopic6': extract_value(row, keys[5]),
                'atopic7': extract_value(row, keys[6]),
                'atopic8': extract_value(row, keys[7]),
                'atopic9': extract_value(row, keys[8]),
                'atopic10': extract_value(row, keys[9]),
                'atopic11': extract_value(row, keys[10]),
                'aAv': extract_value(row, keys[11]),
                'aRank': extract_value(row, keys[12]),
            }
            break

    return studentX_d

def weekly_tests_table(data, year, student, subject):
    table_d = []
    labels = []
    chart_data = []
    chart_rank = []

    keys = subjects.get(subject, {}).get(year, [])
    # debug: show what keys we expect for this subject/year
    print(f"[weekly_tests_table] year={year!r} subject={subject!r} keys={keys!r} rows={len(data) if data else 0}")

    if not keys or not data:
        print("[weekly_tests_table] no keys or data — returning empty")
        return table_d, labels, chart_data, chart_rank

    student_str = str(student).strip()
    print(f"[weekly_tests_table] matching student identifier: {student_str!r}")

    for idx, row in enumerate(data):
        exam_id_val = None
        class_val = None
        name_val = None
        if isinstance(row, dict):
            exam_id_val = row.get('exam_ID') or row.get('exam_id') or row.get('examNo') or row.get('Exam ID')
            class_val = row.get('class') or row.get('Class')
            name_val = row.get('name') or row.get('Name')
        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]

        # debug: show row id values
        print(f"[weekly_tests_table] row#{idx} exam_ID={exam_id_val!r} class={class_val!r} name={name_val!r}")

        if exam_id_val is None and class_val is None and name_val is None:
            continue

        matched = False
        try:
            if exam_id_val is not None and str(exam_id_val).strip() == student_str:
                matched = True
        except Exception:
            pass
        if not matched and class_val is not None and str(class_val).strip() == student_str:
            matched = True
        if not matched and name_val is not None and str(name_val).strip().lower() == student_str.lower():
            matched = True

        print(f"[weekly_tests_table] row#{idx} matched={matched}")

        if not matched:
            continue

        test_no = row.get('Test No') if isinstance(row, dict) else (row[1] if len(row) > 1 else None)
        total_val = row.get('Total') if isinstance(row, dict) else 0
        perc = row.get('%') if isinstance(row, dict) else 0
        rank_val = row.get('Rank') if isinstance(row, dict) else 0

        def _get_topic(r, k):
            try:
                return r.get(k, 0) if isinstance(r, dict) else 0
            except Exception:
                return 0

        rowd = {
            'testNO': test_no,
            'topic1': _get_topic(row, keys[0]) if len(keys) > 0 else 0,
            'topic2': _get_topic(row, keys[1]) if len(keys) > 1 else 0,
            'topic3': _get_topic(row, keys[2]) if len(keys) > 2 else 0,
            'topic4': _get_topic(row, keys[3]) if len(keys) > 3 else 0,
            'topic5': _get_topic(row, keys[4]) if len(keys) > 4 else 0,
            'topic6': _get_topic(row, keys[5]) if len(keys) > 5 else 0,
            'topic7': _get_topic(row, keys[6]) if len(keys) > 6 else 0,
            'topic8': _get_topic(row, keys[7]) if len(keys) > 7 else 0,
            'topic9': _get_topic(row, keys[8]) if len(keys) > 8 else 0,
            'topic10': _get_topic(row, keys[9]) if len(keys) > 9 else 0,
            'topic11': _get_topic(row, keys[10]) if len(keys) > 10 else 0,
            'total': f"{total_val}",
            'perc':f"{perc}",
            'rank': rank_val
        }

        labels.append(test_no)
        try:
            chart_data.append(float(total_val))
        except Exception:
            chart_data.append(0)
        chart_rank.append(rank_val)
        table_d.append(rowd)

    print(f"[weekly_tests_table] returning {len(table_d)} matched rows")
    return table_d, labels, chart_data, chart_rank

def mock_tests_table(data, year, student, subject):
    mock_table = []
    keys = subjects.get(subject, {}).get(year, [])
    if not keys or not data:
        return mock_table

    for row in data:
        if isinstance(row, dict):
            exam_id_val = row.get('exam_ID') or row.get('exam_id') or row.get('examNo') or row.get('Exam ID')
        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]
        else:
            continue

        if exam_id_val is None:
            continue

        if str(exam_id_val) == str(student):
            total_val = row.get('Total') if isinstance(row, dict) else 0
            mock_row = {
                'testName': row.get('Test Name', '') if isinstance(row, dict) else '',
                'topic1': row.get(keys[0], 0) if isinstance(row, dict) else 0,
                'topic2': row.get(keys[1], 0) if isinstance(row, dict) else 0,
                'topic3': row.get(keys[2], 0) if isinstance(row, dict) else 0,
                'topic4': row.get(keys[3], 0) if isinstance(row, dict) else 0,
                'topic5': row.get(keys[4], 0) if isinstance(row, dict) else 0,
                'topic6': row.get(keys[5], 0) if isinstance(row, dict) else 0,
                'topic7': row.get(keys[6], 0) if isinstance(row, dict) else 0,
                'topic8': row.get(keys[7], 0) if isinstance(row, dict) else 0,
                'topic9': row.get(keys[8], 0) if isinstance(row, dict) else 0,
                'topic10': row.get(keys[9], 0) if isinstance(row, dict) else 0,
                'topic11': row.get(keys[10], 0) if isinstance(row, dict) else 0,
                'total': f"{total_val}",
                'rank': row.get('Rank') if isinstance(row, dict) else 0
            }
            mock_table.append(mock_row)
    return mock_table