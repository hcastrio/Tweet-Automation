from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import gspread # pip install gspread

app = Flask(__name__)

gc = gspread.service_account(filename='gsheet_credentials.json') # connects to the sheets file
# found in the sheets url and opens sheets
sh = gc.open_by_key('1rYWa5e3eMmWp6LfOAsAeybRx0AZjZapUZcrG_3a0g60') 
worksheet = sh.sheet1 # locates our only worksheet

class Tweet:
    def __init__(self, message, time, done, row_idx): # same name as sheets file
        self.message = message
        self.time = time
        self.done = done
        self.row_idx = row_idx

def get_date_time(date_time_str):
    date_time_obj = None
    error_code = None
    try:
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e: # if not in correct format
        error_code = f'Error! {e}'
    
    if date_time_obj is not None: # if date is not in the future
        now_time_pst = datetime.utcnow() + timedelta(hours=-7) # always pst time
        if not date_time_obj > now_time_pst:
            error_code = "error! time must be in the future"
    return date_time_obj, error_code

@app.route('/')
def tweet_list():
    tweet_records = worksheet.get_all_records() # accesses the sheets file
    tweets = [] # list of tweets
    for idx, tweet in enumerate(tweet_records, start = 2):
        tweet = Tweet(**tweet, row_idx=idx) # creates a tweet
        tweets.append(tweet) # adds the tweet to the list

    tweets.reverse() # reverse the order of the list

                   # for each tweet in our list that is not done add 1
    n_open_tweets = sum(1 for tweet in tweets if not tweet.done)

    return render_template('base.html', tweets=tweets, n_open_tweets=n_open_tweets)

@app.route('/tweet', methods=['POST'])
def add_tweet():
    message = request.form['message']
    if not message:
        return "error! no message"
    time = request.form['time']
    if not time:
        return "error! no time"
    pw = request.form['pw2544']
    if not pw or pw != "12345":
        return "error! wrong password"

    if len(message) > 280: # twitter character limit
        return "error! message too long!"
    
    date_time_obj, error_code = get_date_time(time)
    if error_code is not None:
        return error_code

    tweet = [str(date_time_obj), message, 0]
    worksheet.append_row(tweet)
    return redirect('/')

    
@app.route('/delete/<int:row_idx>')
def delete_tweet(row_idx):  
    worksheet.delete_rows(row_idx)
    return redirect('/')