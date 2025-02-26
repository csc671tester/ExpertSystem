import clips

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
    (foreach ?skill ?des_skills
        (if (member$ ?skill ?cand_skills) then 
            (bind ?match_count (+ ?match_count 1))
            (printout t ?cn " matches the desired skill: " ?skill crlf)
        )
    )
    (printout t ?cn " is qualified for the " ?jt " position.")
    (if (> ?match_count 0) then 
        (printout t " (Preferred: Matches " ?match_count " desired skills), ")
    )
    (printout t crlf))
""")

# Function to add a job
def add_job(title, required_skills, desired_skills, required_degree):
    req_skills_str = ' '.join(f'"{skill}"' for skill in required_skills)
    des_skills_str = ' '.join(f'"{skill}"' for skill in desired_skills) if desired_skills else ""

    env.assert_string(f'(job (title "{title}") (required_skills {req_skills_str}) (desired_skills {des_skills_str}) (required_degree "{required_degree}"))')

# Function to add a candidate
def add_candidate(name, skills, degree):
    skills_str = ' '.join(f'"{skill}"' for skill in skills) if skills else ""

    env.assert_string(f'(candidate (name "{name}") (skills {skills_str}) (degree "{degree}"))')

# Add job and candidate
add_job("Entry-Level Python Engineer", ["Python Coursework", "Software Engineering Coursework"], ["Agile Course"], "Computer Science")
add_candidate("Jim", ["Python Coursework", "Software Engineering Coursework", "Agile Course"], "Computer Science")

# Run the CLIPS environment (this triggers the rules and the output capture)
env.run()

# Retrieve the captured messages from the custom router
captured_output = my_router.get_captured_messages()

# Save the captured output to a file
output_file = "clips_output.txt"
with open(output_file, "w") as file:
    for message in captured_output:
        file.write(message)

# Print the captured output (optional)
print("Captured Output:")
print("".join(captured_output))
