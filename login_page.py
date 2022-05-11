# Security
#passlib,hashlib,bcrypt,scrypt
import streamlit as st
import hashlib
import pandas as pd
import requests


def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

# DB Management

import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions

def form(username):
    st.write("Enter your feelings")
    with st.form(key = "information form"):
        
        date = st.date_input("Enter the date : ")
        thoughts = st.text_area("Write what you have to say ")
        submission = st.form_submit_button(label = "submit")

        if submission == True:
            x= requests.post('https://apiprediction.azurewebsites.net/predict', json={"thoughts": thoughts})
            prediction = x.text
            print(prediction)
            sentiment = prediction            
            add_data(username,date,thoughts, sentiment)
            
            
            
def add_data(a,b,h,d):
    c.execute("""CREATE TABLE IF NOT EXISTS thoughts_form(USERNAME TEXT(50), DATE TEXT(50), THOUGHTS TEXT(500), SENTIMENT TEXT(50));""")
    c.execute("INSERT INTO thoughts_form VALUES (?,?,?,?)", (a,b,h,d))
    conn.commit()
    conn.close()
    st.success("Successfully added")
    
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(NAME TEXT(50), FIRSTNAME TEXT(50),username TEXT,password TEXT, status TEXT)')


def add_userdata(name,firstname,username,password):
	c.execute('INSERT INTO userstable(name,firstname,username,password, status) VALUES (?,?,?,?,?)',(name,firstname,username,password, "patient"))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def check_status(username):
	status = c.execute('SELECT status FROM userstable WHERE username=?',(username,))
	status = status.fetchone()[0]
	return status

def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def view_all_thoughts():
	c.execute('SELECT * FROM thoughts_form')
	data = c.fetchall()
	return data



def main():
	"""Write about your feelings"""

	st.title("User page")

	menu = ["Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)
 
	if choice == "Login":
		st.subheader("View your account information")

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):

			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:
				
				if check_status(username) == "patient":
					st.success("Logged In as {}".format(username))
		
					form(username)
		
				elif check_status(username) == "doctor":
					task = st.selectbox("Task",["Analytics","Profiles", "Thoughts"])
					if task == "Analytics":
						st.subheader("Analytics")
      
					elif task == "Profiles":
						st.subheader("User Profiles")
						user_table = view_all_users()
						clean_db_1 = pd.DataFrame(user_table,columns=["name", "firstname","Username","Password","Status"])
						st.dataframe(clean_db_1)
      
					elif task == "Thoughts":
						st.subheader("User Thoughts")
						user_thoughts = view_all_thoughts()
						clean_db_2 = pd.DataFrame(user_thoughts,columns=["Username", "Date","Thoughts","Sentiment"])
						st.dataframe(clean_db_2)
					
			else:
				st.warning("Incorrect Username/Password")
    
	elif choice == "SignUp":
		st.subheader("Create an Account")
		new_name = st.text_input("Enter your name")
		new_first_name = st.text_input("Enter your first name")
		new_user = st.text_input('Username')
		new_passwd = st.text_input('Password',type='password')
  
		if st.button('SignUp'):
			create_usertable()
			add_userdata(new_name, new_first_name, new_user,make_hashes(new_passwd))
			st.success("You have successfully created an account.Go to the Login Menu to login")




if __name__ == '__main__':
	main()