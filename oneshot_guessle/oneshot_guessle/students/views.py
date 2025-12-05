from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404 
import requests
from django.http import Http404
import traceback, sys

from .results_functions import analysis_table, weekly_tests_table, mock_tests_table
from .models import SheetsTab

# APIs are no longer pulled from an ENV file. This is impractical
# This will be pulled from the SheetsTab model. 
# If no API call can be made, a Http404 error is raised.


# refactored API call
def g_sheet_API_call(sheet, year, page):
        
    g_sheet = sheet
    if not g_sheet:
        raise Http404(f"No Google Sheet configured for year: {year}")

    # pageID represents which sheet within a docoument is being accessed eg. analysis, weekly_tests or mocks
    pageID = page

    # data to return. g_sheet
    # use a session with retries and a timeout
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        # WARNING: verify=False disables TLS verification; use only in local debugging
        import certifi
        resp = session.get(f"{g_sheet}?gid={pageID}", timeout=10, verify=certifi.where())
        resp.raise_for_status()
        dataJSON = resp.json()
    except requests.exceptions.SSLError:
        # SSL problem — log and return a friendly 404 in dev
        traceback.print_exc(file=sys.stdout)
        raise Http404("SSL error fetching Google Sheet. Ensure container has CA certificates installed.")
    except requests.exceptions.RequestException:
        traceback.print_exc(file=sys.stdout)
        raise Http404("Failed to fetch Google Sheet (network error).")
    except ValueError:
        # invalid JSON
        traceback.print_exc(file=sys.stdout)
        raise Http404("Invalid JSON returned from Google Sheet API.")

    if isinstance(dataJSON, dict):
        rows = dataJSON.get("rows", [])
    elif isinstance(dataJSON, list):
        rows = dataJSON
    else:
        rows = []
    
    return rows

# Page for viewing test results
def fakestudent(request):
    user = 'HealthyRabbit235'
    chart_data = []
    labels = []
    chart_rank = []
    table_d = [
        {
            'testNO':1,
            'topic1':0,
            'topic2':0.41,
            'topic3':0.2,
            'topic4':0.4,
            'topic5':0,
            'topic6':0,
            'topic7':0,
            'total':34.4,
            'rank':56,
        },
        {
            'testNO':2,
            'topic1':0.30,
            'topic2':1,
            'topic3':0.73,
            'topic4':0.66,
            'topic5':0,
            'topic6':0,
            'topic7':0,
            'total':75,
            'rank':14,
        },
        {
            'testNO':3,
            'topic1':0.67,
            'topic2':0.87,
            'topic3':0.54,
            'topic4':0.67,
            'topic5':0.45,
            'topic6':0,
            'topic7':0,
            'total':50.6,
            'rank':23,
        },
        {
            'testNO':4,
            'topic1':0,
            'topic2':0.7,
            'topic3':0.3,
            'topic4':0.55,
            'topic5':0,
            'topic6':0.45,
            'topic7':0.75,
            'total':55,
            'rank':19,
        },
    ]
    for i in range(0,len(table_d)):
        labels.append(table_d[i]['testNO'])
        chart_data.append(table_d[i]['total'])
        chart_rank.append(table_d[i]['rank'])


    studentX_d = {
        'atopic1':0.48,
        'atopic2':0.74,
        'atopic3':0.52,
        'atopic4':0.57,
        'atopic5':0.45,
        'atopic6':0.45,
        'atopic7':0.75,
        'aAv':53.75,
        'aRank':28,
    }

    mock_table = [{
        'testName':"Year # mocks test",
        'topic1':0,
        'topic2':0.7,
        'topic3':0.5,
        'topic4':0.45,
        'topic5':45,
        'topic6':0.45,
        'topic7':0.75,
        'total':55,
        'rank':22,
    }]
    #
    # Include code to create a random generated picture when creating an account as a profile picture
    #
    #pic = https://api.unsplash.com/photos/?client_id=7Pnkiwb8hx0pexhKzCDcy0ITsULKZlNAX6ODEdTkjVA&
    
    
    context = {'tests':table_d, 'analysis':studentX_d, 'mock_table':mock_table, 'student':user,#student
                'chart_data':chart_data, 'labels':labels, 'chart_rank':chart_rank}
    return render(request, 'students/student.html', context)


def student(request, year, studentID,ks):
    
    try:
        # Gets list of IDs
        sheetIDs = get_object_or_404(SheetsTab, year=year)
        # print(f"SheetID, {sheetIDs}")
    except Http404:
        # print helpful context and the exception traceback then re-raise so Django still returns 404
        # print(f"Http404: SheetsTab with id={year} not found", file=sys.stdout)
        traceback.print_exc(file=sys.stdout)
        raise
    except Exception:
        # print full traceback for any other error then re-raise
        traceback.print_exc(file=sys.stdout)
        raise
    
    student = studentID #user.examNo
    
    # 
    # Chart data - data is appended in the weekly test for loops for yrs11 & 13
    #
    labels = []
    chart_data = []
    chart_rank = []

    if ks == 'KS5':
        # gets spreadsheet data from the analysis sheet... (averages of all tests)
        analysis_rows = g_sheet_API_call(sheetIDs.json_workbook, sheetIDs.year, sheetIDs.week_tests_analysis)

        # filters data for student from above get request
        studentX_d = analysis_table(analysis_rows, 'KS5', student, 'cs')

        # gets spreadsheet data from the weekly tests sheet
        data_rows = g_sheet_API_call(sheetIDs.json_workbook, sheetIDs.year, sheetIDs.weekly_tests)

        # filters data for each test for selected student ID
        table_d, labels, chart_data, chart_rank= weekly_tests_table(data_rows, 13, student, 'cs')

        # gets spreadsheet data from mock tests sheet
        mock_data_rows = g_sheet_API_call(sheetIDs.json_workbook, sheetIDs.year, sheetIDs.mocks)
        #print(f"Status code {response.status_code}") # left here for reference
        #print(jprint(data_rows))

        # filters data for each test for selected student ID
        mock_table = mock_tests_table(mock_data_rows, 'KS5', student, 'cs')
        
    else:
        # gets spreadsheet data from the analysis sheet... (averages of all tests)
        analysis_rows = g_sheet_API_call(sheetIDs.json_workbook, year, sheetIDs.week_tests_analysis)

        # filters data for student from above get request
        studentX_d = analysis_table(analysis_rows, 'KS4', student, 'cs')

        # gets spreadsheet data from the weekly tests sheet
        data_rows = g_sheet_API_call(sheetIDs.json_workbook, sheetIDs.year, sheetIDs.weekly_tests)

        # filters data for each test for selected student ID
        table_d, labels, chart_data, chart_rank= weekly_tests_table(data_rows, 11, student, 'cs')

        # gets spreadsheet data from mock tests sheet
        mock_data_rows = g_sheet_API_call(sheetIDs.json_workbook, sheetIDs.year, sheetIDs.mocks)
        
        # filters data for each test for selected student ID
        mock_table = mock_tests_table(mock_data_rows, 'KS4', student, 'cs')

    context = {'tests':table_d, 'analysis':studentX_d, 'mock_table':mock_table, 
                'student':student, 'chart_data':chart_data, 'labels':labels, 'chart_rank':chart_rank}
    return render(request, 'students/student.html', context)