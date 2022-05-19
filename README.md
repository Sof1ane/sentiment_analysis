# sentiment_analysis

# What is this app ?

This app was created to answer a doctor needs. In fact the doctor wanted to have a application that could predict his patients thoughts. The prediction is made through an API and is stored into the databases as well as the patients informations.

# What are the technologies ?
## SQL

Data is stored in a SQL database, there is 2 tables, the **users** one and **thoughts** one.

**Thoughts table** :
- Username(text)
- Date(date)
- Thoughts(text)
- Sentiment(text)

**Users table** :
- Name(text)
- Firstname(text)
- Username(text)
- Password(text)
- Status(text)

## API

You can find everything about the API used [here](https://github.com/theotrc/Api_Model_Sentiments)

## Streamlit

We used Streamlit as library for the frond end since the aim of the project was to focus more on the Machine Learning side.

See streamlit documentation [here](http://streamlit.io/)
