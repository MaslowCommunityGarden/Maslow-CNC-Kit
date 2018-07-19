from github     import Github
import          urllib2
import          datetime
import          pygit2
from robot      import Robot
import          random

# Login to github
g = Github("barboursmith", "ijustmadethis1up")
org = g.get_organization('MaslowCommunityGarden')
user = g.get_user()
repos = org.get_repos()

robot = Robot()

weShouldCheckImageLinks = True

for repo in repos:
    #handle pull requests by voting through the community garden robot
    robot.voteOnPRs(repo)
    #check image links
    if weShouldCheckImageLinks:
        robot.fixImageLinks(repo)

