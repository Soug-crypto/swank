import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth


# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)


st.metric('Version', '0.4.1')

st.code(f"""
Credentials:

First name: {config['credentials']['usernames']['jsmith']['first_name']}
Last name: {config['credentials']['usernames']['jsmith']['last_name']}
Username: jsmith
Password: {'abc' if 'pp' not in config['credentials']['usernames']['jsmith'].keys() else config['credentials']['usernames']['jsmith']['pp']}

First name: {config['credentials']['usernames']['rbriggs']['first_name']}
Last name: {config['credentials']['usernames']['rbriggs']['last_name']}
Username: rbriggs
Password: {'def' if 'pp' not in config['credentials']['usernames']['rbriggs'].keys() else config['credentials']['usernames']['rbriggs']['pp']}
"""
)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# authenticator = stauth.Authenticate(
#     '../config.yaml'
# )

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    st.write('___')
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')    
    st.write('___')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


# import streamlit as st
# import yaml
# from yaml.loader import SafeLoader
# import streamlit_authenticator as stauth

# # Load configuration
# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

# # stauth.Hasher.hash_passwords(config['credentials'])

# # Initialize authenticator
# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
# )

# # Initialize session state
# if 'authentication_status' not in st.session_state:
#     st.session_state['authentication_status'] = None
# if 'show_login' not in st.session_state:
#     st.session_state['show_login'] = True

# def login():
#     """Displays the login widget and updates session state on successful login."""
#     if st.session_state['show_login']:
#         name, authentication_status, username = authenticator.login()

#         if authentication_status:
#             st.session_state['name'] = name
#             st.session_state['username'] = username
#             st.session_state['role'] = config['credentials']['usernames'][username]['role']
#             st.session_state['authentication_status'] = True
#             st.session_state['show_login'] = False  # Hide login form after successful login
#             st.success(f"Welcome, {name}!")
#         elif not authentication_status:
#             st.error("Invalid username or password. Please try again.")
#         else:
#             st.warning("Please enter your credentials.")

# # Initialize session state
# if 'authentication_status' not in st.session_state:
#     st.session_state['authentication_status'] = None
# if 'show_login' not in st.session_state:
#     st.session_state['show_login'] = True

# def login():
#     """Displays the login widget and updates session state on successful login."""
#     if st.session_state.get('show_login', True):
#         name, authentication_status, username = authenticator.login()

#         print(" name, authentication_status, username",  name, authentication_status, username)
#         # Handle login results
#         if authentication_status:
#             # Set session state on successful login
#             st.session_state['name'] = name
#             st.session_state['username'] = username
#             st.session_state['role'] = config['credentials']['usernames'][username]['role']
#             st.session_state['authentication_status'] = True
#             st.session_state['show_login'] = False
#             st.success(f"Welcome, {name}!")
#         elif authentication_status is False:
#             st.error("Invalid username or password. Please try again.")
#         # else:
#         #     st.warning("Please enter your credentials.")


# def logout():
#     """Provides logout functionality."""
#     if st.session_state.get('authentication_status'):
#         authenticator.logout("Logout", "sidebar")
#         st.session_state.clear()
#         st.session_state['show_login'] = True
#         st.success("You have been logged out.")

# def is_authenticated():
#     """Returns True if the user is authenticated."""
#     return st.session_state.get('authentication_status', False)

# def has_access(required_role):
#     """Checks if the user has the required role."""
#     user_role = st.session_state.get('role')
#     return user_role == required_role or (required_role == "user" and user_role in ["admin", "user"])

# def require_role(required_role, message="You do not have access to this section."):
#     """Halts execution if the user lacks the required role."""
#     if not has_access(required_role):
#         st.warning(message)
#         st.stop()

# # Display login form if not authenticated
# if st.session_state['show_login']:
#     login()

# # Main application logic
# if is_authenticated():
#     st.sidebar.success(f"Welcome back, {st.session_state['name']}!")

#     # Navigation options
#     page = st.sidebar.radio("Select Page", ["Home", "Admin Page", "User Page", "Restricted Page"])

#     if page == "Home":
#         st.title("Home")
#         st.write("Welcome to the homepage! Explore the application.")

#     elif page == "Admin Page":
#         require_role("admin")
#         st.title("Admin Page")
#         st.write("Admin-specific content here.")

#     elif page == "User Page":
#         require_role("user")
#         st.title("User Page")
#         st.write("Content for general users and admins.")

#     elif page == "Restricted Page":
#         require_role("restricted")
#         st.title("Restricted Page")
#         st.write("Restricted content for specific users.")

#     # Add logout option
#     logout()

# elif st.session_state['authentication_status'] == False:
#     st.error("Username/password is incorrect. Please try again.")

# elif st.session_state['authentication_status'] is None:
#     st.warning("🔒 Please log in to view the content.")
#     st.write("To access the features of this application, please enter your credentials.")
