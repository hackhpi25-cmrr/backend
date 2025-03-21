def treatmentoptions(points, weights, now):
    """
    array of array of floats/ints

    points[i][0] -> treatment ID
    points[i][1] -> treatment effect
    points[i][j] -> j >= 2 -> value for point

    return array of treatment with expected outcome
    """
    normAdd = 10
    normMull = 1
    score = []
    for point in points:
        res = []
        res.append(point[0])
        res.append(1)
        cnt = 0
        for i in range(2, len(point)):
            if(point[i]==None or now[i-2]==None):
                cnt += 1
                continue
            res *= (abs(point[i]-now[i-2])* weights[i])
        res /= (len(point)-2-cnt)
        score.append(res)
        res *= (normAdd - points[1])*normMull
        score.append(res)

    return score

def rankTreatmentByUse(score):
    """
    array of array floats/ints

    score[i][0] -> treatmentID for treatment i
    score[i][1] -> score for treatment i

    return ranked treatment
    """
    #print(score)
    sortedScore = sorted(score, key=lambda x: (x[1], x[2], x[0]))
    #print(sortedScore)
    res = []
    exists = []
    for i in range(len(sortedScore)):
        if not sortedScore[i][0] in exists:
            exists.append(sortedScore[i][0])
            res.append(sortedScore[i])

    return res

def rankTreatmentByDist(score):
    """
    array of array floats/ints

    score[i][0] -> treatmentID for treatment i
    score[i][1] -> score for treatment i

    return ranked treatment
    """
    #print(score)
    sortedScore = sorted(score, key=lambda x: (x[2], x[1], x[0]))
    #print(sortedScore)
    res = []
    exists = []
    for i in range(len(sortedScore)):
        if not sortedScore[i][0] in exists:
            exists.append(sortedScore[i][0])
            res.append(sortedScore[i])

    return res
    



def anticipatePainlevel(points, weights, now, skipped):
    """
    array of array of floats/ints

    points[i][0] -> painlevel
    points[i][j] -> j >= 1 -> value for point

    return anticiapted Painlevel
    """
    dist = -1
    pain = 0
    for point in points:
        res = 0
        
        cnt = 0
        for i in range(1, len(point)):
            if(point[i]==None or now[i-1]==None):
                cnt += 1
                continue
            res *= (abs(point[i]-now[i-1])* weights[i])
        res /= (len(point)-2-cnt)
        if(res < dist or dist == -1):
            dist = res
            pain = point[0]

    return pain

