import streamlit as st
import hashlib
import pandas as pd
import requests
import plotly.express as px

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

# DB Custom Functions

def signup():
	st.subheader("Account Creation")
	new_name = st.text_input("Enter your name")
	new_first_name = st.text_input("Enter your first name")
	new_user = st.text_input('Username')
	new_passwd = st.text_input('Password',type='password')
  
	if st.button('Submit'):
		create_usertable()
		add_userdata(new_name, new_first_name, new_user,make_hashes(new_passwd))
		st.success("You have successfully created an account. Go to the Login Menu to login")
  
def add_patient():
	st.subheader("Add a patient account")
	new_name = st.text_input("Enter your patient name")
	new_first_name = st.text_input("Enter your patient first name")
	new_user = st.text_input('Patient Username')
	new_passwd = st.text_input('Patient Password',type='password')
  
	if st.button('Submit'):
		create_usertable()
		add_userdata(new_name, new_first_name, new_user,make_hashes(new_passwd))
		st.success("You have successfully added or created an account. Go to the Login Menu to login")

def form(username):
    st.write("Enter your feelings")
    with st.form(key = "information form"):
        
        date = st.date_input("Enter the date : ")
        thoughts = st.text_area("Write what you have to say ")
        submission = st.form_submit_button(label = "submit")

        if submission == True:
            x= requests.post('https://apiprediction.azurewebsites.net/predict', json={"thoughts": thoughts})
            sentiment = x.text
            add_data(username,date,thoughts, sentiment)
            
            
def add_data(a,b,h,d):
    c.execute("""CREATE TABLE IF NOT EXISTS thoughts_form(USERNAME TEXT(50), DATE TEXT(50), THOUGHTS TEXT(500), SENTIMENT TEXT(50));""")
    c.execute("INSERT INTO thoughts_form SELECT ?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM thoughts_form WHERE username= ? AND date = ?)",(a,b,h,d,a,b))
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
					task_patient = st.selectbox("Task",["Add Text","Modify Text", "See my texts"])
					if task_patient =='Add Text':
						form(username)
						
					elif task_patient == 'Modify Text':
						date = st.date_input("Enter the date : ")
						new_text = st.text_area("Write what you have to say ")
						submit = st.button(label = "submit")
						if submit:
							x= requests.post('https://apiprediction.azurewebsites.net/predict', json={"thoughts": new_text})
							prediction = x.text	      
							c.execute("UPDATE thoughts_form SET THOUGHTS = ?, SENTIMENT =? WHERE DATE = ?",(new_text,prediction,date))
							conn.commit()
							conn.close()
							st.success("Successfully added")

					elif task_patient == 'See my texts':
						date_see = st.date_input("Enter the date of your post : ")
						c.execute("SELECT thoughts FROM thoughts_form WHERE USERNAME = ? AND DATE=?",(username,date_see))
						my_thoughts = c.fetchall()
						clean_db_thoughts = pd.DataFrame(my_thoughts)
						st.dataframe(clean_db_thoughts)
      
					
				elif check_status(username) == "doctor":
					task = st.selectbox("Task",["Profiles", "Thoughts","Add Patient", "Modify Patient Infos", "Show Wheel"])
      
					if task == "Profiles":
						st.subheader("User Profiles")
						user_table = view_all_users()
						clean_db_1 = pd.DataFrame(user_table,columns=["name", "firstname","Username","Password","Status"])
						st.dataframe(clean_db_1)
      
					elif task == "Thoughts":
						st.subheader("User Thoughts")
						user_thoughts = view_all_thoughts()
						clean_db_2 = pd.DataFrame(user_thoughts,columns=["Username", "Date","Thoughts","Sentiment"])
						st.dataframe(clean_db_2)
      
					elif task == "Add Patient":
						add_patient()
								
					elif task == "Modify Patient Infos":
						selected_user = st.text_input('Chose the username of the patient')
						updated_name = st.text_input('Enter the new name')
						updated_first_name = st.text_input('Enter the new first name')
						submission = st.button(label = "Submit new entries")

						if submission == True:
							c.execute("UPDATE userstable SET name = ?, firstname = ? where username = ?",(updated_name, updated_first_name,selected_user))
       
					elif task == "Show Wheel":
						user_or_name = st.selectbox("How do you want to select",["Username","Name and First Name"])
						if user_or_name == "Username":
							wheel_username = st.text_input('Show wheel for this username')
							first_date = st.date_input('Chose first date')
							second_date = st.date_input('Chose second date')
							submit_year = st.button(label = "Submit year")
							if submit_year:
								if first_date == second_date :
									c.execute("SELECT username,sentiment,count(sentiment) FROM thoughts_form WHERE username = ? AND date = ? GROUP BY sentiment",(wheel_username,first_date))
									thoughts_year = c.fetchall()
									between_year_df = pd.DataFrame(thoughts_year, columns=["username","sentiment","count"])
									fig = px.pie(between_year_df, values = "count",names="sentiment" )
									st.plotly_chart(fig, use_container_width=True)

								else:
									c.execute("SELECT username,sentiment,count(sentiment) FROM thoughts_form WHERE username = ? AND date between ? and ? GROUP BY sentiment",(wheel_username,first_date,second_date))
									thoughts_year = c.fetchall()
									between_year_df = pd.DataFrame(thoughts_year, columns=["username","sentiment","count"])
									fig = px.pie(between_year_df, values = "count",names="sentiment" )
									st.plotly_chart(fig, use_container_width=True)
         
						elif user_or_name == "Name and First Name":
							wheel_name = st.text_input('Show wheel for this user name')
							wheel_first_name = st.text_input('Show wheel for this user first name')
							first_date = st.date_input('Chose first date')
							second_date = st.date_input('Chose second date')
							submit_year = st.button(label = "Submit year")
							if submit_year:
								if first_date == second_date :
									c.execute("SELECT username,sentiment,count(sentiment) FROM thoughts_form natural join userstable WHERE name=? and firstname=? AND date = ? GROUP BY sentiment",(wheel_name,wheel_first_name,first_date))
									thoughts_year = c.fetchall()
									between_year_df = pd.DataFrame(thoughts_year, columns=["username","sentiment","count"])
									fig = px.pie(between_year_df, values = "count",names="sentiment" )
									st.plotly_chart(fig, use_container_width=True)

								else:
									c.execute("SELECT username,sentiment,count(sentiment) FROM thoughts_form natural join userstable WHERE name=? and firstname=? AND date between ? and ? GROUP BY sentiment",(wheel_name,wheel_first_name,first_date,second_date))
									thoughts_year = c.fetchall()
									between_year_df = pd.DataFrame(thoughts_year, columns=["username","sentiment","count"])
									fig = px.pie(between_year_df, values = "count",names="sentiment" )
									st.plotly_chart(fig, use_container_width=True)

			else:
				st.warning("Incorrect Username/Password")
    
	elif choice == "SignUp":
		signup()
		
if __name__ == '__main__':
	main()