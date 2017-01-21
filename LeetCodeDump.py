import re
import os
import requests
from bs4 import BeautifulSoup

folderName = "LeetCodeSolutions"
if not os.path.exists(folderName):
    os.makedirs(folderName)

class LeetCodeDump:
    def __init__(self):
        # change this
        self.payload = {
            'login': 'username',
            'password': 'password'
        }
        
        self.baseURL = "https://leetcode.com"
        self.loginURL = "https://leetcode.com/accounts/login/"
        self.submissionsURL = "https://leetcode.com/submissions/"
        self.headers = {
            "Host": "leetcode.com",
            "Origin": "https://leetcode.com",
            "Referer": "https://leetcode.com/accounts/login/",
            "Upgrade-Insecure-Requests": "1"
        }
        self.langDict = {
            "python": "py",
            "java": "java",
            "mysql": "sql",
            "cpp": "cpp",
            "c": "c",
            "csharp": "cs",
            "javascript": "js",
            "ruby": "rb"
        }
        self.s = requests.Session()
        
    def __del__(self):
        self.s.close()

    def getQuestionTitle(self, questionURL):
        response = self.s.get(url = questionURL)
        soup = BeautifulSoup(response.text, 'lxml')
        questionTitle = soup.find('div', attrs={'class': "question-title"}).find("h3").text
        return questionTitle.strip()

    def getSolutionDetails(self, solutionURL):
        response = self.s.get(url = solutionURL)
        solution = re.search("submissionCode: '(.+)',\n  editCodeUrl:", response.text).group(1)
        return solution.decode('unicode-escape')

    def parseSubmissionPage(self, response):
        submissionTable = BeautifulSoup(response.text, 'lxml')
        rows = submissionTable.find('tbody').find_all('tr')
        for row in rows:
            questionName = row.find_all("td")[1].text
            accepted = row.find_all("td")[2].text.strip()
            lang = row.find_all("td")[4].text.strip()
            questionURL = row.find_all("td")[1].find('a')['href']
            solutionURL = row.find_all("td")[2].find('a')['href']
            questionTitle = self.getQuestionTitle(self.baseURL + questionURL)
            solutionDetails = self.getSolutionDetails(self.baseURL + solutionURL)
            if accepted == "Accepted":
                fName = os.path.join(folderName, questionTitle) + '.' + self.langDict[lang]
                if not os.path.isfile(fName):
                    with open(fName, "w") as f:
                        f.write(solutionDetails)

    def start(self):
        # get csrfmiddlewaretoken
        firstVisit = self.s.get(url = self.loginURL)
        soup = BeautifulSoup(firstVisit.text, 'lxml')
        csrfmiddlewaretoken = soup.find('input', attrs={'name': "csrfmiddlewaretoken"})['value']
        self.payload['csrfmiddlewaretoken'] = csrfmiddlewaretoken

        # login
        homepage = self.s.post(url=self.loginURL, headers=self.headers, data=self.payload)
        try:
            userName = re.search('<li><a href="/(.+)/">Profile</a></li>', homepage.text).group(1)
            print "Successfully Login as " + userName
        except AttributeError:
            print homepage.text

        # read submissions
        for i in range(200):
            response = self.s.get(self.submissionsURL + str(i))
            if "No more submissions." not in response.text:
                self.parseSubmissionPage(response)
                print str(i+1) + " page(s) parsed."
        print "Done!"


if __name__ == "__main__":
    lcd = LeetCodeDump()
    lcd.start()


