
import clips
import io
import sys
# Initialize the CLIPS environment
env = clips.Environment()

# Create an in-memory string buffer to capture output

def capture_output(output):
    captured_output.append(output)

# Initialize an empty list to store the captured outputs
captured_output = []

# Set the custom capture function as the output handler
env.trace_on()  # Enable tracing to capture output
env.set_message_handler(capture_output)

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
        (printout t " (Preferred: Matches " ?match_count " desired skills)")
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

# Get the captured output


# Print the captured output
print("Captured Output:")
print(captured_output)
