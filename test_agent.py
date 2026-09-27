from backend.recruitment_agent import create_recruitment_agent


# --------------------------------------------------
# Test Job Description
# --------------------------------------------------

JOB_DESCRIPTION = """
React Frontend Developer

We are looking for a React Frontend Developer to build
responsive and user-friendly web applications.

Required Skills:
- React.js
- JavaScript
- HTML5
- CSS3
- Git
- REST APIs
- Responsive Web Design

Preferred Skills:
- TypeScript
- Redux
- Next.js
- Node.js
- MongoDB

Responsibilities:
- Develop web applications using React.js.
- Build reusable UI components.
- Integrate REST APIs.
- Debug and optimize frontend applications.
- Use Git for version control.
"""


# --------------------------------------------------
# Resume to test
# --------------------------------------------------
# Change this path if you want to test another resume.

RESUME_PATH = "data/resumes/candidate2.pdf"


# --------------------------------------------------
# Create Agent
# --------------------------------------------------

print("\nCreating Recruiter AI Agent...")

agent = create_recruitment_agent()

print("Agent created successfully.\n")


# --------------------------------------------------
# Send request to Agent
# --------------------------------------------------

prompt = f"""
Evaluate this candidate for the following job.

Resume:
{RESUME_PATH}

Job Description:
{JOB_DESCRIPTION}

Please:
1. Analyze the job requirements.
2. Evaluate the candidate's resume.
3. Identify matched skills.
4. Identify missing skills.
5. Check supporting evidence for important skills.
6. Provide the candidate's score.
7. Give a short recruitment summary.
"""


print("Running Recruiter AI Agent...")
print("=" * 70)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    }
)


# --------------------------------------------------
# Display Result
# --------------------------------------------------

print("\n")
print("=" * 70)
print("RECRUITER AI AGENT RESULT")
print("=" * 70)

messages = result.get("messages", [])

if messages:
    final_message = messages[-1]

    if hasattr(final_message, "content"):
        print(final_message.content)
    else:
        print(final_message)
else:
    print(result)

print("=" * 70)
print("TEST COMPLETED")
print("=" * 70)