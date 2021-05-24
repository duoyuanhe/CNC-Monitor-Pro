import streamlit as st
from multiapp import MultiApp
# import your app modules here
from apps import home, Top_issue_FAI, Top_issue_CNC, hourly_basis, IPQC_efficiency_check

app = MultiApp()

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Top_issue_FAI", Top_issue_FAI.app)
app.add_app("Top_issue_CNC", Top_issue_CNC.app)
app.add_app("FAI/IPQC review", hourly_basis.app)
app.add_app('IPQC_efficiency_check', IPQC_efficiency_check.app)

# The main app
app.run()
