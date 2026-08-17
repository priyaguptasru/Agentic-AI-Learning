Overview

Module-6 implements a production-style Agentic AI orchestration workflow using multiple specialized agents, deterministic workflow routing, human approval, retry handling, timeout handling, safe exits, and execution traceability.

The system receives a user query, understands the user's intent, creates an execution plan, selects the appropriate agent, executes the required operation, handles failures safely, and generates the final response.

The architecture combines:

LLM-based reasoning
Specialized AI agents
Supervisor-based orchestration
Deterministic workflow routing
Hybrid document retrieval
SQL execution
Generic business action execution
Human-in-the-loop approval
Retry handling
Timeout handling
Safe exits
Execution traceability
==================================================

1.  Architecture
    The high-level workflow is:

                             User Query
                                 |
                                 v
                      +----------------------+
                      |  Intent Classifier    |
                      +----------------------+
                                 |
                                 v
                         +---------------+
                         |    Planner    |
                         +---------------+
                                 |
                                 v
                      +----------------------+
                      |   Agent Workflow     |
                      |    Orchestrator      |
                      +----------------------+
                                 |
                                 v
                      +----------------------+
                      |   Supervisor Agent   |
                      +----------------------+
                                 |
                  +--------------+--------------+
                  |              |              |
                  v              v              v
           Retrieval Agent    SQL Agent    Action Agent
                  |              |              |
                  v              v              v
            Hybrid Search    Database Tool  Business Tool
                                                 |
                                                 v
                                          Human Approval
                                                 |
                                          +------+------+
                                          |             |
                                       Approve        Reject
                                          |             |
                                          v             v
                                    Execute Action   Safe Exit
                                          |
                                          v
                                    Answer Agent
                                          |
                                          v
                                    Final Response

    ==================================================

2.  Main Objective

The objective of Module-6 is to build a reliable orchestration layer that can:

Understand the user's intent.
Generate an execution plan.
Select the correct specialized agent.
Execute workflow steps sequentially.
Route workflow execution deterministically.
Retrieve relevant document information.
Execute read-only SQL operations.
Validate business actions.
Require human approval for critical actions.
Retry transient failures.
Handle agent execution timeouts.
Stop safely when execution cannot continue.
Maintain a traceable execution sequence.
Generate a final user-facing response.
==================================================

3. Supported Intent Types

The system supports multiple types of user requests.

Greeting

Examples:

Hi
Hello
How are you?
Thank you

Typical workflow:

intent_classification
|
v
generate_response
Retrieval

Used when the user asks for information from the available knowledge base.

Examples:

What is RAG?
What is routing?
Explain the architecture.

Typical workflow:

retrieve_documents
|
v
generate_response
SQL

Used when the user asks for structured information from the database.

Examples:

How many files are available in database?
List all documents available in database.

Typical workflow:

execute_sql
|
v
generate_response
Summary

Used when the user requests a summary of available document information.

Example:

Give summary of Adobe_Sample_PDF.

Typical workflow:

retrieve_documents
|
v
generate_response
Comparison

Used when the user wants to compare information from different documents.

Example:

How is AI_Paper different from IRS_Form_1040?

Typical workflow:

retrieve_documents
|
v
generate_response
Action

Used when the user asks the system to perform a business operation.

Examples:

Delete Adobe_Sample_PDF from database.

Make duplicate of IRS_Form_1040.

Send an email to my manager.

Send an email to priyaguptasru@gmail.com.

Typical workflow:

validate_action
|
v
execute_action
|
v
generate_response

# For critical actions, human approval is inserted before execution.

4. Project Structure

The main Module-6 structure is:

Module-6/
│
├── app6/
│ │
│ ├── agents/
│ │ ├── action_agent.py
│ │ ├── answer_agent.py
│ │ ├── retrieval_agent.py
│ │ ├── sql_agent.py
│ │ └── ...
│ │
│ ├── approval/
│ │ ├── approval_service.py
│ │ └── ...
│ │
│ ├── prompts/
│ │ ├── action_prompt.py
│ │ ├── planner_prompt.py
│ │ ├── intent_prompt.py
│ │ └── ...
│ │
│ ├── tools/
│ │ ├── business_action_tool.py
│ │ ├── database_tool.py
│ │ └── ...
│ │
│ ├── workflows/
│ │ ├── agent_workflow.py
│ │ └── workflow_router.py
│ │
│ ├── services/
│ │ ├── hybrid_search.py
│ │ ├── semantic_search.py
│ │ ├── keyword_search.py
│ │ ├── query_normalizer.py
│ │ └── query_expansion.py
│ │
│ ├── models/
│ │ ├── intent.py
│ │ ├── plan.py
│ │ └── ...
│ │
│ ├── tests/
│ │ ├── test_agent_workflow.py
│ │ ├── test_retry_behavior.py
│ │ ├── test_retry_integration.py
│ │ └── test_timeout.py
│ │
│ └── ...
│
├── .env
├── requirements.txt
└── README.md
==================================================

5. Component Responsibilities
   Intent Classifier

The Intent Classifier determines the type of request made by the user.

Example:

"What is RAG?"
|
v
retrieval

Example:

"Delete Adobe_Sample_PDF."
|
v
action

The classifier also provides a confidence score and reason.

Example:

Intent : action
Confidence : 0.95
Reason : User requested a business action.
==================================================

6. Planner

The Planner creates a structured execution plan based on the detected intent.

Example:

User:
What is RAG?

Plan:

1. retrieve_documents
2. generate_response

For an action:

User:
Send an email to my manager.

Plan:

1. validate_action
2. execute_action
3. generate_response

# The Planner determines what steps are required, while the workflow determines how those steps are safely executed.

7. Supervisor Agent

The Supervisor Agent coordinates the specialized agents.

It selects the appropriate agent for the current workflow step.

Examples:

retrieve_documents
|
v
retrieval_agent
execute_sql
|
v
sql_agent
validate_action
|
v
action_agent
generate_response
|
v
answer_agent

# The Supervisor does not directly perform every operation. It delegates work to specialized agents.

8. Retrieval Agent

The Retrieval Agent retrieves relevant information from the knowledge base.

The retrieval flow is:

User Query
|
v
Query Normalization
|
v
Query Expansion
|
v
Hybrid Search
|
+----------------+
| |
v v
Semantic Search Keyword Search
| |
+--------+-------+
|
v
Retrieved Context

# The retrieved context is then provided to the Answer Agent.

9. Hybrid Search

The retrieval system combines two approaches.

Semantic Search

Finds information based on semantic similarity.

Keyword Search

Finds information based on exact or keyword matches.

# Combining both approaches improves retrieval coverage and makes the system less dependent on only semantic or only keyword matching.

10. SQL Agent

The SQL Agent handles natural-language requests that require structured database information.

Example:

User:
How many files are available in database?

The SQL Agent:

Reads the database schema.
Generates SQL from the user's natural-language request.
Performs basic SQL safety validation.
Allows only read-oriented SQL.
Executes the query through the database tool.
Returns the structured result to the workflow.

The generated SQL is not blindly executed.

# The workflow validates that the generated query is a read-only query before execution.

11. Action Agent

The Action Agent understands and validates business actions.

It does not directly execute the action.

Example:

User:
Delete Adobe_Sample_PDF from database.

The Action Agent identifies:

Action:
delete

Approval:
required

Another example:

User:
Send an email to priyaguptasru@gmail.com.

The Action Agent identifies:

Action:
send_email

Approval:
required

This separates:

Action Understanding

from:

# Action Execution

12. Business Action Tool

BusinessActionTool provides a generic registry-based interface for executing business actions.

The Action Agent does not need to know how the underlying business operation is implemented.

The design is:

ActionAgent
|
v
BusinessActionTool
|
v
Registered Action Handler

Actions can be registered through handlers.

The design can later be extended to adapters for:

Email
ServiceNow
CRM
REST APIs
File systems
Database operations
Enterprise applications

The current demonstration handlers are intentionally safe and generic.

For example:

send_email

# is simulated and does not send a real email.

13. Human-in-the-Loop Approval

Critical business actions require human approval before execution.

Examples include:

send_email
delete
write
update
duplicate

The safety flow is:

User Request
|
v
Action Validation
|
v
Approval Evaluation
|
v
Human Approval
|
+------------------+
| |
Approve Reject
| |
v v
Execute Action Safe Exit

The Action Agent evaluates whether approval is required.

# The workflow then prevents execution until approval has been granted.

14. Approval Example

Example request:

Send an email to priyaguptasru@gmail.com
with subject "One Day Leave Request"
and body "I would like to request one day leave."

The system identifies:

Action:
send_email

Approval Required:
True

The workflow pauses before execution.

After the user approves:

human_approval_approved
|
v
execute_action

The business action is then executed through the BusinessActionTool.

In the current demonstration environment:

Action : send_email
Status : simulated

# No real email is sent.

15. Rejected Approval

If the user rejects a critical action:

validate_action
|
v
approval_required
|
v
human rejects
|
v
execute_action is skipped
|
v
generate_response

# This prevents the action from being executed.

16. Workflow Router

The Workflow Router contains deterministic workflow decisions.

The LLM is used for reasoning-oriented tasks such as:

Intent classification
Planning
Action interpretation
Natural-language understanding

The deterministic Router controls safety-sensitive execution decisions such as:

Step validation
Agent routing
Execution limits
Stop conditions
Retry decisions
Approval gates
Safe exits

# This prevents the LLM from having unrestricted control over critical workflow transitions.

17. Execution Limits

The workflow has a maximum execution-step limit.

This prevents an incorrectly generated plan or workflow loop from executing indefinitely.

The workflow tracks:

execution_count
max_execution_steps

# If the maximum execution limit is reached, the workflow stops safely.

18. Retry Handling

The workflow supports retries for transient failures.

Configured maximum retries:

MAX_RETRIES = 2

Example:

Attempt 1
|
| failure
v
RETRY
|
Attempt 2
|
| failure
v
RETRY
|
Attempt 3
|
v
SAFE_EXIT

The workflow also uses exponential backoff.

Example:

Retry 1
Backoff: 1 second

Retry 2
Backoff: 2 seconds

# After the retry limit is reached, the workflow stops safely instead of retrying indefinitely.

19. Retry Recovery

The system also supports recovery after a transient failure.

Example:

Supervisor
|
v
Failure
|
v
Workflow Router
|
v
RETRY
|
v
Supervisor executes again
|
v
SUCCESS

# This was tested through the retry integration test.

20. Timeout Handling

The workflow protects against agents that take too long to execute.

Configured agent execution timeout:

30 seconds

If an agent exceeds the timeout:

Agent Execution
|
| > 30 seconds
v
TIMEOUT
|
v
failure_type = timeout
|
v
retryable_failure = True

# This prevents a slow or stuck agent from blocking the complete workflow indefinitely.

21. Safe Exit

The workflow can safely terminate when execution cannot continue.

Examples include:

Maximum retries reached
Critical action rejected
Execution failure cannot be recovered
Execution limit reached
Workflow stopped

# Instead of continuing indefinitely, the system returns a controlled result.

22. Traceable Execution Flow

The workflow maintains execution information such as:

current_step
next_step
steps_executed
execution_status
retry_count
failure_type
approval_required
approval_status
approval_reason
stop_reason

The workflow also prints important execution decisions.

Example:

Steps Executed:

✓ intent_classification
✓ planning
✓ validate_action
✓ human_approval_approved
✓ execute_action
✓ generate_response

This makes the execution flow understandable and traceable.

A developer can determine:

What the user requested
Which intent was detected
What plan was generated
Which step was being executed
Which agent handled the step
Whether approval was required
Whether approval was granted or rejected
Whether an action was executed
Whether a retry occurred
Why the workflow stopped
What final answer was generated
==================================================

23. End-to-End Retrieval Example

User:

What is RAG?

Workflow:

User Query
|
v
Intent Classifier
|
v
retrieval
|
v
Planner
|
v
retrieve_documents
|
v
Supervisor
|
v
RetrievalAgent
|
v
Hybrid Search
|
v
Retrieved Context
|
v
generate_response
|
v
AnswerAgent
|
v
Final Answer
==================================================

24. End-to-End SQL Example

User:

How many files are available in database?

Workflow:

User Query
|
v
Intent Classifier
|
v
sql
|
v
Planner
|
v
execute_sql
|
v
Supervisor
|
v
SQLAgent
|
v
DatabaseTool
|
v
SQL Result
|
v
AnswerAgent
|
v
Final Answer
==================================================

25. End-to-End Business Action Example

User:

Send an email to priyaguptasru@gmail.com
with subject "One Day Leave Request"
and body "I would like to request one day leave."

Workflow:

User Query
|
v
Intent Classifier
|
v
action
|
v
Planner
|
v
validate_action
|
v
ActionAgent
|
v
send_email
|
v
Approval Required
|
v
Human Approval
|
v
Approved
|
v
execute_action
|
v
BusinessActionTool
|
v
Simulated Email
|
v
AnswerAgent
|
v
Final Response

Example execution trace:

✓ intent_classification
✓ planning
✓ validate_action
✓ human_approval_approved
✓ execute_action
✓ generate_response

Final response:

The email has been approved and simulated successfully.
No real email was sent.
==================================================

26. End-to-End Rejected Action Example

User:

Delete Adobe_Sample_PDF from database.

Workflow:

User Query
|
v
Intent Classifier
|
v
action
|
v
Planner
|
v
validate_action
|
v
Approval Required
|
v
Human Rejects
|
v
execute_action skipped
|
v
generate_response
|
v
Safe Exit

The important safety property is:

Human rejected
|
v
No destructive action executed
==================================================

27. Testing

The project includes tests for the major workflow capabilities.

Run the Interactive Workflow

From the Module-6 directory:

python -m app6.tests.test_agent_workflow

The application starts an interactive prompt:

Enter Query (exit/quit/q):

Example queries:

Hi

What is RAG?

How many files are available in database

List all documents available in database

Give summary of Adobe_Sample_PDF

How is AI_Paper different from IRS_Form_1040?

Delete Adobe_Sample_PDF from database

# Send an email to priyaguptasru@gmail.com

28. Retry Behavior Test

Run:

python -m app6.tests.test_retry_behavior

Expected behavior:

Attempt 1 -> RETRY
Attempt 2 -> RETRY
Attempt 3 -> SAFE_EXIT

This verifies:

Retry count
Maximum retry limit
Retry availability
Safe exit after retry exhaustion
Exponential backoff
==================================================

29. Retry Integration Test

Run:

python -m app6.tests.test_retry_integration

Expected flow:

Supervisor failure
|
v
WorkflowRouter -> RETRY
|
v
retry_execution
|
v
Supervisor executes again
|
v
SUCCESS

# This verifies that retry logic is connected to the Supervisor workflow.

30. Timeout Test

Run:

python -m app6.tests.test_timeout

Expected output:

AGENT EXECUTION TIMEOUT

Failure Type : timeout
Retryable Failure : True

# This verifies that a slow agent execution is detected and classified as retryable.

31. Environment Configuration

Create a .env file in the project root.

Example:

GROQ_API_KEY=your_api_key
MODEL_NAME=openai/gpt-oss-120b
TEMPERATURE=0
DATABASE_URL=postgresql://username:password@localhost:5432/module1_db

Do not commit actual API keys, passwords, database credentials, or other secrets to Git.

A safe approach is to maintain a .env.example file containing placeholders.

Example:

GROQ_API_KEY=your_api_key_here
MODEL_NAME=openai/gpt-oss-120b
TEMPERATURE=0
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
==================================================

32. Installation

Create the virtual environment:

python -m venv .venv6

Activate it:

.venv6\Scripts\activate

Install dependencies:

# pip install -r requirements.txt

33. Running the Application

From:

Module-6/

run:

python -m app6.tests.test_agent_workflow

The system initializes:

Initializing Agent Workflow...
Initializing Supervisor Agent...
Initializing Hybrid Search...
Initializing Semantic Search...
Initializing Keyword Search...
Hybrid Search Ready!
Supervisor Agent Ready!
Agent Workflow Ready!

Then enter a query:

# Enter Query (exit/quit/q):

34. Design Principles
    Separation of Responsibilities

Each component has a specific responsibility.

Intent Classifier
|
+--> Understand user intent

Planner
|
+--> Create execution plan

Supervisor
|
+--> Select responsible agent

Specialized Agents
|
+--> Perform specialized work

Tools
|
+--> Perform controlled operations

Workflow Router
|
+--> Make deterministic workflow decisions

Answer Agent
|
+--> Generate final response
LLM + Deterministic Control

The system uses the LLM where natural-language reasoning is useful, while deterministic Python logic controls safety-sensitive execution.

LLM-driven responsibilities
Intent classification
Planning
Natural-language interpretation
Action identification
Final response generation
Deterministic responsibilities
Agent routing
Execution limits
Retry limits
Timeout handling
Approval gates
Safe exits
Workflow transitions

# This hybrid approach provides better reliability and control than allowing the LLM to make every workflow decision.

35. Safety Model

Potentially risky business actions require human approval.

Examples:

delete
duplicate
send_email
write
update

The safety model is:

User Request
|
v
Action Validation
|
v
Approval Evaluation
|
v
Human Approval
|
v
Execution

The BusinessActionTool itself does not make the approval decision.

# Approval is handled by the workflow and approval service before the action is executed.

36. Failure Handling

The system handles different failure conditions.

Examples:

execution_error
timeout

Retryable failures can be retried within the configured limit.

Example:

Failure
|
v
Is retryable?
|
+---- No ----> Safe Exit
|
Yes
|
v
Retry Available?
|
+---- No ----> Safe Exit
|
Yes
|
v
Retry

# This prevents infinite loops and uncontrolled execution.

37. Observability

The workflow prints important execution information, including:

Current Step
Execution Count
Selected Agent
Agent Result
Router Decision
Next Step
Approval Status
Retry Count
Failure Type
Final Result
Steps Executed

Example:

Current Step : execute_action
Execution Count : 3/10

Selected Agent : ActionAgent

Action : send_email

Approval Status : approved

Action Status : simulated

# Next Step : generate_response

38. Module-6 Requirements Status

The Module-6 implementation covers the following requirements:

✓ 1. Intent interpretation and step-by-step execution
✓ 2. Specialized agents
✓ 3. Supervisor Agent
✓ 4. Step-based planning and execution limits
✓ 5. Deterministic + agent-driven workflow
✓ 6. Database, retrieval and business-action tools
✓ 7. Human-in-the-loop approval
✓ 8. Routing based on failures, confidence and workflow state
✓ 9. Retry, timeout and safe-exit handling
✓ 10. Traceable execution flow
==================================================

39. Validation Completed

The following scenarios have been tested:

✓ Intent classification
✓ Dynamic planning
✓ Specialized agent routing
✓ Retrieval workflow
✓ SQL workflow
✓ Summary workflow
✓ Comparison workflow
✓ Business action validation
✓ Business action execution
✓ Human approval
✓ Approval rejection
✓ Approval resume
✓ Retry behavior
✓ Retry exhaustion
✓ Failure -> Retry -> Success
✓ Timeout detection
✓ Timeout classification
✓ Safe exit
✓ Execution traceability
✓ End-to-end workflow
==================================================

40. Final End-to-End Demonstration

A recommended final demonstration is:

Send an email to priyaguptasru@gmail.com
with subject "One Day Leave Request"
and body "I would like to request one day leave."

Expected flow:

USER QUERY
|
v
INTENT CLASSIFIER
|
v
action
|
v
PLANNER
|
v
validate_action
|
v
SUPERVISOR
|
v
ACTION AGENT
|
v
send_email
|
v
APPROVAL REQUIRED
|
v
PAUSED
|
v
USER APPROVES
|
v
RESUMED
|
v
BUSINESS ACTION TOOL
|
v
SIMULATED EMAIL
|
v
ANSWER AGENT
|
v
FINAL RESPONSE

This single workflow demonstrates:

LLM-driven intent understanding
Planning
Supervisor orchestration
Specialized agent execution
Business tool usage
Human-in-the-loop approval
Safe action execution
Final response generation
Traceable execution
==================================================

41. Key Takeaway

Module-6 demonstrates a production-style Agentic AI architecture where:

LLM Reasoning +
Specialized Agents +
Planner +
Supervisor +
Deterministic Router +
Tools +
Human Approval +
Retry Handling +
Timeout Handling +
Safe Exits +
Traceability

work together to create a controlled and reliable Agentic AI workflow.

The key design principle is:

# Use the LLM for intelligence and reasoning, while deterministic application logic controls execution, safety, retries, approvals, and failure handling.

==================================================

42. Project Completion

Module-6 has implemented and validated the planned Agentic AI orchestration capabilities through:

End-to-end workflow execution
Specialized agent execution
Retrieval testing
SQL testing
Business action testing
Human approval testing
Approval rejection testing
Approval resume testing
Retry testing
Retry integration testing
Retry exhaustion testing
Timeout testing
Safe-exit testing
Execution traceability
Final end-to-end demonstration

The system is designed to be generic and extensible so that additional agents, tools, business actions, and enterprise integrations can be added without redesigning the complete orchestration architecture.
