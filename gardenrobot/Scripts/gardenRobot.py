from github     import Github
import          urllib2
import          datetime
import          pygit2
from robot      import Robot
import          random

file = open("/home/ubuntu/gitlogin.txt", "r") 
logins = file.readlines() 
userName = logins[0].replace('\n', '')
password = logins[1].replace('\n', '')

# Login to github
g = Github(userName, password)
org = g.get_organization('MaslowCommunityGarden')
repos = org.get_repos()

robot = Robot()

weShouldCheckImageLinks = False
if random.randint(0, 10) == 1:
    weShouldCheckImageLinks = True

for repo in repos:
    #handle pull requests by voting through the community garden robot
    robot.voteOnPRs(repo)
    #fix any broken image links in the repo README files
    if weShouldCheckImageLinks:
        robot.fixImageLinks(repo)

org = g.get_organization('MaslowCNC')
repos = org.get_repos()

for repo in repos:
    #handle pull requests by voting through the community garden robot
    robot.voteOnPRs(repo)
    #fix any broken image links in the repo README files
    if weShouldCheckImageLinks:
        robot.fixImageLinks(repo)