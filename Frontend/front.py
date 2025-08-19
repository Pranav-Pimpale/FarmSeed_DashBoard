import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:5000"

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "register_mode" not in st.session_state:
    st.session_state.register_mode = False

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:

    if not st.session_state.register_mode:
        # Login screen
        st.title("🌱 Seed Manager - Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state.logged_in = True
                if username == "admin" and password == "1234":
                    st.session_state.role = "admin"
                else:
                    st.session_state.role = "user"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

        if st.button("Register new user"):
            st.session_state.register_mode = True
            st.rerun()

    else:
        # Register screen
        st.title("🌱 Seed Manager - Register New User")
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if not new_username or not new_password:
                st.warning("Please enter both username and password")
            elif new_password != confirm_password:
                st.warning("Passwords do not match")
            else:
                res = requests.post(f"{BASE_URL}/register", json={"username": new_username, "password": new_password})
                if res.status_code == 200:
                    st.success("Registration successful! You can now login.")
                    st.session_state.register_mode = False
                    st.rerun()
                elif res.status_code == 409:
                    st.error("Username already exists. Please choose another.")
                else:
                    st.error("Registration failed.")

        if st.button("Back to Login"):
            st.session_state.register_mode = False
            st.rerun()

    st.stop()

# ---------------- LOGOUT BUTTON ----------------
if st.session_state.logged_in:
    st.sidebar.write(f"Logged in as: **{st.session_state.role.upper()}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

# ---------------- NAVIGATION ----------------
if st.session_state.role == "admin":
    page = st.sidebar.radio("Go to", ["View Seeds", "Add Seed", "Update Seed", "Delete Seed", "Feedback"])
else:
    page = st.sidebar.radio("Go to", ["View Seeds", "Feedback"])

# ---------------- VIEW SEEDS ----------------
if page == "View Seeds":
    st.title("All Seeds")
    res = requests.get(f"{BASE_URL}/seeds")
    if res.ok:
        seeds = res.json()
        if seeds:
            df = pd.DataFrame(seeds)
            df['Info'] = df['name'].apply(
                lambda x: f'<a href="https://www.google.com/search?q={x.replace(" ", "+")}" target="_blank">Click Here</a>'
            )
            st.markdown(
                """
                <style>
                table {
                    width: 100% !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.write(df[['id', 'name', 'price', 'Info']].to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No seeds found.")
    else:
        st.error("Failed to fetch seeds.")

# ---------------- ADD SEED (Admin Only) ----------------
elif page == "Add Seed" and st.session_state.role == "admin":
    st.title("Add New Seed")
    seed_id = st.text_input("Seed ID")
    name = st.text_input("Seed Name")
    price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f")

    if st.button("Add Seed"):
        if seed_id.strip() == "" or name.strip() == "":
            st.warning("Please enter both Seed ID and Seed Name.")
        elif not seed_id.isdigit():
            st.warning("Seed ID must be numeric.")
        else:
            new_seed = {"id": int(seed_id), "name": name, "price": price}
            res = requests.post(f"{BASE_URL}/seeds", json=new_seed)
            if res.status_code in (200, 201):
                st.success("Seed added successfully!")
                st.rerun()
            else:
                st.error("Failed to add seed.")

# ---------------- UPDATE SEED (Admin Only) ----------------
elif page == "Update Seed" and st.session_state.role == "admin":
    st.title("Update Seed")
    res = requests.get(f"{BASE_URL}/seeds")
    if res.ok:
        seeds = res.json()
        if seeds:
            seed_map = {f"{s['id']} - {s['name']}": s for s in seeds}
            selected = st.selectbox("Select Seed to Update", list(seed_map.keys()))
            seed = seed_map[selected]
            new_name = st.text_input("New Name", seed["name"])
            new_price = st.number_input("New Price", value=float(seed["price"]), step=0.01, format="%.2f")

            if st.button("Update Seed"):
                updated_seed = {"name": new_name, "price": new_price}
                res = requests.put(f"{BASE_URL}/seeds/{seed['id']}", json=updated_seed)
                if res.ok:
                    st.success("Seed updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update seed.")
        else:
            st.info("No seeds available to update.")
    else:
        st.error("Failed to fetch seeds.")

# ---------------- DELETE SEED (Admin Only) ----------------
elif page == "Delete Seed" and st.session_state.role == "admin":
    st.title("Delete Seed")
    seed_id = st.text_input("Enter Seed ID to delete")

    if st.button("Delete Seed"):
        if seed_id.isdigit():
            res = requests.delete(f"{BASE_URL}/seeds/{seed_id}")
            if res.ok:
                st.success(f"Seed with ID {seed_id} deleted successfully!")
                st.rerun()
            else:
                st.error(f"Failed to delete seed with ID {seed_id}.")
        else:
            st.warning("Please enter a valid numeric Seed ID.")

# ---------------- FEEDBACK (Users submit / Admin view) ----------------
elif page == "Feedback":
    if st.session_state.role == "admin":
        st.title("All User Feedback")
        res = requests.get(f"{BASE_URL}/feedbacks", params={"username": "admin", "password": "1234"})
        if res.ok:
            feedbacks = res.json()
            if feedbacks:
                df = pd.DataFrame(feedbacks)
                # ✅ Ensure order: User first, then Comment
                df = df[["user", "comment"]]
                st.table(df)
            else:
                st.info("No feedback found.")
        else:
            st.error("Failed to fetch feedback.")
    else:
        st.title("Submit Feedback")
        user = st.text_input("Your Name")
        comment = st.text_area("Your Feedback")

        if st.button("Submit Feedback"):
            if user and comment:
                data = {"user": user, "comment": comment}
                res = requests.post(f"{BASE_URL}/feedback", json=data)
                if res.ok:
                    st.success("Thank you for your feedback!")
                else:
                    st.error("Failed to submit feedback.")
            else:
                st.warning("Please enter your name and feedback.")
