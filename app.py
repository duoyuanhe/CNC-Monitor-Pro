import streamlit as st
from multiapp import MultiApp
from apps import home, Top_issue_FAI, Top_issue_CNC, hourly_basis  # import your app modules here

app = MultiApp()

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Top_issue_FAI", Top_issue_FAI.app)
app.add_app("Top_issue_CNC", Top_issue_CNC.app)
app.add_app("FAI/IPQC review", hourly_basis.app)

# The main app
app.run()
