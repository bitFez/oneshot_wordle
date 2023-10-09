from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404 
import requests
from django.conf import settings

from .results_functions import analysis_table, weekly_tests_table, mock_tests_table
from .models import Student

SHEETS_API=settings.G_SHEETS_API

# Create your views here.
# refactored API call
def g_sheet_API_call(user, page):
    year = user.exam_yr
    
    # sheetID represents which Google Sheet **Document** is being accessed
    # 
    # This will need to be refactored further if we need to include different schools or departments
    # A solution in my head currently is either a file in the repo with a list of schools & departments 
    # with their corresponding GoogleSheet IDs and subjects in a dict or ...
    # another Google Sheet document which returns a lookup table with all the desired data to other 
    # GoogleSheet documents 
    if year == 11:
        sheetID = '1jOgSUMeC7bPntFZ7g7ForLs_YVhyTr7HhOtAZG49RgQ'
    elif year == 10:
        sheetID = '1GYrLbDSRNewGxHuUuoDq8OEUItB_26JReNAZnjgBlO4'
    else:
        sheetID = '1eKKi6VzHKVZYd0YsAynTNXjo_DWvEldm6OXwJ9WPfPA'

    # pageID represents which sheet within a docoument is being accessed eg. analysis, weekly_tests or mocks
    pageID = page

    # data to return
    data = requests.get(f'https://gsx2json.com/api?id={sheetID}&sheet={pageID}&api_key={SHEETS_API}&columns=false')
    dataJSON = data.json()
    return dataJSON['rows']

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


def student(request):
    #
    # Gets user id from whoever is logged in
    user = get_object_or_404(Student, pk=request.user.id)
    
    # takes student data from user profile
    student = user.examNo
    
    # 
    # Chart data - data is appended in the weekly test for loops for yrs11 & 13
    #
    labels = []
    chart_data = []
    chart_rank = []

    if user.exam_yr == 13:
        # gets spreadsheet data from the analysis sheet... (averages of all tests)
        analysis_rows = g_sheet_API_call(user, 'Analysis')

        # filters data for student from above get request
        studentX_d = analysis_table(analysis_rows, 13, student, 'cs')

        # gets spreadsheet data from the weekly tests sheet
        data_rows = g_sheet_API_call(user, '6aWeekTests')

        # filters data for each test for selected student ID
        table_d, labels, chart_data, chart_rank= weekly_tests_table(data_rows, 13, student, 'cs')

        # gets spreadsheet data from mock tests sheet
        mock_data_rows = g_sheet_API_call(user, 'Mocks')
        #print(f"Status code {response.status_code}") # left here for reference
        #print(jprint(data_rows))

        # filters data for each test for selected student ID
        mock_table = mock_tests_table(mock_data_rows, 13, student, 'cs')
        
    else:
        # gets spreadsheet data from the analysis sheet... (averages of all tests)
        analysis_rows = g_sheet_API_call(user, 'Analysis')

        # filters data for student from above get request
        studentX_d = analysis_table(analysis_rows, 11, student, 'cs')

        # gets spreadsheet data from the weekly tests sheet
        data_rows = g_sheet_API_call(user, '6aWeekTests')

        # filters data for each test for selected student ID
        table_d, labels, chart_data, chart_rank= weekly_tests_table(data_rows, 11, student, 'cs')

        # gets spreadsheet data from mock tests sheet
        mock_data_rows = g_sheet_API_call(user, 'Mocks')
        
        # filters data for each test for selected student ID
        mock_table = mock_tests_table(mock_data_rows, 11, student, 'cs')

    context = {'tests':table_d, 'analysis':studentX_d, 'mock_table':mock_table, 
                'student':student, 'chart_data':chart_data, 'labels':labels, 'chart_rank':chart_rank}
    return render(request, 'students/student.html', context)