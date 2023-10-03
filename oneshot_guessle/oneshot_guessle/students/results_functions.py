

subjects = {
    'cs':{
        11:['1. Algorithms', '2. Programming', '3. Computer Systems', '4. Data rep', '5. Security', '6. Networks',
            '7. ethics & Leg', '%', 'Rank'],
        13:['1.1 IO & Storage', '1.2 Software & Development', '1.3 Exchanging Data','1.4 Datatypes & Algorithms', 
            '1.5 legal & moral issues', '2.1 Computation Thinking', '2.2 Problem Solving', '%', 'Rank']
    }
}


def analysis_table(data, year, student, subject):
    # Looks at each row in the spreadsheet table
    for i in range(len(data)):
        # finds the row matching the users student ID
        # and gathers data for the table
        if data[i]['exam_ID'] == student:
            studentX = data[i]
            studentX_d = {
                'atopic1':studentX[subjects[subject][year][0]], 
                'atopic2':studentX[subjects[subject][year][1]],
                'atopic3':studentX[subjects[subject][year][2]],
                'atopic4':studentX[subjects[subject][year][3]],
                'atopic5':studentX[subjects[subject][year][4]],
                'atopic6':studentX[subjects[subject][year][5]],
                'atopic7':studentX[subjects[subject][year][6]],
                'aAv':studentX[subjects[subject][year][7]],
                'aRank':studentX[subjects[subject][year][8]]
            }
    #returns the data to be shared in the template
    return studentX_d

def weekly_tests_table(data, year, student, subject):
    table_d = []
    labels = []
    chart_data =[] 
    chart_rank=[]

    for i in range(len(data)):
        if data[i]['exam_ID'] == student:
            row = {
                'testNO':data[i]['Test No'],
                'topic1':data[i][subjects[subject][year][0]], # , ".2%") try later
                'topic2':data[i][subjects[subject][year][1]],
                'topic3':data[i][subjects[subject][year][2]],
                'topic4':data[i][subjects[subject][year][3]],
                'topic5':data[i][subjects[subject][year][4]],
                'topic6':data[i][subjects[subject][year][5]],
                'topic7':data[i][subjects[subject][year][6]],
                'total':f"{data[i][subjects[subject][year][7]]}",
                'rank':data[i][subjects[subject][year][8]]
            }
            labels.append(data[i]['Test No'])
            chart_data.append(data[i][subjects[subject][year][7]])
            chart_rank.append(data[i][subjects[subject][year][8]])
            table_d.append(row)
    
    return table_d, labels, chart_data, chart_rank

def mock_tests_table(data, year, student, subject):
    mock_table=[]
    for i in range(len(data)):
        if data[i]['exam_ID'] == student:
            row = {
                'testName':data[i]['Test Name'],
                'topic1':data[i][subjects[subject][year][0]], # 
                'topic2':data[i][subjects[subject][year][1]],
                'topic3':data[i][subjects[subject][year][2]],
                'topic4':data[i][subjects[subject][year][3]],
                'topic5':data[i][subjects[subject][year][4]],
                'topic6':data[i][subjects[subject][year][5]],
                'topic7':data[i][subjects[subject][year][6]],
                'total':f"{data[i][subjects[subject][year][7]]}",
                'rank':data[i][subjects[subject][year][8]]                }
            mock_table.append(row)
    return mock_table