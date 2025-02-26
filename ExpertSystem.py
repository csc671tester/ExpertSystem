import clips
import streamlit as st
import io
import sys
# Initialize CLIPS environment
# Define a custom router class
class MyCaptureRouter(clips.routers.Router):
    def __init__(self, name: str, priority: int = 0):
        super().__init__(name, priority)
        self.captured_messages = []

    def query(self, name: str) -> bool:
        # Capture 'stdout' output from CLIPS
        return name == 'stdout'

    def write(self, name: str, message: str):
        # Remove the unwanted newlines and extra spaces, add space if necessary
        formatted_message = message.replace("\n", " ").strip()  # Remove newlines
        if formatted_message:
            # Ensure that there is proper spacing after each message
            if self.captured_messages:
                self.captured_messages[-1] += " " + formatted_message  # Join with a space
            else:
                self.captured_messages.append(formatted_message)

    def get_captured_messages(self):
        return self.captured_messages

# Initialize the CLIPS environment
env = clips.Environment()

# Create a custom router instance
my_router = MyCaptureRouter(name="my_output_router")

# Add the custom router to the environment
env.add_router(my_router)
# Define job and candidate templates in CLIPS using build
# Define the job and candidate templates in CLIPS using build
try:
    env.build("""
    (deftemplate job
        (slot title)
        (multislot required_skills)
        (multislot desired_skills)
        (slot required_degree)
    )
    """)



    env.build("""
    (deftemplate candidate
        (slot name)
        (multislot skills)
        (slot degree)
    )
    """)


except clips.CLIPSError as e:
    print(f"Error during template loading: {e}")

# Define the qualification rule
env.build("""
(defrule qualified
    (job (title ?jt) (required_skills $?req_skills) (desired_skills $?des_skills) (required_degree ?req_deg))
    (candidate (name ?cn) (skills $?cand_skills) (degree ?deg&:(eq ?deg ?req_deg)))
    (test (subsetp $?req_skills $?cand_skills)) ; Ensure all required skills are present
    =>
    (bind ?match_count 0)
    (bind ?matched_skills "")  ; String to hold all matched required skill names
    (bind ?desired_match_count 0)  ; Count of matched desired skills
    (foreach ?skill ?req_skills
        (if (member$ ?skill ?cand_skills) then 
            (bind ?match_count (+ ?match_count 1))
            (if (eq ?matched_skills "") then
                (bind ?matched_skills ?skill) ; First match
            else
                (bind ?matched_skills (str-cat ?matched_skills ", " ?skill)) ; Concatenate other matches
            )
        )
    )
    (foreach ?skill ?des_skills
        (if (member$ ?skill ?cand_skills) then
            (bind ?desired_match_count (+ ?desired_match_count 1))
        )
    )
    (printout t ?cn " matches the required skills: " ?matched_skills crlf)
    (printout t ?cn " is qualified for the " ?jt " position." crlf)
    (if (> ?desired_match_count 0) then 
        (printout t " (Preferred: Matches " ?desired_match_count " desired skills)" crlf)
    )
)
""")
def add_job(title, required_skills, desired_skills, required_degree):
    req_skills_str = ' '.join(f'"{skill}"' for skill in required_skills)
    des_skills_str = ' '.join(f'"{skill}"' for skill in desired_skills) if desired_skills else ""

    env.assert_string(f'(job (title "{title}") (required_skills {req_skills_str}) (desired_skills {des_skills_str}) (required_degree "{required_degree}"))')

# Function to add a candidate
def add_candidate(name, skills, degree):
    skills_str = ' '.join(f'"{skill}"' for skill in skills) if skills else ""

    env.assert_string(f'(candidate (name "{name}") (skills {skills_str}) (degree "{degree}"))')
# Predefined jobs
import streamlit as st

# Job listings
add_job("Entry-Level Python Engineer", ["Python Coursework", "Software Engineering Coursework"], ["Agile Coursework"], "Bachelors in Computer Science")
add_job("Python Engineer", ["3 Years Python Development", "1 year in Data Development", 'Experience in Agile Projects'], ['Git'], "Bachelors in Computer Science")
add_job("Project Manager", ['3 Years Managing Software Projects', '2 years in Agile Projects'], [], "PMI Lean Project Management Certification")
add_job("Senior Knowledge Engineer", ['3 years using Python to develop Expert Systems', '2 years data architecture and development'], [], 'Masters in CS')

# Streamlit UI
st.title("Job Qualification Expert System")

name = st.text_input("Candidate Name")

# Multi-select inputs for different skill categories
selected_skills_python = st.multiselect("Select Python Skills", ["Python Coursework", "3 Years Python Development", "3 years using Python to develop Expert Systems"])
selected_skills_agile = st.multiselect("Select Agile skills/experience", ["Agile Coursework", "Experience in Agile Projects", "2 years in Agile Projects"])
selected_skills_management = st.multiselect("Select Software Management/Development experience", ["Software Engineering Coursework", "3 Years Managing Software Projects"])
selected_skills_data = st.multiselect("Select Data Experience", ["1 year in Data Development", "2 years data architecture and development"])
selected_skills_git = st.multiselect("Select your version control experience", ["Git"])

# Combine all selected skills into a single list
selected_skills = selected_skills_python + selected_skills_agile + selected_skills_management + selected_skills_data + selected_skills_git

degree = st.selectbox("Select Your Degree\Qualification", ["Bachelors in Computer Science", "Masters in CS", "PMI Lean Project Management Certification"])

if st.button("Submit Candidate"):
    add_candidate(name, selected_skills, degree)
    env.run() 
    captured_output = my_router.get_captured_messages()
    if captured_output:
    # Display output in Streamlit
        st.write(("".join(captured_output)))
    else: 
        st.write("Unfortunately no open positions match your qualifications")
    
