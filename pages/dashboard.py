import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as pl
from streamlit_option_menu import option_menu

st.set_page_config(page_title="VoxLocal Dashboard",layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"]{display:none;}
</style>
""",unsafe_allow_html=True)

def set_gif_bg():
    gif_url="https://cdn.dribbble.com/userupload/20481043/file/original-ff919c0d8190474293a4a448343b80e2.gif"
    st.markdown(f"""
    <style>
    .stApp{{
        background:linear-gradient(rgba(0,0,0,0.5),rgba(0,0,0,0.5)),url("{gif_url}");
        background-size:cover;
        background-position:center;
        background-repeat:no-repeat;
        background-attachment:fixed;
    }}
    </style>
    """,unsafe_allow_html=True)

set_gif_bg()

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.stop()

with st.sidebar:
    selected=option_menu(
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
        icons=[
            "house",
            "plus-circle",
            "envelope",
            "bell",
            "person",
            "trophy",
            "images",
            "info",
            "power"
        ],
        default_index=0
    )

@st.cache_data
def load_issues():
    try:
        return pd.read_csv("issues.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name","username","Issue","Type","Status","Location","Description","Priority","Proof"])

def save_issue(data):
    try:
        if os.path.exists("issues.csv"):
            old_data=pd.read_csv("issues.csv")
        else:
            old_data=pd.DataFrame(columns=["Name","username","Issue","Type","Status","Location","Description","Priority","Proof"])
        required_columns=["Name","username","Issue","Type","Status","Location","Description","Priority","Proof"]
        for column in required_columns:
            if column not in old_data.columns:
                old_data[column]=""
        old_data=old_data[required_columns]
        final_data=pd.concat([old_data,data],ignore_index=True)
        final_data.to_csv("issues.csv",index=False)
        load_issues.clear()
        return True
    except Exception as e:
        st.error(f"❌ Error saving issue: {e}")
        return False

if selected=="Home":
    st.title("🏠 Dashboard")
    st.markdown(f"Welcome, **{st.session_state.get('username','User')}** 👋")
    df=load_issues()
    if df.empty:
        st.warning("No issues reported yet.")
    else:
        st.subheader("📊 Overview")
        st.dataframe(df,use_container_width=True)
        total=len(df)
        resolved=len(df[df["Status"].astype(str).str.lower()=="resolved"])
        pending=len(df[df["Status"].astype(str).str.lower()=="pending"])
        progress=len(df[df["Status"].astype(str).str.lower()=="in progress"])
        col1,col2,col3,col4=st.columns(4)
        col1.metric("Total Issues",total)
        col2.metric("Resolved",resolved)
        col3.metric("In Progress",progress)
        col4.metric("Pending",pending)
        st.subheader("📌 Issue Distribution")
        if "Issue" in df.columns and not df["Issue"].empty:
            issue_counts=df["Issue"].value_counts()
            fig,ax=pl.subplots(figsize=(5,5))
            ax.pie(issue_counts,labels=issue_counts.index,autopct="%1.1f%%",radius=0.8)
            ax.axis("equal")
            st.pyplot(fig)
        st.subheader("📈 Status Distribution")
        if "Status" in df.columns:
            status_counts=df["Status"].value_counts()
            st.bar_chart(status_counts)

elif selected=="Report an Issue":
    st.subheader("📝 Report an Issue")
    if st.session_state.get("issue_submitted",False):
        st.success("✅ Issue reported successfully!")
        del st.session_state["issue_submitted"]
    with st.form("issue_form",clear_on_submit=True):
        name=st.text_input("Name *")
        issue=st.text_input("Issue *")
        location=st.text_input("Location *")
        description=st.text_area("Description *")
        priority=st.selectbox("Priority *",["Very High","High","Medium","Low","Very Low"])
        type_issue=st.selectbox("Type of Issue *",[
            "Environment",
            "Infrastructure",
            "Health & Sanitation",
            "Safety & Security",
            "Education & Awareness",
            "Social Welfare",
            "Animal Welfare",
            "Disaster Management",
            "Technology",
            "Community Activities",
            "Others"
        ])
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
            elif proof is None:
                st.error("⚠️ Please upload proof of the issue.")
            else:
                try:
                    os.makedirs("proof_issue",exist_ok=True)
                    safe_filename=os.path.basename(proof.name)
                    proof_path=os.path.join("proof_issue",safe_filename)
                    with open(proof_path,"wb") as f:
                        f.write(proof.getbuffer())
                    new_data=pd.DataFrame({
                        "Name":[name.strip()],
                        "username":[st.session_state.get("username","")],
                        "Issue":[issue.strip()],
                        "Type":[type_issue],
                        "Status":["Pending"],
                        "Location":[location.strip()],
                        "Description":[description.strip()],
                        "Priority":[priority],
                        "Proof":[proof_path]
                    })
                    if save_issue(new_data):
                        st.session_state["issue_submitted"]=True
                        st.rerun()
                except Exception as e:
                    st.error("❌ An error occurred while submitting the issue.")
                    st.error(f"Error details: {e}")

elif selected=="Create & Invite":
    st.subheader("📝 Invite Others for Your Programme")
    if st.session_state.get("programme_submitted",False):
        st.success("✅ Programme published successfully!")
        del st.session_state["programme_submitted"]
    with st.form("create_programme_form",clear_on_submit=True):
        name=st.text_input("Enter name of the programme:")
        date=st.date_input("Enter date:")
        venue=st.text_input("Enter venue:")
        description=st.text_area("Describe the programme:")
        link=st.text_input("Enter link for participant registration:")
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
                    if os.path.exists("programmes.csv"):
                        old_data=pd.read_csv("programmes.csv")
                    else:
                        old_data=pd.DataFrame(columns=["ID","Programme Name","Date","Venue","Description","Registration Link"])
                    required=["ID","Programme Name","Date","Venue","Description","Registration Link"]
                    for column in required:
                        if column not in old_data.columns:
                            old_data[column]=""
                    old_data["ID"]=pd.to_numeric(old_data["ID"],errors="coerce").fillna(0).astype(int)
                    new_id=int(old_data["ID"].max()+1) if len(old_data)>0 else 1
                    new_programme=pd.DataFrame({
                        "ID":[new_id],
                        "Programme Name":[name.strip()],
                        "Date":[date],
                        "Venue":[venue.strip()],
                        "Description":[description.strip()],
                        "Registration Link":[link.strip()]
                    })
                    final_data=pd.concat([old_data[required],new_programme],ignore_index=True)
                    final_data.to_csv("programmes.csv",index=False)
                    st.session_state["programme_submitted"]=True
                    st.rerun()
                except Exception as e:
                    st.error("❌ An error occurred while publishing the programme.")
                    st.error(f"Error details: {e}")

elif selected=="Announcements":
    programme_option=st.selectbox("Choose an Option",["View Programmes","My Joined Programmes"])
    if programme_option=="View Programmes":
        try:
            df=pd.read_csv("programmes.csv")
        except FileNotFoundError:
            st.warning("No programmes available.")
            st.stop()
        st.markdown("""
        <style>
        .card{
            background-color:rgba(255,255,255,0.9);
            padding:20px;
            border-radius:15px;
            margin-bottom:15px;
            box-shadow:2px 2px 10px rgba(0,0,0,0.2);
        }
        .title{
            font-size:20px;
            font-weight:bold;
            color:#333;
        }
        .info{
            font-size:14px;
            color:#555;
            margin-top:5px;
        }
        </style>
        """,unsafe_allow_html=True)
        for _,row in df.iterrows():
            programme_name=str(row.get("Programme Name",""))
            programme_date=str(row.get("Date",""))
            venue=str(row.get("Venue",""))
            description=str(row.get("Description",""))
            link=str(row.get("Registration Link",""))
            st.markdown(f"""
            <div class="card">
            <div class="title">{programme_name}</div>
            <div class="info">📅 <b>Date:</b> {programme_date}</div>
            <div class="info">📍 <b>Venue:</b> {venue}</div>
            <div class="info">📝 {description}</div>
            <br>
            <a href="{link}" target="_blank">
            <button style="background-color:#4CAF50;color:white;border:none;padding:10px 15px;border-radius:8px;">
            🔗 Join Programme
            </button>
            </a>
            </div>
            """,unsafe_allow_html=True)
    elif programme_option=="My Joined Programmes":
        st.header("🤝 Joined Programme Registration")
        if st.session_state.get("joined",False):
            st.success("✅ Programme registration submitted!")
            del st.session_state["joined"]
        try:
            programme_df=pd.read_csv("programmesandty.csv")
            programme_df["category"]=programme_df["category"].astype(str).str.strip()
            programme_df["issue_name"]=programme_df["issue_name"].astype(str).str.strip()
        except FileNotFoundError:
            st.error("programmesandty.csv not found")
            st.stop()
        programme_type=st.selectbox("Programme Type",programme_df["category"].unique())
        related_issues=programme_df[programme_df["category"]==programme_type]["issue_name"].tolist()
        if not related_issues:
            st.warning("No issues available for this category.")
            st.stop()
        issue=st.selectbox("Related Issue",related_issues)
        with st.form("join_programme_form",clear_on_submit=True):
            username=st.session_state.get("username","")
            st.text_input("Username",value=username,disabled=True)
            programmename=st.text_input("Programme Name")
            datejoined=st.date_input("Date of Registration")
            programdate=st.date_input("Programme Date")
            venue=st.text_input("Venue")
            proof=st.file_uploader("Upload Proof of Participation",type=["jpg","jpeg","png","pdf"])
            submit=st.form_submit_button("✅ Submit")
            if submit:
                if not programmename.strip():
                    st.error("⚠️ Please enter programme name.")
                elif not venue.strip():
                    st.error("⚠️ Please enter venue.")
                elif proof is None:
                    st.error("⚠️ Please upload proof of participation.")
                else:
                    try:
                        os.makedirs("proofs",exist_ok=True)
                        safe_filename=os.path.basename(proof.name)
                        proof_path=os.path.join("proofs",safe_filename)
                        with open(proof_path,"wb") as f:
                            f.write(proof.getbuffer())
                        new_data=pd.DataFrame({
                            "username":[username],
                            "programme name":[programmename.strip()],
                            "Date Joined":[datejoined],
                            "Programme Date":[programdate],
                            "Type":[programme_type],
                            "Issue":[issue],
                            "Venue":[venue.strip()],
                            "Proof":[safe_filename],
                            "Status":["Pending Verification"]
                        })
                        if os.path.exists("joined_programmes.csv"):
                            joined=pd.read_csv("joined_programmes.csv")
                            joined=pd.concat([joined,new_data],ignore_index=True)
                        else:
                            joined=new_data
                        joined.to_csv("joined_programmes.csv",index=False)
                        st.session_state["joined"]=True
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

elif selected=="My Profile":
    st.header("👤 My Profile")
    username=st.session_state.get("username","")
    try:
        users=pd.read_csv("users.csv")
    except FileNotFoundError:
        st.error("users.csv not found.")
        st.stop()
    user_rows=users[users["username"].astype(str)==str(username)]
    if user_rows.empty:
        st.error("User profile not found ❌")
    else:
        user_index=user_rows.index[0]
        user_data=users.loc[user_index]
        if st.session_state.get("profile_updated",False):
            st.success("Profile updated successfully ✅")
            st.session_state["profile_updated"]=False
        col1,col2=st.columns(2)
        with col1:
            st.text_input("Name",value=str(user_data["Name"]),disabled=True,key="display_name")
            st.text_input("Email",value=str(user_data["Mail ID"]),disabled=True,key="display_email")
            st.text_input("Date of Birth",value=str(user_data["dateofbirth"]),disabled=True,key="display_dob")
        with col2:
            st.text_input("Username",value=str(user_data["username"]),disabled=True,key="display_username")
            st.text_input("Date of Join",value=str(user_data["dateofjoin"]),disabled=True,key="display_join")
        st.divider()
        st.subheader("✏️ Edit Profile")
        new_name=st.text_input("Edit Name",value=str(user_data["Name"]),key="edit_name")
        new_email=st.text_input("Edit Email",value=str(user_data["Mail ID"]),key="edit_email")
        change_password=st.checkbox("Change Password 🔒",key="change_password")
        new_password=""
        confirm_password=""
        if change_password:
            new_password=st.text_input("New Password",type="password",key="new_password")
            confirm_password=st.text_input("Confirm Password",type="password",key="confirm_password")
        if st.button("💾 Save Changes",key="save_changes"):
            if not new_name.strip():
                st.error("Please enter your name ❌")
                st.stop()
            if not new_email.strip():
                st.error("Please enter your email ❌")
                st.stop()
            if change_password:
                if not new_password:
                    st.error("Please enter a new password ❌")
                    st.stop()
                if new_password!=confirm_password:
                    st.error("Passwords do not match ❌")
                    st.stop()
            users.at[user_index,"Name"]=new_name.strip()
            users.at[user_index,"Mail ID"]=new_email.strip()
            if change_password:
                users.at[user_index,"password"]=new_password
            users.to_csv("users.csv",index=False)
            st.session_state["profile_updated"]=True
            st.rerun()

elif selected=="Achievements":
    st.header("🏆 My Achievements")
    username=st.session_state.get("username","")
    try:
        issues=pd.read_csv("issues.csv")
    except FileNotFoundError:
        issues=pd.DataFrame(columns=["Name","username","Issue","Type","Status","Location","Description","Priority","Proof"])
    try:
        programmes=pd.read_csv("joined_programmes.csv")
    except FileNotFoundError:
        programmes=pd.DataFrame(columns=["username","programme name","Date Joined","Programme Date","Type","Issue","Venue","Proof","Status"])
    if "username" in issues.columns:
        user_issues=issues[issues["username"].astype(str)==str(username)]
    else:
        user_issues=pd.DataFrame()
    if "username" in programmes.columns:
        user_programmes=programmes[programmes["username"].astype(str)==str(username)]
    else:
        user_programmes=pd.DataFrame()
    total_issues=len(user_issues)
    if "Status" in user_issues.columns:
        resolved_issues=len(user_issues[user_issues["Status"].astype(str).str.lower()=="resolved"])
    else:
        resolved_issues=0
    total_programmes=len(user_programmes)
    st.subheader("📊 Your Contribution")
    col1,col2,col3=st.columns(3)
    with col1:
        st.info(f"📢 Issues Reported\n\n{total_issues}")
    with col2:
        st.success(f"✅ Issues Resolved\n\n{resolved_issues}")
    with col3:
        st.warning(f"🤝 Programmes Joined\n\n{total_programmes}")
    st.divider()
    st.subheader("🏅 Badges Earned")
    achievements=[]
    if total_issues>=1:
        achievements.append("🌱 Community Starter\nReported your first issue")
    if total_issues>=5:
        achievements.append("📢 Voice of the Community\nReported 5+ issues")
    if resolved_issues>=5:
        achievements.append("🛠 Problem Solver\nHelped resolve 5 issues")
    if total_programmes>=3:
        achievements.append("🤝 Community Volunteer\nJoined 3 programmes")
    if total_issues>=10:
        achievements.append("🌟 Local Hero\n10+ issues reported")
    if achievements:
        for badge in achievements:
            st.success(badge)
    else:
        st.info("🌱 No achievements yet. Start reporting issues and joining programmes!")
    st.divider()
    st.subheader("🚀 Next Achievement")
    if total_issues<5:
        remaining=5-total_issues
        st.write(f"📢 Report {remaining} more issue(s) to unlock **Voice of the Community**")
    elif total_programmes<3:
        remaining=3-total_programmes
        st.write(f"🤝 Join {remaining} more programme(s) to unlock **Community Volunteer**")
    else:
        st.write("🎉 You have unlocked most achievements!")

elif selected=="Gallery":

    gallery_option=st.selectbox("Choose an Option",["View Voxlocal Gallery","Publish your Gallery"])

    def format_name(name):
        return str(name).strip().lower().replace(" ","_")

    if gallery_option=="View Voxlocal Gallery":

        st.header("🖼️ VoxLocal Gallery")

        try:
            programme_df=pd.read_csv("programmesandty.csv")
        except FileNotFoundError:
            st.error("❌ programmesandty.csv not found")
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

                cols=st.columns(3)

                for i,image in enumerate(images):
                    with cols[i%3]:
                        st.image(os.path.join(folder_path,image),use_container_width=True)

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

        programme_type=programme_data["Type"].values[0]

        matching_data=programme_df[programme_df["category"]==programme_type]

        if matching_data.empty:
            st.error("This programme type is not available.")
            st.stop()

        issue_list=matching_data["issue_name"].tolist()

        selected_issue=st.selectbox("Select Issue",issue_list)

        st.info(f"🏷️ Category: {programme_type}")

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

                file_path=os.path.join(folder_path,proof.name)

                with open(file_path,"wb") as f:
                    f.write(proof.getbuffer())
                st.success("✅ Image uploaded successfully!")
                st.session_state.upload_key+=1
                st.rerun()


elif selected=="About Voxlocal":
    st.header("🌍 About VoxLocal")
    st.markdown("""
    **VoxLocal** is a community-driven digital platform designed to connect residents,
    encourage active participation, and create a better living environment for everyone.
    """)
    st.subheader("🎯 Our Mission")
    st.markdown("""
    Our mission is to create a smarter, safer, and more sustainable community by using
    technology to improve communication, encourage citizen involvement, and support faster
    solutions to local challenges.
    """)
    st.subheader("🌱 Our Connection with SDG 11")
    st.markdown("""
    **SDG 11: Sustainable Cities and Communities** aims to improve urban living by
    promoting safe environments, sustainable practices, and inclusive communities.
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

elif selected=="Logout":
    st.session_state.clear()
    st.success("Logged out successfully")
    st.switch_page("app.py")
    st.stop()
