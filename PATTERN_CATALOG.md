# PromptSpec Pattern Catalog

> **Read this if you just want the taxonomy.** This is the MD view of the catalog. The method CSV is the source of truth; [`catalog/patterns.json`](catalog/patterns.json) is the generated machine-readable view.

The catalog contains **30 prompt-engineering patterns** across **5 categories**.

All patterns in this catalog are derived from published prompt-engineering literature. They are taxonomy entries, not empirically observed corpus findings.

Each pattern lists the **prompt component type(s)** it relates to in the PromptSpec model (`PROFILE_ROLE`, `DIRECTIVE`, `CONTEXT`, `PROCEDURAL_STEPS`, `EXAMPLES`, `OUTPUT_FORMAT`, `CONSTRAINTS`). The binding *semantics* (whether a pattern is primary in, modifies, or spans those components) are defined in the associated publication, not in this catalog.

## Summary

| Pattern | Category | Component(s) |
|---|---|---|
| FewShot | In-Context Learning | `DIRECTIVE`, `EXAMPLES` |
| ZeroShot | In-Context Learning | `DIRECTIVE` |
| ChainOfThought | Reasoning | `PROCEDURAL_STEPS` |
| ComplexCoT | Reasoning | `PROCEDURAL_STEPS` |
| LeastToMost | Reasoning | `PROCEDURAL_STEPS` |
| PlanAndSolve | Reasoning | `PROCEDURAL_STEPS` |
| ReverseCoT | Reasoning | `PROCEDURAL_STEPS` |
| StructuredCoT | Reasoning | `OUTPUT_FORMAT`, `PROCEDURAL_STEPS` |
| FactCheckList | Output Control | `CONSTRAINTS`, `PROCEDURAL_STEPS` |
| OutputAutomater | Output Control | `OUTPUT_FORMAT` |
| Recipe | Output Control | `DIRECTIVE`, `PROCEDURAL_STEPS` |
| Reflection | Output Control | `CONSTRAINTS`, `PROCEDURAL_STEPS` |
| SchemaSpecs | Output Control | `OUTPUT_FORMAT` |
| SelfCalibration | Output Control | `CONSTRAINTS`, `PROCEDURAL_STEPS` |
| SelfVerification | Output Control | `CONSTRAINTS`, `PROCEDURAL_STEPS` |
| Template | Output Control | `DIRECTIVE`, `OUTPUT_FORMAT` |
| VisualizationGenerator | Output Control | `OUTPUT_FORMAT` |
| ContextManager | Context Control | `CONTEXT`, `DIRECTIVE`, `PROCEDURAL_STEPS` |
| MetaLanguageCreation | Context Control | `CONTEXT`, `DIRECTIVE` |
| Persona | Context Control | `CONTEXT`, `OUTPUT_FORMAT`, `PROFILE_ROLE` |
| AlternativeApproaches | Meta-Directives | `DIRECTIVE`, `PROCEDURAL_STEPS` |
| CognitiveVerifier | Meta-Directives | `DIRECTIVE`, `PROCEDURAL_STEPS` |
| FlippedInteraction | Meta-Directives | `DIRECTIVE` |
| GamePlay | Meta-Directives | `DIRECTIVE` |
| InfiniteGeneration | Meta-Directives | `DIRECTIVE` |
| InstructionSelection | Meta-Directives | `DIRECTIVE`, `PROCEDURAL_STEPS` |
| QuestionRefinement | Meta-Directives | `DIRECTIVE` |
| RAR | Meta-Directives | `DIRECTIVE`, `PROCEDURAL_STEPS` |
| RE2 | Meta-Directives | `DIRECTIVE` |
| RefusalBreaker | Meta-Directives | `CONSTRAINTS`, `DIRECTIVE` |


## In-Context Learning

### FewShot

Provide a few exemplar input-output pairs to guide the model.

**Component(s):** `DIRECTIVE`, `EXAMPLES`

*Placeholder form:*

```
Instruction: {QUESTION}
Examples:
Input: {EXAMPLE_INPUT_1}
Output: {EXAMPLE_OUTPUT_1}
Input: {EXAMPLE_INPUT_2}  Output: {EXAMPLE_OUTPUT_2}

Now apply to: {INPUT_DATA}
```

*Example:*

```
Translate English to French.

Examples:
Input: Night
Output: Nuit
Input: Morning
Output: Matin
Input: Fall
Output: Automne

Now apply to:
Winter
```

*Formalization:*

~~~promptspec
pattern FewShot
category IN_CONTEXT_LEARNING

variables {
    task* : string              "Description of the task"
    examples+ : list            "List of example objects"
    num_examples? : int = 3     "How many examples to show"
    selection? : enum = "first" | ["first", "random", "all"]
}

template ```
Task: {{task}}

Here are some examples:
{{^examples num_examples}}
Input: {{input}}
Output: {{output}}
{{/examples}}

Now do the same for:
```
~~~

> Mutually exclusive with ZeroShot.

### ZeroShot

Provide no examples to guide the task.

**Component(s):** `DIRECTIVE`

*Placeholder form:*

```
Instruction: {QUESTION}
Input data: {INPUT_DATA}
```

*Example:*

```
Translate English to French.

Example:
Input: Night
Output: Nuit

Now apply to:
Morning
```

*Formalization:*

~~~promptspec
pattern ZeroShot
category IN_CONTEXT_LEARNING

variables {
    question* : string
    input_data? : string
}

template ```
Instruction: {{question}}
{{#input_data}}
Input data: {{input_data}}
{{/input_data}}
```
~~~

> Represents the default prompting strategy when no demonstrations are provided.


## Reasoning

### ChainOfThought

Encourage step-by-step reasoning before final answer.

**Component(s):** `PROCEDURAL_STEPS`

*Placeholder form:*

```
Let’s think step by step.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Let’s think step by step.

Solve the following math problem:

Roger has 5 apples and gives 2 to Josh and 1 to Jane. How much is left?
```

*Formalization:*

~~~promptspec
pattern ChainOfThought
category REASONING

variables {
    question* : string
    input_data? : string
    reasoning_cue? : string = "Let's think step by step."
}

template ```
{{reasoning_cue}}

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### ComplexCoT

Generate multiple reasoning chains and prefer answers supported by the most complex and detailed chains.

**Component(s):** `PROCEDURAL_STEPS`

*Placeholder form:*

```
Generate {PATH_COUNT} detailed reasoning paths for the following question.
Prioritize the most complex and detailed paths, then use their majority answer as the final answer.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Solve the following problem step by step. Generate multiple reasoning paths, making each as detailed as possible.
Among the most complex and detailed paths, take the majority answer as the final answer.

Solve the following math problem:

{QUESTION}
{INPUT_DATA}
```

*Formalization:*

~~~promptspec
pattern ComplexCoT
category REASONING

variables {
    question* : string
    input_data? : string
    path_count? : int = 3
}

template ```
Generate {{path_count}} reasoning paths, each as detailed as possible.
Among the most complex and detailed paths, take the majority answer as the final answer.

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### LeastToMost

Decompose into easiest sub-problems first, then harder ones.

**Component(s):** `PROCEDURAL_STEPS`

*Placeholder form:*

```
{QUESTION}
{INPUT_DATA}

Decompose problem into simpler subproblems: {SUBPROBLEM_1}, {SUBPROBLEM_2}, …

Solve each subproblem in sequence.

Combine subproblem solutions into final answer.
```

*Example:*

```
Solve the following problem step by step. First, decompose the problem into smaller subproblems.
Then, solve each subproblem in sequence.
Finally, combine the solutions to produce the final answer.

Question:
A school cafeteria has 312 apples. They want to distribute them equally to 24 students. Each student eats 2 apples, and the rest are saved. How many apples are saved?
```

*Formalization:*

~~~promptspec
pattern LeastToMost
category REASONING

variables {
    question* : string
    input_data? : string
    subproblems... : list
}

template ```
{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}

Decompose problem into simpler subproblems:
{{^subproblems}}
  - {{.}}
{{/subproblems}}

Solve each subproblem in sequence.

Combine subproblem solutions into final answer.
```
~~~

### PlanAndSolve

First plan sub-problems, then solve them step by step.

**Component(s):** `PROCEDURAL_STEPS`

*Placeholder form:*

```
Step 1: Generate a high-level plan of solution steps: {PLAN}
Step 2: Execute each step in order.
Step 3: Produce final answer.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
First, generate a clear plan outlining the steps needed to solve the problem.
Then, follow the plan step by step to produce the final answer.

Question:
If a train travels 120 km in 2 hours, and then 180 km in 3 hours, what is its average speed across the whole trip?
```

*Formalization:*

~~~promptspec
pattern PlanAndSolve
category REASONING

variables {
    question* : string
    input_data? : string
    plan_label? : string = "PLAN"
}

template ```
Step 1: Generate a high-level plan of solution steps: {{plan_label}}
Step 2: Execute each step in order.
Step 3: Produce final answer.

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### ReverseCoT

Generate reasoning steps after giving the answer, to simulate justification.

**Component(s):** `PROCEDURAL_STEPS`

*Placeholder form:*

```
{QUESTION}
{INPUT_DATA}

First, output the final answer only.
Then, generate the reasoning steps that justify the answer.
```

*Example:*

```
Please answer the question.
First, state the final answer directly.
Then, explain the reasoning that justifies your answer.
 “The answer is 57. Reasoning: Because 23+47…”
```

*Formalization:*

~~~promptspec
pattern ReverseCoT
category REASONING

variables {
    question* : string
    input_data? : string
}

template ```
{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}

First, output the final answer only.
Then, generate the reasoning steps that justify the answer.
```
~~~

### StructuredCoT

Structure reasoning with program-like constructs (loops, branches).

**Component(s):** `OUTPUT_FORMAT`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Use structured reasoning constructs:
- Sequencing: {STEP_1}, {STEP_2}, …
- Branching: IF {CONDITION} THEN {ACTION}
- Looping: FOR {ITEM} IN {SET} DO {ACTION}
End with final answer.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Sequencing: Initialize sum = 0
Looping: FOR i=1..10 IF i is even THEN sum += i
End with final answer.
```

*Formalization:*

~~~promptspec
pattern StructuredCoT
category REASONING

variables {
    question* : string
    input_data? : string
    steps... : list
    condition? : string
    action? : string
    item? : string
    set_name? : string
}

template ```
Use structured reasoning constructs:
{{#steps}}
- Sequencing:
{{^steps}}
  - {{.}}
{{/steps}}
{{/steps}}
{{#condition}}
- Branching: IF {{condition}} THEN {{action}}
{{/condition}}
{{#item}}
- Looping: FOR {{item}} IN {{set_name}} DO {{action}}
{{/item}}
End with final answer.

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~


## Output Control

### FactCheckList

Use a checklist to confirm factual accuracy of the output.

**Component(s):** `CONSTRAINTS`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Extract facts from output: {FACT_1}, {FACT_2}, …

Insert fact list at {OUTPUT_LOCATION}

Ensure facts are fundamental to correctness.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Extract facts from output: {Capital of Australia = Canberra}

Insert fact list at end of answer

Ensure facts are fundamental to correctness.
```

*Formalization:*

~~~promptspec
pattern FactCheckList
category OUTPUT_CONTROL

variables {
    question* : string
    input_data? : string
    facts... : list
    output_location? : string = "end of answer"
}

template ```
Extract facts from output:
{{^facts}}
  - {{.}}
{{/facts}}

Insert fact list at {{output_location}}.

Ensure facts are fundamental to correctness.

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### OutputAutomater

The model outputs an executable artifact (typically a script) that automates the steps it recommends, instead of only describing them.

**Component(s):** `OUTPUT_FORMAT`

*Placeholder form:*

```
Whenever your output contains at least one manual step, generate an executable {LANGUAGE} script that automates those steps.

Task: {TASK}
```

*Example:*

```
Whenever your response includes steps a user would otherwise carry out by hand, also output a runnable Bash script that performs those steps automatically.

Task: set up a Python virtual environment and install the project's dependencies.
```

*Formalization:*

~~~promptspec
pattern OutputAutomater
category OUTPUT_CONTROL

variables {
    language* : string
    task* : string
}

template ```
Whenever your output contains at least one manual step, generate an executable {{language}} script that automates those steps.

Task: {{task}}
```
~~~

### Recipe

Provide a repeatable recipe-style sequence for solving tasks.

**Component(s):** `DIRECTIVE`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
I would like to achieve {INPUT_DATA}.
Provide a complete sequence of steps for me.
Fill in any missing steps.
Identify any unnecessary steps.
```

*Example:*

```
List ordered steps: STEP_1 = Preheat oven, STEP_2 = Mix flour and sugar, STEP_3 = Bake for 30 minutes
Fill in missing steps if necessary.
Identify unnecessary steps if present.
```

*Formalization:*

~~~promptspec
pattern Recipe
category OUTPUT_CONTROL

variables {
    pronoun? : enum = "I" | ["I", "You", "We"]
    goal* : string
    steps... : list
    complete? : bool = true
    missing? : bool = true
    unnecessary? : bool = false
}

template ```
{{pronoun}} would like to achieve {{goal}}.
{{#complete}}
Provide a complete sequence of steps.
{{/complete}}
{{#missing}}
Fill in any missing steps.
{{/missing}}
{{#unnecessary}}
Identify any unnecessary steps.
{{/unnecessary}}
{{#steps}}
Steps to consider:
{{^steps}}
  - {{.}}
{{/steps}}
{{/steps}}```
~~~

### Reflection

Model reflects on its first output, critiques, and improves it.

**Component(s):** `CONSTRAINTS`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Step 1: Generate initial answer: {ANSWER_1}
Step 2: Critique reasoning and assumptions in {ANSWER_1}
Step 3: Revise output based on critique.
Final Answer = {ANSWER_REVISED}


{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Whenever you generate an answer
Explain the reasoning and assumptions behind your
answer
(Optional) ...so that I can improve my question
```

*Formalization:*

~~~promptspec
pattern Reflection
category OUTPUT_CONTROL

variables {
    trigger? : enum = "AFTER_ANSWER" | ["ALWAYS", "AFTER_ANSWER"]
    explain? : bool = true             "Explain reasoning"
    assumptions? : bool = true         "State assumptions"
    improvements? : bool = false       "Suggest improvements"
}

trigger AFTER_ANSWER

template ```
{{#trigger}}
After generating your answer:
{{/trigger}}
{{#explain}}
Explain the reasoning behind your answer.
{{/explain}}
{{#assumptions}}
State any assumptions you made.
{{/assumptions}}
{{#improvements}}
Suggest potential improvements.
{{/improvements}}
```
~~~

### SchemaSpecs

Define schema/structure the model must follow.

**Component(s):** `OUTPUT_FORMAT`

*Placeholder form:*

```
Force output into schema: {SCHEMA}

Populate schema fields: {FIELD_1}, {FIELD_2}, …

{QUESTION}
```

*Example:*

```
Output must follow schema: {Title:…, Author:…, Year:…}”
```

*Formalization:*

~~~promptspec
pattern SchemaSpecs
category OUTPUT_CONTROL

variables {
    schema* : string
    fields... : list
    question* : string
}

template ```
Force output into schema: {{schema}}
{{#fields}}

Populate schema fields:
{{^fields}}
  - {{.}}
{{/fields}}
{{/fields}}

{{question}}
```
~~~

### SelfCalibration

After answering, the model estimates its confidence that the answer is correct and revises or abstains when that confidence is low.

**Component(s):** `CONSTRAINTS`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Answer the question: {QUESTION}
Then state your confidence (0–100%) that the answer is correct, with a brief justification.
If confidence is below {THRESHOLD}, revise or abstain.
```

*Example:*

```
Answer the question. Then state your confidence from 0–100% that the answer is correct, with a one-line justification. If your confidence is below 60%, revise your answer or say you are not sure.

Question: What is the boiling point of water at the summit of Mount Everest?
```

*Formalization:*

~~~promptspec
pattern SelfCalibration
category OUTPUT_CONTROL

variables {
    question* : string
    threshold? : int = 60
}

trigger AFTER_ANSWER

template ```
Answer the question: {{question}}
Then state your confidence (0-100%) that the answer is correct, with a brief justification.
If confidence is below {{threshold}}, revise or abstain.
```
~~~

### SelfVerification

Model checks and verifies its own answers before finalizing.

**Component(s):** `CONSTRAINTS`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Step 1: Generate an initial answer: {ANSWER_1}

Step 2: Verify whether {ANSWER_1} satisfies constraints: {CONSTRAINTS}

Step 3: If verification fails, explain issue and correct.

Final Answer = {VERIFIED_ANSWER}

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Step 1: Generate an initial answer.
Step 2: Verify whether the answer satisfies the requirements.
Step 3: If verification fails, explain the issues.
Final Answer: {final answer}

Question:
What is the capital of Australia?
Final Answer: Canberra
```

*Formalization:*

~~~promptspec
pattern SelfVerification
category OUTPUT_CONTROL

variables {
    question* : string
    input_data? : string
    constraints... : list
}

template ```
Step 1: Generate an initial answer.

Step 2: Verify whether the answer satisfies constraints:
{{^constraints}}
  - {{.}}
{{/constraints}}

Step 3: If verification fails, explain issue and correct.

Final Answer = verified answer

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### Template

Use a reusable template to structure answers consistently.

**Component(s):** `DIRECTIVE`, `OUTPUT_FORMAT`

*Placeholder form:*

```
Use template: {TEMPLATE}

Insert content into placeholders: {PLACEHOLDER_1}, {PLACEHOLDER_2}, …

Preserve formatting of template.

{QUESTION}
{INPUT_DATA}
```

*Formalization:*

~~~promptspec
pattern Template
category OUTPUT_CONTROL

variables {
    template* : string
    placeholders... : list
    question* : string
    input_data? : string
}

template ```
Use template: {{template}}

Insert content into placeholders:
{{^placeholders}}
  - {{.}}
{{/placeholders}}

Preserve formatting of template.

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### VisualizationGenerator

Generate visual or tabular representations (charts, tables).

**Component(s):** `OUTPUT_FORMAT`

*Placeholder form:*

```
Generate visualization: {VISUALIZATION_TYPE}

Structure data for tool: {TOOL}

Output must be formatted for visualization.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Generate visualization: bar chart
Structure data for tool: matplotlib
Output must be formatted for visualization.
```

*Formalization:*

~~~promptspec
pattern VisualizationGenerator
category OUTPUT_CONTROL

variables {
    visualization_type* : string
    tool? : string
    question* : string
    input_data? : string
}

template ```
Generate visualization: {{visualization_type}}
{{#tool}}

Structure data for tool: {{tool}}
{{/tool}}

Output must be formatted for visualization.

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~


## Context Control

### ContextManager

Explicitly control what context the model uses to avoid drift.

**Component(s):** `CONTEXT`, `DIRECTIVE`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Set scope: {SCOPE}
Include only: {INCLUDE_ITEMS}
Exclude always: {EXCLUDE_ITEMS}
If signal = "reset", discard accumulated context and restart within {SCOPE}.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Within scope X
Please consider Y
Please ignore Z
(Optional) start over
```

*Formalization:*

~~~promptspec
pattern ContextManager
category CONTEXT_CONTROL

variables {
    scope* : string
    include_items... : list
    exclude_items... : list
    reset_signal? : string = "reset"
    question* : string
    input_data? : string
}

template ```
Set scope: {{scope}}
{{#include_items}}
Include only:
{{^include_items}}
  - {{.}}
{{/include_items}}
{{/include_items}}
{{#exclude_items}}
Exclude always:
{{^exclude_items}}
  - {{.}}
{{/exclude_items}}
{{/exclude_items}}
{{#reset_signal}}
If signal = "{{reset_signal}}", discard accumulated context and restart within {{scope}}.
{{/reset_signal}}

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### MetaLanguageCreation

Define custom shorthand notation and its semantics for the model to apply in the rest of the prompt or conversation.

**Component(s):** `CONTEXT`, `DIRECTIVE`

*Formalization:*

~~~promptspec
pattern MetaLanguageCreation
category CONTEXT_CONTROL

variables {
    shorthand* : string
    meaning* : string
    question* : string
    input_data? : string
}

template ```
In this conversation, interpret "{{shorthand}}" to mean: {{meaning}}

Whenever I use "{{shorthand}}", apply that meaning in the rest of the prompt or conversation.

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~

### Persona

Adopt a role/persona to shape style/voice.

**Component(s):** `CONTEXT`, `OUTPUT_FORMAT`, `PROFILE_ROLE`

*Placeholder form:*

```
Act as {PERSONA}
Provide outputs that {PERSONA} would create

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Act as a helpful math tutor.
Provide outputs that a helpful math tutor would create

Explain how to solve the following equation step by step:
2x + 5 = 15
```

*Formalization:*

~~~promptspec
pattern Persona
category CONTEXT_CONTROL

variables {
    persona* : string
    question* : string
    input_data? : string
}

template ```
Act as {{persona}}
Provide outputs that {{persona}} would create

{{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
```
~~~


## Meta-Directives

### AlternativeApproaches

Suggest multiple different ways to solve the same problem.

**Component(s):** `DIRECTIVE`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Given input task: {TASK}

List alternative approaches: {APPROACH_1}, {APPROACH_2}, …

(Optional) Compare pros/cons of each.

{QUESTION}
```

*Example:*

```
Within scope X, if there are alternative ways to accom-
plish the same thing, list the best alternate approaches
(Optional) compare/contrast the pros and cons of each
approach
(Optional) include the original way that I asked
(Optional) prompt me for which approach I would like
to use
```

*Formalization:*

~~~promptspec
pattern AlternativeApproaches
category META_DIRECTIVES

variables {
    task* : string
    approach_count? : int = 3
    compare? : bool = true
    question? : string
}

template ```
Given input task: {{task}}

List {{approach_count}} alternative approaches.
{{#compare}}

Compare pros and cons of each.
{{/compare}}
{{#question}}

{{question}}
{{/question}}
```
~~~

### CognitiveVerifier

Add explicit verification of reasoning correctness.

**Component(s):** `DIRECTIVE`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Given input question: {QUESTION}

Generate subquestions: {Q1}, {Q2}, …

Answer each subquestion.
Combine subanswers into final answer.
```

*Example:*

```
When you are asked a question, follow these rules
Generate a number of additional questions that would
help more accurately answer the question
Combine the answers to the individual questions to
produce the final answer to the overall question
```

*Formalization:*

~~~promptspec
pattern CognitiveVerifier
category META_DIRECTIVES

variables {
    question* : string
    subquestion_count? : int = 3
}

template ```
Given input question: {{question}}

Generate {{subquestion_count}} subquestions.

Answer each subquestion.
Combine subanswers into final answer.
```
~~~

### FlippedInteraction

Model asks the user questions instead of directly answering.

**Component(s):** `DIRECTIVE`

*Placeholder form:*

```
Instead of answering directly:
Generate subquestions to ask user: {Q1}, {Q2}, …

Stop when {GOAL_CONDITION} is satisfied.

{QUESTION}
```

*Example:*

```
I would like you to ask me questions to achieve X
You should ask questions until this condition is met or
to achieve this goal (alternatively, forever)
(Optional) ask me the questions one at a time, two at
a time, etc.
```

*Formalization:*

~~~promptspec
pattern FlippedInteraction
category META_DIRECTIVES

variables {
    question* : string
    goal_condition? : string
    question_count? : int = 1
}

template ```
Instead of answering directly:
Generate {{question_count}} subquestions to ask the user.
{{#goal_condition}}

Stop when {{goal_condition}} is satisfied.
{{/goal_condition}}

{{question}}
```
~~~

### GamePlay

Frame the task as a game to increase engagement.

**Component(s):** `DIRECTIVE`

*Placeholder form:*

```
Frame task as a game: {GAME_NAME}

Define rules: {RULE_1}, {RULE_2}, …

Interaction must proceed according to rules.

{QUESTION}
```

*Example:*

```
Create a game around practicing French vocabulary.
The game must define one or more fundamental rules.
The rules should constrain how the user can respond.
The interaction must proceed according to the defined rules.
```

*Formalization:*

~~~promptspec
pattern GamePlay
category META_DIRECTIVES

variables {
    game_name* : string
    rules+ : list
    question* : string
}

template ```
Frame task as a game: {{game_name}}

Define rules:
{{^rules}}
  - {{.}}
{{/rules}}

Interaction must proceed according to rules.

{{question}}
```
~~~

### InfiniteGeneration

Model generates continuously, with prompts to “keep going.”

**Component(s):** `DIRECTIVE`

*Placeholder form:*

```
Continuously generate {OUTPUT_TYPE}

Batch size = {N} outputs per turn

Stop when {STOP_CONDITION}

{QUESTION}
```

*Example:*

```
I would like you to generate a name
and job forever. I am going to provide a
template for your output. Everything in all caps is a
placeholder. Any time that you generate text, try to
fit it into one of the placeholders that I list. Please
preserve the formatting and overall template that I
provide: https://myapi.com/NAME/profile/JOB
```

*Formalization:*

~~~promptspec
pattern InfiniteGeneration
category META_DIRECTIVES

variables {
    output_type* : string
    batch_size? : int = 1
    stop_condition? : string
    question* : string
}

template ```
Continuously generate {{output_type}}

Batch size = {{batch_size}} outputs per turn
{{#stop_condition}}

Stop when {{stop_condition}}
{{/stop_condition}}

{{question}}
```
~~~

### InstructionSelection

Given several candidate instructions for a task, the model selects the most appropriate one and then carries out the task using it.

**Component(s):** `DIRECTIVE`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Candidate instructions: {INST_1}, {INST_2}, … {INST_N}
Select the instruction best suited to {TASK}, state your choice, then carry out the task using it.

{INPUT_DATA}
```

*Example:*

```
Here are three candidate instructions for summarizing a contract:
A) "Summarize the contract in plain English."
B) "List each obligation and its responsible party."
C) "Extract key dates, amounts, and termination clauses."
Choose the one best suited to a compliance review, state your choice, then apply it to the contract below.

Contract: {CONTRACT}
```

*Formalization:*

~~~promptspec
pattern InstructionSelection
category META_DIRECTIVES

variables {
    instructions+ : list
    task* : string
    input_data* : string
}

template ```
Candidate instructions:
{{^instructions}}
  - {{.}}
{{/instructions}}
Select the instruction best suited to {{task}}, state your choice, then carry out the task using it.

{{input_data}}
```
~~~

### QuestionRefinement

Improve or reformulate the user’s query for clarity.

**Component(s):** `DIRECTIVE`

*Placeholder form:*

```
Take input query: {RAW_QUESTION}

Suggest a refined version: {REFINED_QUESTION}

(Optional) Ask user to confirm refinement.

{QUESTION}
```

*Example:*

```
Within scope of cybersecurity and security risks, suggest a better version of the question
to use instead
(Optional) prompt me if I would like to use the better
version instead

How to use Windows?
```

*Formalization:*

~~~promptspec
pattern QuestionRefinement
category META_DIRECTIVES

variables {
    raw_question* : string
    ask_confirmation? : bool = true
}

template ```
Take input query: {{raw_question}}

Suggest a refined version.
{{#ask_confirmation}}

Ask user to confirm refinement.
{{/ask_confirmation}}
```
~~~

### RAR

In one prompt, the model first rephrases and expands the question, then answers the rephrased version.

**Component(s):** `DIRECTIVE`, `PROCEDURAL_STEPS`

*Placeholder form:*

```
Rephrase and expand the following question, then answer your rephrased version.

Question: {QUESTION}
```

*Example:*

```
Rephrase and expand the question below, then answer the expanded version.

Question: Was Ada Lovelace born before the telephone was invented?
```

*Formalization:*

~~~promptspec
pattern RAR
category META_DIRECTIVES

variables {
    question* : string
}

template ```
Rephrase and expand the following question, then answer your rephrased version.

Question: {{question}}
```
~~~

### RE2

Re-reading: instruct the model to read the question again before answering, to improve reasoning.

**Component(s):** `DIRECTIVE`

*Placeholder form:*

```
Read the question again: {QUESTION}
{INPUT_DATA}

Now answer the question.
```

*Example:*

```
Read the question again before answering.

Question: Which city hosted the 2016 Summer Olympics?
Now answer the question.
```

*Formalization:*

~~~promptspec
pattern RE2
category META_DIRECTIVES

variables {
    question* : string
    input_data? : string
}

template ```
Read the question again: {{question}}
{{#input_data}}
{{input_data}}
{{/input_data}}
Now answer the question.
```
~~~

### RefusalBreaker

Overcome model refusals by reframing the request.

**Component(s):** `CONSTRAINTS`, `DIRECTIVE`

*Placeholder form:*

```
If refusal occurs:
Step 1: State refusal reason.
Step 2: Reframe request into
alternative query: {ALT_QUERY}

{QUESTION}
```

*Example:*

```
Whenever you can’t answer a question
Explain why you can’t answer the question
Provide one or more alternative wordings of the ques-
tion that you could answer
```

*Formalization:*

~~~promptspec
pattern RefusalBreaker
category META_DIRECTIVES

variables {
    question* : string
    alt_query? : string
}

trigger ON_REFUSAL

template ```
If refusal occurs:
Step 1: State refusal reason.
Step 2: Reframe request into an alternative query.
{{#alt_query}}
Alternative query: {{alt_query}}
{{/alt_query}}

{{question}}
```
~~~
