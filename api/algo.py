def treatmentoptions(points, weights, now):
    """
    array of array of floats/ints

    points[i][0] -> treatment ID
    points[i][1] -> treatment effect
    points[i][j] -> j >= 2 -> value for point

    return array of treatments with expected outcome
    score[i][0] -> treatmentID for treatment i
    score[i][1] -> score for treatment i
    score[i][2] -> dist for treatment i
    score[i][3] -> effectivness for treatment i
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
            res[1] *= (abs(point[i]-now[i-2])* weights[i])
        res[1] /= (len(point)-1-cnt)
        res.append(res[1])
        res[2] *= (normAdd - point[1]) * normMull
        res.append(point[1])
        score.append(res)

    return score

def rankTreatmentByUse(score):
    """
    array of array floats/ints

    score[i][0] -> treatmentID for treatment i
    score[i][1] -> score for treatment i
    score[i][2] -> dist for treatment i
    score[i][3] -> effectivness for treatment i

    return ranked treatment
    """
    #print(score)
    sortedScore = sorted(score, key=lambda x: (x[1], x[2], x[3], x[0]))
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
    score[i][2] -> dist for treatment i
    score[i][3] -> effectivness for treatment i

    return ranked treatment
    """
    #print(score)
    sortedScore = sorted(score, key=lambda x: (x[2], x[1], x[3], x[0]))
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
        res /= (len(point)-1-cnt)
        if(res < dist or dist == -1):
            dist = res
            pain = point[0]

    return pain


def bestUserProfile(userProfiles, weights, now):
    """
    userProfiles array of user
    
    userProfiles[i][0] -> userID
    userProfiles[i][j] -> j >= 1 -> values from baseline

    now array of values

    now[i] -> i >= 0 -> values from now

    return best userID
    """
    score = []
    for user in userProfiles:
        score.append([user[0], 1])
        cnt = 0
        for i in range(1, len(user)):
            if(user[i]==None or now[i-1]==None):
                cnt += 1
                continue
            score[1] *= (abs(user[i]-now[i-1])* weights[i])
        score[1] /= (len(user)-cnt)
    sortedScore = sorted(score, key=lambda x: (x[1], x[0]))
    return sortedScore[0][0]

from .models import Logbook, ParameterAnswer, Baseline, Suggestion, Treatment, Parameter, BaselineQuestion

def rankFromDB(nowID):

    parameters = Parameter.objects.all()
    
    # Gewichtungen und Sortierung filtern
    parameterIDs = []
    weights = []
    for parameter in parameters:
        weights.append(parameter.weight)
        parameterIDs.append(parameter.id)
    
    # Logbucheintrag von now holen
    nowlogbook = Logbook.objects.get(id=nowID)
    userID = nowlogbook.user.id
    now = []

    # Parameterantworten von now holen
    for parameterID in parameterIDs:
        try:
            answer = ParameterAnswer.objects.get(parameter_id=parameterID, logbook_entry_id=nowID)
            now.append(answer.normalised_answer)
        except ParameterAnswer.DoesNotExist:
            now.append(None)

    points = []
    Logbooks = Logbook.objects.all()
    suggestions = Suggestion.objects.all()
    for logbook in Logbooks:
        if logbook.id == nowID or logbook.user.id != userID:
            continue
        # Suggestions durchsuchen
        tmp = []
        for suggestion in suggestions:
            if suggestion.logbook_entry.id == logbook.id:
                tmp.append(suggestion.treatment.id)
                tmp.append(suggestion.effectiveness)
                for parameterID in parameterIDs:
                    try:
                        answer = ParameterAnswer.objects.get(parameter_id=parameterID, logbook_entry_id=logbook.id)
                        tmp.append(answer.normalised_answer)
                    except ParameterAnswer.DoesNotExist:
                        tmp.append(None)
    points.append(tmp)

    # Scores berechnen
    score = treatmentoptions(points, weights, now)

    # Ranking
    ranked = rankTreatmentByUse(score)

    return ranked



def getBaseUserProfileFromDB(userID, userProfilesIDs):
    
    # Baselinefragen holen
    baselineQuestions = BaselineQuestion.objects.all()
    
    # Weights und IDs holen
    baselineIDs = []
    weights = []
    for baselineQuestion in baselineQuestions:
        weights.append(baselineQuestion.weight)
        baselineIDs.append(baselineQuestion.id)

    # Baseline von User holen
    now = []
    for baselineID in baselineIDs:
        try:
            baseline = Baseline.objects.get(user_id=userID, baseline_question_id=baselineID)
            now.append(baseline.normalised_answer)
        except Baseline.DoesNotExist:
            now.append(None)

    userProfiles = []
    for userProfilesID in userProfilesIDs:
        user = []
        user.append(userProfilesID)
        for baselineID in baselineIDs:
            try:
                baseline = Baseline.objects.get(user_id=userProfilesID, baseline_question_id=baselineID)
                user.append(baseline.normalised_answer)
            except Baseline.DoesNotExist:
                user.append(None)
        userProfiles.append(user)

    # Bestes Profil finden
    bestProfile = bestUserProfile(userProfiles, weights, now)

    return bestProfile


    

