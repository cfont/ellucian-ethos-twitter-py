# Written for Python 3
#
# This is the SUBSCRIBING Ethos App that will consume Academic Program data changes
# and post a tweet to twitter
#
import time, pprint, json, configparser

# import the twitter required libraries which requires pip3 install
import tweepy

# import custom class
from ethos import Ethos

config = configparser.ConfigParser()
config.read('config.ini')

ethosApiKey = config.get('ETHOS','API_KEY')
twitterConsumerKey = config.get('TWITTER','consumer_key')
twitterConsumerSecret = config.get('TWITTER','consumer_secret')
twitterAccessToken = config.get('TWITTER','access_token')
twitterAccessTokenSecret = config.get('TWITTER','access_token_secret')

def main():
    print('Starting Ethos Tweeting System')

    ethos = Ethos(ethosApiKey)

    while True:

        print('Checking for change notifications in Ethos Integration')
        data = ethos.get_change_notifications()

        if data and len(data) > 0:
            process_change_notifications(data)
        else:
            print('No change notifications available')

        # uncomment the wait loop for demo purposes    
        wait_seconds = 5
        print('Waiting for {seconds} seconds...\n'.format(seconds=wait_seconds))
        time.sleep(wait_seconds)

def process_change_notifications(data):
    print('Received {count} change notifications'.format(count=len(data)))
    print('Here is the entire returned data set:')
    print(data)
    print('Now we will iterate through all of those received messages: ')

    # loop through returned data but only tweet new sections
    for d in data:
        print('Here is a message:')
        pprint.pprint(d) # changed data to d because upon startup it will print all messages every time this gets looped through
        
        if d['resource']['name'] == 'academic-programs': 
            tweetNewAcademicProgram(d)

        elif d['resource']['name'] == 'sections': 
            tweetNewCourseSection(d)

        else:
            print ('There was a change to some data model resource published through Ethos, but it is not one that we support, so we will ignore it. In the future we may handle this differently') 
 
def tweetNewAcademicProgram(d):
    if d['operation'] == 'replaced' or d['operation'] == 'created':    #only tweet new and updated Academic Program info
        if d['resource']['version'] == 'application/vnd.hedtech.integration.v15+json': #only want version 15 of this Ethos Data Model 

            print('Received new or updated academic program info for '+d['content']['title']+' with Code '+d['content']['code'])
            #TODO: get term code description somehow

            # Pass the required data pieces to the tweet function
            send_tweet('academicProgram',d['content']['title'])
        else: 
            print('Ethos sent a version of the academic-programs data model this program does not support. In the future we will get the correct version.')
    else:
        print('There was a change to an academic-programs data model resource published through Ethos, but it is not for a new or update/replace operation, so we will ignore it. In the future we may handle this differently.')

def tweetNewCourseSection(d):
    if d['operation'] == 'created':    #only tweet new Course Section info
        if d['resource']['version'] == 'application/vnd.hedtech.integration.v16.0.0+json': #only want version 15 of this Ethos Data Model 

            print('Received new or updated course section info for '+d['content']['titles'][0]['value']+' with Section Code '+d['content']['code'])
            #TODO: get term code description somehow

            # Pass the required data pieces to the tweet function
            send_tweet('courseSection',d['content']['titles'][0]['value'])
        else: 
            print('Ethos sent a version of the sections data model this program does not support. In the future we will get the correct version.')
    else:
        print('There was a change to a sections data model resource published through Ethos, but it is not for a new/created operation, so we will ignore it. In the future we may handle this differently.')

def send_tweet(eeDmResource,eeDmTitle):
    # print('DEBUG entering send_tweet')
    print('DEBUG twitter consumer key: ' + twitterConsumerKey)
    
    # Set up OAuth and integrate with API
    auth = tweepy.OAuthHandler(twitterConsumerKey, twitterConsumerSecret)
    auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)

    api = tweepy.API(auth)

    if eeDmResource == 'courseSection':
        tweet = "We are pleased to inform you that a new section of "+eeDmTitle+" has recently been added for the **Fall 2018**.  For additional details or to register, please go to https://www.ellucian.com" 

    elif eeDmResource == 'academicProgram':
        tweet ="We are pleased to offer you a new program in "+eeDmTitle+" beginning in the **Fall 2019**.  If you need additional details or are interested in the program, please contact your advisor."

    else:
        print('We received a request to send a tweet for something we did not understand. The Ethos Data Model resource identified as '+eeDmResource+' and the title as '+eeDmTitle+'.')
        tweet = 'Something did not work as expected. Please check the logs.'
        # In a production environment we may not want to actually post this tweet to the world wide webs on the internets for the kids to see
    
    # send the tweet
    api.update_status(status=tweet)
   
    print('DEBUG exiting send_tweet function after posting ' + tweet)


if __name__ == '__main__':
    main()
