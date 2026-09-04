import streamlit as st
import pandas as pd
import matplotlib.pyplot as pl
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Dashboard", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ---------- BACKGROUND ----------
def set_gif_bg():
    gif_url = "https://cdn.dribbble.com/userupload/20481043/file/original-ff919c0d8190474293a4a448343b80e2.gif"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
                        url("{gif_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_gif_bg()

# ---------- SESSION CHECK ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.stop()

# ---------- SIDEBAR MENU ----------
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=[
            "Home",
            "Report an Issue",
            "Create & Invite",
            "Announcements",
            "My Profile",
            "Achievements",
            "Gallery",
            "About Voxlocal",
            "Logout"
        ],
        icons=["house", "plus-circle","envelope", "bell", "person","trophy","laptop", "info", "power"],
        default_index=0,
    )

# ---------- LOAD DATA ----------
@st.cache_data
def load_issues():
    try:
        return pd.read_csv("issues.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name","Issue","Status","Location","Description","Priority"])

# ---------- HOME ----------

if selected == "Home":
    st.title("Dashboard")
    st.markdown(f"Welcome, **{st.session_state.get('username','User')}** 👋")

    df = load_issues()

    if df.empty:
        st.warning("No issues reported yet.")
    else:
        st.subheader("📊 Overview")
        st.dataframe(df)

        # Metrics
        total = len(df)
        resolved = len(df[df["Status"] == "Resolved"])
        pending = len(df[df["Status"] == "Pending"])
        progress = len(df[df["Status"] == "In Progress"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Issues", total)
        col2.metric("Resolved", resolved)
        col3.metric("In Progress", progress)
        col4.metric("Pending", pending)

        # Pie Chart
        st.subheader("📌 Issue Distribution")
        issue_counts = df["Issue"].value_counts()

        fig, ax = pl.subplots(figsize=(4,4))
        fig.patch.set_facecolor("#DBD4D4")
        ax.pie(issue_counts, labels=issue_counts.index, autopct='%1.1f%%', radius=0.7)
        ax.axis("equal")

        st.pyplot(fig)

        # Bar Chart
        st.subheader("📈 Status Distribution")
        status_counts = df["Status"].value_counts()
        st.bar_chart(status_counts)

# ---------- REPORT ISSUE ----------
elif selected=="Report an Issue":
    st.subheader("📝 Report an Issue")
    if st.session_state.get("submitted",False):
        st.success("✅ Issue reported successfully!")
        del st.session_state["submitted"]
    with st.form("issue_form",clear_on_submit=True):
        name=st.text_input("Name *")
        issue=st.text_input("Issue *")
        location=st.text_input("Location *")
        description=st.text_area("Description *")
        priority=st.selectbox("Priority *",["Very High","High","Medium","Low","Very Low"])
        type_issue=st.selectbox("Type of Issue *",["Environment","Infrastructure","Health & Sanitation","Safety & Security","Education & Awareness","Social Welfare","Animal Welfare","Disaster Management","Technology","Community Activities","Others"])
        proof=st.file_uploader("Upload Proof of Issue *",type=["jpg","jpeg","png","pdf"])
        submit=st.form_submit_button("Submit")
        if submit:
            if not name.strip():
                st.error("⚠️ Please enter your name.")
            elif not issue.strip():
                st.error("⚠️ Please enter the issue.")
            elif not location.strip():
                st.error("⚠️ Please enter the location.")
            elif not description.strip():
                st.error("⚠️ Please enter a description.")
            elif not proof:
                st.error("⚠️ Please upload proof of the issue.")
            else:
                try:
                    import os
                    import pandas as pd
                    os.makedirs("proof_issue",exist_ok=True)
                    proof_path=os.path.join("proof_issue",proof.name)
                    with open(proof_path,"wb") as f:
                        f.write(proof.getbuffer())
                    new_data=pd.DataFrame({
                        "Name":[name.strip()],
                        "Issue":[issue.strip()],
                        "Type":[type_issue],
                        "Status":["Pending"],
                        "Location":[location.strip()],
                        "Description":[description.strip()],
                        "Priority":[priority],
                        "Proof":[proof_path]
                    })
                    if os.path.exists("issues.csv"):
                        df=pd.read_csv("issues.csv")
                    else:
                        df=pd.DataFrame(columns=["Name","Issue","Type","Status","Location","Description","Priority","Proof"])
                    df=pd.concat([df,new_data],ignore_index=True)
                    df.to_csv("issues.csv",index=False)
                    st.session_state["submitted"]=True
                    st.rerun()
                except Exception as e:
                    st.error("❌ An error occurred while submitting the issue.")
                    st.error(f"Error details: {e}")
                    
elif selected=="Create & Invite":
    st.subheader("📝 Invite others for your Programme")
    if st.session_state.get("submitted",False):
        st.success("✅ Programme published successfully!")
        del st.session_state["submitted"]
    with st.form("programme_form",clear_on_submit=True):
        name=st.text_input("Enter name of the programme:")
        date=st.date_input("Enter date:")
        venue=st.text_input("Enter venue:")
        description=st.text_area("Describe the programme:")
        link=st.text_input("Enter link for the participants registration:")
        submit=st.form_submit_button("Publish Programme")
        if submit:
            if not name.strip():
                st.error("⚠️ Please enter the programme name.")
            elif not venue.strip():
                st.error("⚠️ Please enter the venue.")
            elif not description.strip():
                st.error("⚠️ Please enter a description.")
            elif not link.strip():
                st.error("⚠️ Please enter the registration link.")
            else:
                try:
                    import os
                    import pandas as pd
                    if os.path.exists("programmes.csv"):
                        old_data=pd.read_csv("programmes.csv")
                    else:
                        old_data=pd.DataFrame(columns=["ID","Programme Name","Date","Venue","Description","Registration Link"])
                    if "ID" not in old_data.columns:
                        old_data["ID"]=range(1,len(old_data)+1)
                    old_data["ID"]=pd.to_numeric(old_data["ID"],errors="coerce").fillna(0).astype(int)
                    if len(old_data)>0:
                        new_id=old_data["ID"].max()+1
                    else:
                        new_id=1
                    new_programme=pd.DataFrame({
                        "ID":[new_id],
                        "Programme Name":[name.strip()],
                        "Date":[date],
                        "Venue":[venue.strip()],
                        "Description":[description.strip()],
                        "Registration Link":[link.strip()]
                    })
                    df=pd.concat([old_data,new_programme],ignore_index=True)
                    df.to_csv("programmes.csv",index=False)
                    st.session_state["submitted"]=True
                    st.rerun()
                except PermissionError:
                    st.error("❌ Permission denied. The programme could not be saved.")
                except pd.errors.EmptyDataError:
                    st.error("❌ programmes.csv is empty or corrupted.")
                except Exception as e:
                    st.error("❌ An error occurred while publishing the programme.")
                    st.error(f"Error details: {e}")
# ---------- JOIN PROGRAMMES ----------
elif selected == "Announcements":
    programme_option = st.selectbox(label="Choose an Option",options=["View Programmes","My Joined Programmes"])

    if programme_option == "View Programmes":
        try:
            df = pd.read_csv("programmes.csv")
        except FileNotFoundError:
            st.warning("No programmes available.")
            st.stop()

        sort_option = st.selectbox("Sort programmes by:",["Newest","Oldest","Name","Venue"])

        if sort_option == "Newest":
            df = df.sort_values(by="Date",ascending=False)
        elif sort_option == "Oldest":
            df = df.sort_values(by="Date",ascending=True)
        elif sort_option == "Name":
            df = df.sort_values(by="Programme Name")
        elif sort_option == "Venue":
            df = df.sort_values(by="Venue")

        st.markdown("""
        <style>
        .card{
            background-color:rgba(255,255,255,0.9);
            padding:20px;
            border-radius:15px;
            margin-bottom:15px;
            box-shadow:2px 2px 10px rgba(0,0,0,0.2);}
        .title{
            font-size:20px;
            font-weight:bold;
            color:#333;}
        .info{
            font-size:14px;
            color:#555;}
        </style>
        """,unsafe_allow_html=True)

        for i,row in df.iterrows():
            st.markdown(f"""
            <div class="card">
            <div class="title">{row['Programme Name']}</div>
            <div class="info">📅 <b>Date:</b> {row['Date']}</div>
            <div class="info">📍 <b>Venue:</b> {row['Venue']}</div>
            <div class="info">📝 {row['Description']}</div>
            <br>
            <a href="{row['Registration Link']}" target="_blank">
            <button style="background-color:#4CAF50;color:white;border:none;padding:10px 15px;border-radius:8px;">
            🔗 Join Programme
            </button>
            </a>
            </div>
            """,unsafe_allow_html=True)


    elif programme_option == "My Joined Programmes":

        st.header("🤝 Joined Programme Registration")

        if "joined" in st.session_state:
            st.success("✅ Programme registration submitted! Check Achievements for further confirmation")
            del st.session_state["joined"]


        # LOAD CATEGORY AND ISSUES

        try:
            programme_df = pd.read_csv("programmesandty.csv")

            programme_df["category"] = programme_df["category"].str.strip()
            programme_df["issue_name"] = programme_df["issue_name"].str.strip()

        except FileNotFoundError:
            st.error("programmesandty.csv not found")
            st.stop()


        # CATEGORY SELECTBOX

        programme_type = st.selectbox(
            "Programme Type",
            programme_df["category"].unique()
        )


        # FILTER ISSUE BASED ON CATEGORY

        related_issues = programme_df[
            programme_df["category"] == programme_type
        ]["issue_name"].tolist()


        # ISSUE SELECTBOX

        issue = st.selectbox(
            "Related Issue",
            related_issues
        )


        with st.form("programme_form",clear_on_submit=True):

            username = st.session_state.get("username","")

            st.text_input("Username",value=username,disabled=True)

            programmename = st.text_input("Programme Name")

            datejoined = st.date_input("Date of Registration")

            programdate = st.date_input("Programme Date")


            venue = st.text_input("Venue")


            proof = st.file_uploader(
                "Upload Proof of Participation",
                type=["jpg","jpeg","png","pdf"]
            )


            submit = st.form_submit_button("✅ Submit")


            if submit:

                if not programmename or proof is None:
                    st.error("⚠️ Please enter programme name and upload proof.")

                else:

                    import os

                    if not os.path.exists("proofs"):
                        os.makedirs("proofs")


                    proof_path = "proofs/"+proof.name


                    with open(proof_path,"wb") as f:
                        f.write(proof.getbuffer())


                    new_data = pd.DataFrame({
                        "username":[username],
                        "programme name":[programmename],
                        "Date Joined":[datejoined],
                        "Programme Date":[programdate],
                        "Type":[programme_type],
                        "Issue":[issue],
                        "Venue":[venue],
                        "Proof":[proof.name],
                        "Status":["Pending Verification"]
                    })


                    try:
                        joined = pd.read_csv("joined_programmes.csv")
                        joined = pd.concat([joined,new_data],ignore_index=True)

                    except FileNotFoundError:
                        joined = new_data


                    joined.to_csv("joined_programmes.csv",index=False)


                    st.session_state["joined"] = True
                    st.rerun()
# ---------- PROFILE ----------
elif selected == "My Profile":
    st.header("👤 My Profile")
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        username = st.session_state["username"]
        users = pd.read_csv("users.csv")
        user_index = users[users["username"] == username].index[0]
        user_data = users.loc[user_index]
    # Layout (side-by-side)
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Name", user_data["Name"], disabled=True)
            st.text_input("Email", user_data["Mail ID"], disabled=True)
            st.text_input("Date of Birth", user_data["dateofbirth"], disabled=True)

        with col2:
            st.text_input("Username", user_data["username"], disabled=True)
            st.text_input("Date of Join", user_data["dateofjoin"], disabled=True)
    # ---- EDIT SECTION ----
    st.subheader("✏️ Edit Profile")
    new_name = st.text_input("Edit Name", user_data["Name"])
    new_email = st.text_input("Edit Email", user_data["Mail ID"])
    change_password = st.checkbox("Change Password 🔒")

    if change_password:
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        # Save button
    if st.button("💾 Save Changes"):
        users.at[user_index, "Name"] = new_name
        users.at[user_index, "Mail ID"] = new_email
        if change_password:
            if new_password == confirm_password:
                users.at[user_index, "password"] = new_password
            else:
                st.error("Passwords do not match ❌")
                st.stop()
        users.to_csv("users.csv", index=False)
        st.success("Profile updated successfully ✅")
        st.rerun()
#------Acheivements----------
elif selected == "Achievements":

    st.header("🏆 My Achievements")

    username = st.session_state.get("username", "")

    try:
        issues = pd.read_csv("issues.csv")
        programmes = pd.read_csv("joined_programmes.csv")

    except FileNotFoundError:
        st.error("Required files are missing")
        st.stop()


    # Filter user data
    user_issues = issues[
        issues["Name"] == username
    ]

    user_programmes = programmes[
        programmes["username"] == username
    ]


    # Calculate achievements
    total_issues = len(user_issues)

    resolved_issues = len(
        user_issues[
            user_issues["Status"].str.lower() == "resolved"
        ]
    )

    total_programmes = len(user_programmes)


    # Contribution Section

    st.subheader("📊 Your Contribution")

    col1, col2, col3 = st.columns(3)


    with col1:
        st.info(f"📢 Issues Reported\n\n{total_issues}")

    with col2:
        st.success(f"✅ Issues Resolved\n\n{resolved_issues}")

    with col3:
        st.warning(f"🤝 Programmes Joined\n\n{total_programmes}")
    st.divider()


    # Achievement badges

    st.subheader("🏅 Badges Earned")


    achievements = []


    if total_issues >= 1:
        achievements.append(
            "🌱 Community Starter\nReported your first issue"
        )

    if total_issues >= 5:
        achievements.append(
            "📢 Voice of the Community\nReported 5+ issues"
        )

    if resolved_issues >= 5:
        achievements.append(
            "🛠 Problem Solver\nHelped resolve 5 issues"
        )

    if total_programmes >= 3:
        achievements.append(
            "🤝 Community Volunteer\nJoined 3 programmes"
        )

    if total_issues >= 10:
        achievements.append(
            "🌟 Local Hero\n10+ issues reported"
        )


    if achievements:

        for badge in achievements:
            st.success(badge)

    else:

        st.info(
            "🌱 No achievements yet. Start reporting issues and joining programmes!"
        )


    st.divider()


    # Progress section

    st.subheader("🚀 Next Achievement")


    if total_issues < 5:
        remaining = 5 - total_issues
        st.write(
            f"📢 Report {remaining} more issue(s) to unlock **Voice of the Community**"
        )

    elif total_programmes < 3:
        remaining = 3 - total_programmes
        st.write(
            f"🤝 Join {remaining} more programme(s) to unlock **Community Volunteer**"
        )

    else:
        st.write(
            "🎉 You have unlocked most achievements!"
        )
#----------Gallery-----------
#----------Gallery-----------
import os

if not os.path.exists("gallery"):
    os.makedirs("gallery")

elif selected=="Gallery":
    gallery_option=st.selectbox("Choose an Option",["View Voxlocal Gallery","Publish your Gallery"])
    def format_name(name):
        return str(name).strip().lower().replace(" ","_")
    if gallery_option=="View Voxlocal Gallery":
        st.header("🖼️ VoxLocal Gallery")
        try:
            programme_df=pd.read_csv("programmesandty.csv")
            joined_df=pd.read_csv("joined_programmes.csv")
        except FileNotFoundError:
            st.error("❌ Required CSV file not found")
            st.stop()
        category_list=programme_df["category"].unique()
        selected_category=st.selectbox("Select Category",category_list)
        issue_list=programme_df[programme_df["category"]==selected_category]["issue_name"].tolist()
        selected_issue=st.selectbox("Select Issue",issue_list)
        st.subheader(f"📌 {selected_issue}")
        st.caption(f"Category: {selected_category}")
        folder_path=os.path.join("gallery",format_name(selected_category),format_name(selected_issue))
        if os.path.exists(folder_path):
            images=[img for img in os.listdir(folder_path) if img.lower().endswith((".jpg",".jpeg",".png"))]
            if images:
                uploader_data=joined_df[(joined_df["Type"].astype(str).str.strip()==str(selected_category).strip())&(joined_df["Issue"].astype(str).str.strip()==str(selected_issue).strip())]
                cols=st.columns(3)
                for i,image in enumerate(images):
                    with cols[i%3]:
                        image_path=os.path.join(folder_path,image)
                        st.image(image_path,use_container_width=True)
                        if "_" in image:
                            uploader=image.rsplit("_",1)[0]
                            st.caption(f"👤 Uploaded by: {uploader}")
                        elif not uploader_data.empty:
                            uploader=uploader_data["username"].iloc[0]
                            st.caption(f"👤 Uploaded by: {uploader}")
                        else:
                            st.caption("👤 Uploaded by: Unknown")
            else:
                st.info("No images uploaded for this issue.")
        else:
            st.info("No gallery available.")
    elif gallery_option=="Publish your Gallery":
        st.header("📤 Publish Your Gallery")
        username=st.session_state.get("username","")
        if username=="":
            st.warning("⚠️ Please login first.")
            st.stop()
        try:
            joined_df=pd.read_csv("joined_programmes.csv")
            programme_df=pd.read_csv("programmesandty.csv")
        except FileNotFoundError:
            st.error("❌ Required CSV files missing")
            st.stop()
        user_programmes=joined_df[joined_df["username"]==username]
        if user_programmes.empty:
            st.warning("⚠️ You have not joined any programmes.")
            st.stop()
        programme_list=user_programmes["programme name"].unique()
        selected_programme=st.selectbox("Select Joined Programme",programme_list)
        programme_data=user_programmes[user_programmes["programme name"]==selected_programme]
        uploader=programme_data["username"].iloc[0]
        programme_type=programme_data["Type"].values[0]
        matching_data=programme_df[programme_df["category"]==programme_type]
        if matching_data.empty:
            st.error("This programme type is not available.")
            st.stop()
        issue_list=matching_data["issue_name"].tolist()
        selected_issue=st.selectbox("Select Issue",issue_list)
        st.info(f"🏷️ Category: {programme_type}")
        st.info(f"📌 Issue: {selected_issue}")
        if "upload_key" not in st.session_state:
            st.session_state.upload_key=0
        proof=st.file_uploader("Upload Gallery Image",type=["jpg","jpeg","png"],key=f"proof_{st.session_state.upload_key}")
        col1,col2=st.columns(2)
        with col1:
            upload_btn=st.button("📤 Upload")
        with col2:
            clear_btn=st.button("🗑️ Clear")
        if clear_btn:
            st.session_state.upload_key+=1
            st.rerun()
        if upload_btn:
            if proof is None:
                st.warning("⚠️ Please upload an image.")
            else:
                folder_path=os.path.join("gallery",format_name(programme_type),format_name(selected_issue))
                os.makedirs(folder_path,exist_ok=True)
                file_path=os.path.join(folder_path,f"{uploader}_{proof.name}")
                with open(file_path,"wb") as f:
                    f.write(proof.getbuffer())
                st.success("✅ Image uploaded successfully!")
                st.session_state.upload_key+=1
                st.rerun()
# # ---------- ABOUT ----------
# Add this once at the top of your app
elif selected == "About Voxlocal":
    with st.container():
        st.markdown('<div class="white-box">', unsafe_allow_html=True)

        st.header("🌍 About Voxlocal")

        st.markdown("""
        **VoxLocal** is a community-driven digital platform designed to connect residents, 
        encourage active participation, and create a better living environment for everyone.

        It provides a space where people can share their concerns, stay informed about 
        neighbourhood activities, and actively contribute towards building stronger and 
        more connected communities.

        The name **VoxLocal** represents the idea of giving a voice to local communities. 
        **"Vox"** means voice, while **"Local"** represents the neighbourhoods we live in.
        """)


        st.subheader("🎯 Our Mission")

        st.markdown("""
        Our mission is to create a smarter, safer, and more sustainable community by using 
        technology to improve communication, encourage citizen involvement, and support 
        faster solutions to local challenges.

        VoxLocal aligns with **SDG 11: Sustainable Cities and Communities**, which focuses 
        on making cities and human settlements inclusive, safe, resilient, and sustainable.
        """)


        st.subheader("🌱 Our Connection with SDG 11")

        st.markdown("""
        **SDG 11: Sustainable Cities and Communities** aims to improve urban living by 
        promoting safe environments, sustainable practices, and inclusive communities.

        🏙️ **Creating Inclusive Communities**  
        Providing residents with a platform to share opinions and report concerns.

        🛠️ **Improving Local Infrastructure**  
        Helping identify issues such as damaged roads, waste problems, and broken streetlights.

        🌿 **Promoting Sustainable Practices**  
        Encouraging cleanliness drives, tree plantation programmes, and sustainability campaigns.

        🤝 **Encouraging Community Participation**  
        Connecting residents through volunteering opportunities and community programmes.
        """)


        st.subheader("💡 What We Offer")

        st.markdown("""
        📝 **Neighbourhood Issue Reporting**  
        Report problems such as road damage, waste management issues, water leaks, and safety concerns.

        📢 **Community Announcements**  
        Receive updates about local events, notices, and activities.

        🤝 **Community Programmes**  
        Participate in cleanliness drives, awareness campaigns, and volunteering activities.

        🏆 **Achievements & Recognition**  
        Track your contribution and participation in community improvement.
        """)


        st.subheader("🌏 Our Vision")

        st.markdown("""
        Our vision is to create sustainable neighbourhoods where every citizen has a voice, 
        every issue receives attention, and communities work together towards a cleaner, 
        safer, and more connected future.

        **VoxLocal — Your Voice. Your Community. Your Impact.**
        """)

        st.markdown('</div>', unsafe_allow_html=True)
# ---------- LOGOUT ----------
elif selected == "Logout":
    st.session_state.clear()
    st.success("Logged out successfully")
    st.switch_page("app.py")
    st.stop()
