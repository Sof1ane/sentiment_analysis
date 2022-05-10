# Security
#passlib,hashlib,bcrypt,scrypt
import streamlit as st
import hashlib
import pandas as pd


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

def form():
    st.write("Enter your feelings")
    with st.form(key = "information form"):
        name = st.text_input("Enter your name")
        first_name = st.text_input("Enter your first name")
        date = st.date_input("Enter the date : ")
        thoughts = st.text_area("Write what you have to say ")
        submission = st.form_submit_button(label = "submit")
        
        if submission == True:
            
            sentiment = "triste"
            add_data(name, first_name, date,thoughts, sentiment)
            
            
            
def add_data(a,b,h,d,e):
    c.execute("""CREATE TABLE IF NOT EXISTS thoughts_form(NAME TEXT(50), FIRSTNAME TEXT(50), DATE TEXT(50), THOUGHTS TEXT(500), SENTIMENT TEXT(50));""")
    c.execute("INSERT INTO thoughts_form VALUES (?,?,?,?,?)", (a,b,h,d,e))
    conn.commit()
    conn.close()
    st.success("Successfully added")
    
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data



def main():
	"""Simple Login App"""

	st.title("Simple Login App")

	menu = ["Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)
 
	if choice == "Login":
		st.subheader("Login Section")

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:
				st.success("Logged In as {}".format(username))
    

				task = st.selectbox("Task",["Add Post","Analytics","Profiles"])
				if task == "Add Post":
					form()

				elif task == "Analytics":
					st.subheader("Analytics")
				elif task == "Profiles":
					st.subheader("User Profiles")
					user_result = view_all_users()
					clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
					st.dataframe(clean_db)
			else:
				st.warning("Incorrect Username/Password")
    
	elif choice == "SignUp":
		st.subheader("Create an Account")
		new_user = st.text_input('Username')
		new_passwd = st.text_input('Password',type='password')
  
		if st.button('SignUp'):
			create_usertable()
			add_userdata(new_user,make_hashes(new_passwd))
			st.success("You have successfully created an account.Go to the Login Menu to login")




if __name__ == '__main__':
	main()