subjects = {
    'cs':{
        'KS4':['1.1 System Architecture','1.2 Memory & Storage','1.3 Networks','1.4 Network Security',
               '1.5 System Software','1.6 ELCE','2.1 Algorithms','2.2 Programming fundamentals',
               '2.3 Producing Robust Programs','2.4 Boolean Logic','2.5 Languages and IDEs', '%', 'Rank'],
        # KS5 headers aligned to the sheet export (no trailing spaces)
        'KS5':['1.1 IO & Storage', '1.2 Software & Development', '1.3 Exchanging Data','1.4 Datatypes & Algorithms', 
            '1.5 legal & moral issues', '2.1 Computation Thinking', '2.2 Problem Solving','2.3 Algorithms' , '%', 'Rank']
    }
}


def _get_by_prefix(row, key, default=0):
    if not isinstance(row, dict) or not isinstance(key, str):
        return default

    if key in row:
        return row.get(key, default)

    prefix = key.strip().split(" ")[0]
    if not prefix:
        return default

    for k, v in row.items():
        if isinstance(k, str) and k.strip().startswith(prefix):
            return v

    return default

# ============ KS4 Functions ============

def analysis_table_ks4(data, student, subject):
    """Analysis table for KS4 (11 topics + % + Rank)"""
    studentX_d = {
        'atopic1': 0, 'atopic2': 0, 'atopic3': 0, 'atopic4': 0, 'atopic5': 0,
        'atopic6': 0, 'atopic7': 0, 'atopic8': 0, 'atopic9': 0, 'atopic10': 0,
        'atopic11': 0, 'aAv': 0, 'aRank': 0,
    }

    if not data:
        return studentX_d

    keys = subjects.get(subject, {}).get('KS4', [])

    def extract_value(row, key):
        if isinstance(row, dict):
            return row.get(key, 0)
        elif isinstance(row, (list, tuple)):
            try:
                return row[int(key)]
            except Exception:
                return 0
        return 0

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

def analysis_table_ks5(data, student, subject):
    """Analysis table for KS5 (7 topics + % + Rank)"""
    studentX_d = {
        'atopic1': 0, 'atopic2': 0, 'atopic3': 0, 'atopic4': 0, 'atopic5': 0,
        'atopic6': 0, 'atopic7': 0, 'atopic8': 0, 'atopic9': 0, 'atopic10': 0,
        'atopic11': 0, 'aAv': 0, 'aRank': 0,
    }

    if not data:
        return studentX_d

    keys = subjects.get(subject, {}).get('KS5', [])

    def extract_value(row, key):
        if isinstance(row, dict):
            return _get_by_prefix(row, key, 0)
        elif isinstance(row, (list, tuple)):
            try:
                return row[int(key)]
            except Exception:
                return 0
        return 0

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
            studentX_d = {
                'atopic1': extract_value(row, keys[0]),
                'atopic2': extract_value(row, keys[1]),
                'atopic3': extract_value(row, keys[2]),
                'atopic4': extract_value(row, keys[3]),
                'atopic5': extract_value(row, keys[4]),
                'atopic6': extract_value(row, keys[5]),
                'atopic7': extract_value(row, keys[6]),
                'atopic8': extract_value(row, keys[7]),
                'atopic9': 0,
                'atopic10': 0,
                'atopic11': 0,
                'aAv': extract_value(row, keys[8]),
                'aRank': extract_value(row, keys[9]),
            }
            break

    return studentX_d

def weekly_tests_table_ks4(data, student, subject):
    """Weekly tests table for KS4 (11 topics)"""
    table_d = []
    labels = []
    chart_data = []
    chart_rank = []

    keys = subjects.get(subject, {}).get('KS4', [])
    if not keys or not data:
        return table_d, labels, chart_data, chart_rank

    student_str = str(student).strip()

    for row in enumerate(data):
        idx, row = row[0], row[1]
        exam_id_val = None
        class_val = None
        name_val = None
        if isinstance(row, dict):
            exam_id_val = row.get('exam_ID') or row.get('exam_id') or row.get('examNo') or row.get('Exam ID')
            class_val = row.get('class') or row.get('Class')
            name_val = row.get('name') or row.get('Name')
        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]

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
            'topic1': _get_topic(row, keys[0]),
            'topic2': _get_topic(row, keys[1]),
            'topic3': _get_topic(row, keys[2]),
            'topic4': _get_topic(row, keys[3]),
            'topic5': _get_topic(row, keys[4]),
            'topic6': _get_topic(row, keys[5]),
            'topic7': _get_topic(row, keys[6]),
            'topic8': _get_topic(row, keys[7]),
            'topic9': _get_topic(row, keys[8]),
            'topic10': _get_topic(row, keys[9]),
            'topic11': _get_topic(row, keys[10]),
            'total': f"{total_val}",
            'perc': f"{perc}",
            'rank': rank_val
        }

        labels.append(test_no)
        # prefer percentage for charting; fallback to total if percent not numeric
        try:
            chart_data.append(float(perc))
        except Exception:
            try:
                chart_data.append(float(total_val))
            except Exception:
                chart_data.append(0)
        chart_rank.append(rank_val)
        table_d.append(rowd)

    return table_d, labels, chart_data, chart_rank

def weekly_tests_table_ks5(data, student, subject):
    """Weekly tests table for KS5 (7 topics)"""
    table_d = []
    labels = []
    chart_data = []
    chart_rank = []

    keys = subjects.get(subject, {}).get('KS5', [])
    if not keys or not data:
        return table_d, labels, chart_data, chart_rank

    student_str = str(student).strip()

    for row in enumerate(data):
        idx, row = row[0], row[1]
        exam_id_val = None
        class_val = None
        name_val = None
        if isinstance(row, dict):
            exam_id_val = row.get('exam_ID') or row.get('exam_id') or row.get('examNo') or row.get('Exam ID')
            class_val = row.get('class') or row.get('Class')
            name_val = row.get('name') or row.get('Name')
        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]

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

        if not matched:
            continue

        test_no = row.get('Test No') if isinstance(row, dict) else (row[1] if len(row) > 1 else None)
        total_val = row.get('Total') if isinstance(row, dict) else 0
        perc = row.get('%') if isinstance(row, dict) else 0
        rank_val = row.get('Rank') if isinstance(row, dict) else 0

        def _get_topic(r, k):
            try:
                return _get_by_prefix(r, k, 0) if isinstance(r, dict) else 0
            except Exception:
                return 0

        rowd = {
            'testNO': test_no,
            'topic1': _get_topic(row, keys[0]),
            'topic2': _get_topic(row, keys[1]),
            'topic3': _get_topic(row, keys[2]),
            'topic4': _get_topic(row, keys[3]),
            'topic5': _get_topic(row, keys[4]),
            'topic6': _get_topic(row, keys[5]),
            'topic7': _get_topic(row, keys[6]),
            'topic8': _get_topic(row, keys[7]),
            'topic9': 0,
            'topic10': 0,
            'topic11': 0,
            'total': f"{total_val}",
            'perc': f"{perc}",
            'rank': rank_val
        }

        labels.append(test_no)
        # prefer percentage for charting; fallback to total if percent not numeric
        try:
            chart_data.append(float(perc))
        except Exception:
            try:
                chart_data.append(float(total_val))
            except Exception:
                chart_data.append(0)
        chart_rank.append(rank_val)
        table_d.append(rowd)

    return table_d, labels, chart_data, chart_rank

def mock_tests_table_ks4(data, student, subject):
    """Mock tests table for KS4 (11 topics)"""
    mock_table = []
    keys = subjects.get(subject, {}).get('KS4', [])
    
    if not keys or not data:
        return mock_table

    for row in data:
        if isinstance(row, dict):
            norm = {}
            for k, v in row.items():
                if isinstance(k, str):
                    stripped = k.strip()
                    norm[stripped] = v
                    norm[stripped.lower()] = v
                else:
                    norm[k] = v
            def get_norm(key):
                if key in norm:
                    return norm[key]
                key_s = key.strip()
                if key_s in norm:
                    return norm[key_s]
                key_l = key_s.lower()
                if key_l in norm:
                    return norm[key_l]
                for nk in norm.keys():
                    if isinstance(nk, str) and nk.lower().startswith(key_l):
                        return norm[nk]
                return None

            exam_id_val = (
                get_norm('exam_ID') or get_norm('exam id') or get_norm('exam_id')
                or get_norm('examNo') or get_norm('Exam ID') or get_norm('exam_ID ')
            )
            rank_val = get_norm('Rank')
            total_val = get_norm('Total')

            test_name_val = get_norm('Test Name')
            if test_name_val is None:
                for nk in norm.keys():
                    if isinstance(nk, str) and nk.lower().startswith('test name'):
                        test_name_val = norm[nk]
                        break

            def topic_val(pos):
                if pos >= len(keys):
                    return 0
                v = get_norm(keys[pos])
                return v if v is not None else 0

        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]
            rank_val = row[2] if len(row) > 2 else None
            total_val = row[1] if len(row) > 1 else None
            test_name_val = row[3] if len(row) > 3 else ''
            def topic_val(pos):
                return row[pos + 4] if len(row) > pos + 4 else 0
        else:
            continue

        if exam_id_val is None:
            continue

        if str(exam_id_val).strip() == str(student).strip():
            mock_row = {
                'testName': test_name_val or '',
                'topic1': topic_val(0),
                'topic2': topic_val(1),
                'topic3': topic_val(2),
                'topic4': topic_val(3),
                'topic5': topic_val(4),
                'topic6': topic_val(5),
                'topic7': topic_val(6),
                'topic8': topic_val(7),
                'topic9': topic_val(8),
                'topic10': topic_val(9),
                'topic11': topic_val(10),
                'total': f"{total_val}",
                'rank': rank_val or 0,
            }
            mock_table.append(mock_row)
    return mock_table

def mock_tests_table_ks5(data, student, subject):
    """Mock tests table for KS5 (7 topics)"""
    mock_table = []
    keys = subjects.get(subject, {}).get('KS5', [])
    
    if not keys or not data:
        return mock_table

    for row in data:
        if isinstance(row, dict):
            norm = {}
            for k, v in row.items():
                if isinstance(k, str):
                    stripped = k.strip()
                    norm[stripped] = v
                    norm[stripped.lower()] = v
                else:
                    norm[k] = v
            def get_norm(key):
                if key in norm:
                    return norm[key]
                key_s = key.strip()
                if key_s in norm:
                    return norm[key_s]
                key_l = key_s.lower()
                if key_l in norm:
                    return norm[key_l]
                for nk in norm.keys():
                    if isinstance(nk, str) and nk.lower().startswith(key_l):
                        return norm[nk]
                return None

            exam_id_val = (
                get_norm('exam_ID') or get_norm('exam id') or get_norm('exam_id')
                or get_norm('examNo') or get_norm('Exam ID') or get_norm('exam_ID ')
            )
            rank_val = get_norm('Rank')
            total_val = get_norm('Total')

            test_name_val = get_norm('Test Name')
            if test_name_val is None:
                for nk in norm.keys():
                    if isinstance(nk, str) and nk.lower().startswith('test name'):
                        test_name_val = norm[nk]
                        break

            def topic_val(pos):
                if pos >= len(keys):
                    return 0
                v = get_norm(keys[pos])
                if v is None:
                    v = _get_by_prefix(row, keys[pos], 0)
                return v if v is not None else 0

        elif isinstance(row, (list, tuple)) and len(row) > 0:
            exam_id_val = row[0]
            rank_val = row[2] if len(row) > 2 else None
            total_val = row[1] if len(row) > 1 else None
            test_name_val = row[3] if len(row) > 3 else ''
            def topic_val(pos):
                return row[pos + 4] if len(row) > pos + 4 else 0
        else:
            continue

        if exam_id_val is None:
            continue

        if str(exam_id_val).strip() == str(student).strip():
            mock_row = {
                'testName': test_name_val or '',
                'topic1': topic_val(0),
                'topic2': topic_val(1),
                'topic3': topic_val(2),
                'topic4': topic_val(3),
                'topic5': topic_val(4),
                'topic6': topic_val(5),
                'topic7': topic_val(6),
                'topic8': topic_val(7),
                'topic9': 0,
                'topic10': 0,
                'topic11': 0,
                'total': f"{total_val}",
                'rank': rank_val or 0,
            }
            mock_table.append(mock_row)
    return mock_table

# ============ Legacy wrapper functions (for backwards compatibility) ============

def analysis_table(data, ks, student, subject):
    """Wrapper that delegates to KS4 or KS5 version"""
    if ks.upper() == 'KS5':
        return analysis_table_ks5(data, student, subject)
    else:
        return analysis_table_ks4(data, student, subject)

def weekly_tests_table(data, year, student, subject):
    """Wrapper that delegates to KS4 or KS5 version"""
    if year.upper() == 'KS5':
        return weekly_tests_table_ks5(data, student, subject)
    else:
        return weekly_tests_table_ks4(data, student, subject)

def mock_tests_table(data, year, student, subject):
    """Wrapper that delegates to KS4 or KS5 version"""
    if year.upper() == 'KS5':
        return mock_tests_table_ks5(data, student, subject)
    else:
        return mock_tests_table_ks4(data, student, subject)
