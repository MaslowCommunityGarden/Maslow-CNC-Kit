from github     import Github
import          urllib2
import          datetime
import          pygit2
import          base64
import          json

class Robot:
    
    def voteOnPRs(self, repo):
        '''
        
        Runs to tally votes on open pull requests if the project is community managed
        
        '''
        try:
            #find the URL to the file
            trackedURL  = repo.html_url
            rawPath     = trackedURL.split('.com')[-1]
            rawPath     = "https://raw.githubusercontent.com" + rawPath
            rawPath     = rawPath.replace('\n', '')
            robotURL    = rawPath + '/master/ROBOT.md'
            robotURL    = "".join(robotURL.split())
            
            #read the file
            text        = urllib2.urlopen(robotURL)
            robotText   = text.read()
            
            projectIsCommunityManaged = False
            
            try:                                                        #Try to read the robot.md file as a json file
                data = json.loads(robotText)
                if data["ModerationLevel"] == 'communityManaged':
                    projectIsCommunityManaged = True
            except:                                                     #If it's not a json file fall back to the old technique
                if 'communityManaged' in robotText:
                    projectIsCommunityManaged = True
            
            #if the project is community managed we need to see if there are pull requests to merge
            if projectIsCommunityManaged:
                '''
                
                Check if there are any open pull requests that need to be voted on
                
                '''
                openPullRequests = repo.get_pulls()
                for pullRequest in openPullRequests:
                    
                    print "\n\n"+pullRequest.title
                    
                    pullRequestAlreadyRespondedTo = False
                    
                    prAsIssue = repo.get_issue(pullRequest.number)
                    comments  = prAsIssue.get_comments()  #this is a work around for a bug in pygithub. We have to use the issues API :rolleyes:
                    
                    #determine if the robot has already commented"
                    robotHasAlreadyCommented = False
                    for comment in comments:
                        
                        #if something has gone wrong and the robot was unable to merge the PR on the last try...skip it
                        if "Times up and" in comment.body:
                            break
                            
                        if 'Congratulations on the' in comment.body:
                            robotHasAlreadyCommented = True
                            
                            upVotes = 0
                            downVotes = 0
                            for reaction in comment.get_reactions():
                                if reaction.content == '+1':
                                    upVotes = upVotes + 1
                                if reaction.content == '-1':
                                    downVotes = downVotes + 1
                            
                            
                            timeOpened = pullRequest.created_at
                            
                            elapsedTime = (datetime.datetime.now() - timeOpened).total_seconds()
                            
                            
                            fourtyEightHoursInSeconds = 172800
                            if elapsedTime < fourtyEightHoursInSeconds:
                                pass
                            else:
                                if upVotes > downVotes:
                                    commentText = "Time is up and we're ready to merge this pull request. Great work!"
                                    theNewComment = prAsIssue.create_comment(commentText)
                                    pullRequest.merge()
                                else:
                                    commentText = "It looks like adding these changes right now isn't a good idea. Consider any feedback that the community has given about why not and feel free to open a new pull request with the changes"
                                    theNewComment = prAsIssue.create_comment(commentText)
                                    prAsIssue.edit(state='closed')
                    
                    if not robotHasAlreadyCommented:
                        commentText = "Congratulations on the pull request @" + pullRequest.user.login + "\n\n Now we need to decide as a community if we want to integrate these changes. Vote by giving this comment a thumbs up or a thumbs down. Votes are counted in 48 hours. Ties will not be merged.\n\nI'm just a robot, but I love to see people contributing so I'm going vote thumbs up!"
                        theNewComment = prAsIssue.create_comment(commentText)
                        theNewComment.create_reaction("+1")
                
                '''
                
                Check if there are any open pull requests that need to be voted on
                
                '''
                
                if 'delete' in robotText:
                    
                    #remove the string from the tracked projects list
                    newText = ""
                    with open("/var/www/html/trackedProjects.txt", "r") as f:
                        text = f.read()
                        newText = text.replace(repo.html_url,'')
                    with open("/var/www/html/trackedProjects.txt", "w") as f:
                        f.write(newText)
                    
                    #delete the repo
                    repo.delete()
                
            else:
                print "This project is not community managed"
        except Exception as e:
            print "This repo does not have a ROBOT.md file"
            print e
    
    def fixImageLinks(self,repo):
        
        #fix images in the README file
        self.fixImageLinksInOneFile(repo, '/README.md')
        #fix images in the INSTRUCTIONS file
        self.fixImageLinksInOneFile(repo, '/INSTRUCTIONS.md')
        #fix images in the BOM file
        self.fixImageLinksInOneFile(repo, '/BOM.md')
    
    def fixImageLinksInOneFile(self, repo, fileName):
        '''
        
        Detects and fixes if a file has an image link which won't render right in the community garden
        
        '''
        
        try:
        
            fileContents = repo.get_file_contents(fileName)
            
            fileText = base64.b64decode(fileContents.content)
            
            #print "string to replace: " #https://github.com/MaslowCommunityGarden/A-Simple-Night-Stand/blob/master/
            stringToReplace = 'https://github.com/' + repo.full_name + '/blob/master/'
            #print "String to replace it with: " #https://raw.githubusercontent.com/MaslowCommunityGarden/A-Simple-Night-Stand/master/
            replaceWithString = 'https://raw.githubusercontent.com/' + repo.full_name + '/master/'
            
            
            newFileText = fileText.replace(stringToReplace, replaceWithString)
            
            print repo.full_name
            print "We have made a change?"
            print fileText != newFileText
            
            if fileText != newFileText: #if we have fixed at least one link
                
                repo.update_file(fileName, "fix image links", newFileText, fileContents.sha)
        except:
            print "unable to update image links for" + str(repo.name)
    
    def acceptInvitations(self, user):
        '''
        
        Accept access to any repos that the robot has been invited to
        
        '''
        
        print user.get_invitations()
        
        