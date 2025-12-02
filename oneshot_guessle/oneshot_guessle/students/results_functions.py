

subjects = {
    'cs':{
        'KS4':['1. Algorithms', '2. Programming', '3. Computer Systems', '4. Data rep', '5. Security', '6. Networks',
            '7. ethics & Leg', '%', 'Rank'],
        'KS5':['1.1 IO & Storage', '1.2 Software & Development', '1.3 Exchanging Data','1.4 Datatypes & Algorithms', 
            '1.5 legal & moral issues', '2.1 Computation Thinking', '2.2 Problem Solving', '%', 'Rank']
    }
}


def analysis_table(data, year, student, subject):
    # default returned structure if no row matches
    studentX_d = {
        'atopic1': 0,
        'atopic2': 0,
        'atopic3': 0,
        'atopic4': 0,
        'atopic5': 0,
        'atopic6': 0,
        'atopic7': 0,
        'aAv': 0,
        'aRank': 0,
    }

    keys = subjects.get(subject, {}).get(year, [])
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
                'aAv': extract_value(row, keys[7]),
                'aRank': extract_value(row, keys[8]),
            }
            break

    return studentX_d

def weekly_tests_table(data, year, student, subject):
    table_d = []
    labels = []
    chart_data = []
    chart_rank = []

    keys = subjects.get(subject, {}).get(year, [])
    if not keys or not data:
        return table_d, labels, chart_data, chart_rank

    for row in data:
        # resolve exam id
        if isinstance(row, dict):
            exam_id_val = row.get('exam_ID') or row.get('exam_id') or row.get('examNo') or row.get('Exam ID')
        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]
        else:
            continue

        if exam_id_val is None:
            continue

        if str(exam_id_val) == str(student):
            test_no = row.get('Test No') if isinstance(row, dict) else (row[1] if len(row) > 1 else None)
            total_val = row.get(keys[7], 0) if isinstance(row, dict) else 0
            rank_val = row.get(keys[8], 0) if isinstance(row, dict) else 0

            rowd = {
                'testNO': test_no,
                'topic1': row.get(keys[0], 0) if isinstance(row, dict) else 0,
                'topic2': row.get(keys[1], 0) if isinstance(row, dict) else 0,
                'topic3': row.get(keys[2], 0) if isinstance(row, dict) else 0,
                'topic4': row.get(keys[3], 0) if isinstance(row, dict) else 0,
                'topic5': row.get(keys[4], 0) if isinstance(row, dict) else 0,
                'topic6': row.get(keys[5], 0) if isinstance(row, dict) else 0,
                'topic7': row.get(keys[6], 0) if isinstance(row, dict) else 0,
                'total': f"{total_val}",
                'rank': rank_val
            }
            labels.append(test_no)
            # ensure numeric chart data where possible
            try:
                chart_data.append(float(total_val))
            except Exception:
                chart_data.append(0)
            chart_rank.append(rank_val)
            table_d.append(rowd)

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
            total_val = row.get(keys[7], 0) if isinstance(row, dict) else 0
            mock_row = {
                'testName': row.get('Test Name', '') if isinstance(row, dict) else '',
                'topic1': row.get(keys[0], 0) if isinstance(row, dict) else 0,
                'topic2': row.get(keys[1], 0) if isinstance(row, dict) else 0,
                'topic3': row.get(keys[2], 0) if isinstance(row, dict) else 0,
                'topic4': row.get(keys[3], 0) if isinstance(row, dict) else 0,
                'topic5': row.get(keys[4], 0) if isinstance(row, dict) else 0,
                'topic6': row.get(keys[5], 0) if isinstance(row, dict) else 0,
                'topic7': row.get(keys[6], 0) if isinstance(row, dict) else 0,
                'total': f"{total_val}",
                'rank': row.get(keys[8], 0) if isinstance(row, dict) else 0
            }
            mock_table.append(mock_row)
    return mock_table