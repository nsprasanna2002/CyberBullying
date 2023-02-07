# twitter cyberbullying detection using machine learning

import pandas as pd
import numpy as np
import joblib
import pickle
import streamlit as st
import hashlib
from stop_words import get_stop_words
import datetime

import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()

stop_words = get_stop_words('english')
stopwords = set(stop_words)

model = joblib.load('./cb_sgd_final.sav')
vectorizer = pickle.load(open('./cv.pkl', 'rb'))

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def predict(text):
    text = text.replace("@", " ")
    text = text.replace("#", " ")
    text = text.replace("RT", " ")
    text = text.replace(":", " ")
    #text = text.replace(";", " ")
    text = text.replace(",", " ")
    text = text.replace(".", " ")
    text = text.replace("!", " ")
    text = text.replace("?", " ")
    text = text.lower()
    text = str(text)
    text = text.split()
    text = [word for word in text if word not in stopwords]
    text = ' '.join(text)
    text = [text]
    text1 = vectorizer.transform(text)
    return model.predict(text1)

# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def create_tweettable():
	c.execute('CREATE TABLE IF NOT EXISTS tweettable(username TEXT,tweet TEXT,result TEXT,date TEXT)')

def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()


def add_tweet(username, tweet, result, date):
	c.execute('INSERT INTO tweettable(username,tweet,result,date) VALUES (?,?,?,?)',(username,tweet,result,date))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data


def view_all_tweet():
	c.execute('SELECT * FROM tweettable')
	dat = c.fetchall()
	return dat

def main():
    st.title("Twitter Cyberbullying Detection")
    menu = ["AdminPage", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "AdminPage":
        st.subheader("Admin Page")
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            if username == 'admin' and password == 'admin':
                st.success("Logged In as {}".format(username))

                task = st.selectbox("Task", ["View Tweets", "View Users"])
                if task == "View Tweets":
                    st.subheader("View Tweets")
                    tweet_result = view_all_tweet()
                    clean_db = pd.DataFrame(tweet_result, columns=["User", "Tweet", "Result", "Date"])
                    st.dataframe(clean_db)

                elif task == "View Users":
                    st.subheader("View Users")
                    user_result = view_all_users()
                    clean_db = pd.DataFrame(user_result, columns=["User", "Password"])
                    st.dataframe(clean_db)
            
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            hashed_pswd = make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:
                st.success("Logged In as {}".format(username))

                tweet = st.text_area("Tweet")

                if st.button("Submit"):
                    create_tweettable()
                    result = predict(tweet)
                    date = datetime.datetime.now()
                    if result == 1:
                        result = "Cyberbullying"
                    else:
                        result = "Non-Cyberbullying"
                    
                    add_tweet(username, tweet, result, date)
                    st.success("Tweeted Successfully")
                
                tweet_result = view_all_tweet()
                clean_db = pd.DataFrame(tweet_result, columns=["User", "Tweet", "Result", "Date"])
                st.write("Most Recent Tweet")
                clean_db = clean_db[['User', 'Tweet','Date']]
                st.dataframe(clean_db)


            else:
                st.warning("Incorrect Username/Password")
            
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Signup"):
            create_usertable()
            hashed_new_password = make_hashes(new_password)
            add_userdata(new_user,hashed_new_password)
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

if __name__ == '__main__':
    main()