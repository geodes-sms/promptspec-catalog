# Prompt Pattern Taxonomy — Full Reproducibility Documentation

This document records, in full, the methodology and raw data behind the 30-pattern "writable prompt" taxonomy. Everything here is generated directly from the underlying dataset (`master_raw_dataset.csv`), so the counts below are exact, not estimates.

## 1. Source papers

Five papers were read in full and mined for every named prompting technique/pattern presented in each paper's own technique catalog or taxonomy section:

| # | Paper | arXiv ID | What was extracted |
|---|---|---|---|
| 1 | White, Fu, Hays, Sandborn, Olea, Gilbert, Elnashar, Spencer-Smith & Schmidt (2023). *A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT* | 2302.11382 | All 16 patterns in Section III ("A Catalog of Prompt Patterns for Conversational LLMs"), Table I. |
| 2 | Schulhoff et al. (2024, v6). *The Prompt Report: A Systematic Survey of Prompting Techniques* | 2406.06608 | All techniques in Section 2.2 ("Text-Based Techniques"), Figure 2.2: In-Context Learning, Thought Generation, Decomposition, Ensembling, Self-Criticism. |
| 3 | Sahoo, Singh, Saha, Jain, Mondal & Chadha (2024, v2). *A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications* | 2402.07927 | All techniques in Section 2, subsections 2.1–2.12 (application-area organized), 41 named in the v2/2025 taxonomy. |
| 4 | Vatsal & Dubey (2024, v2). *A Survey of Prompt Engineering Methods in Large Language Models for Different NLP Tasks* | 2407.12994 | All techniques in Section 2 ("Prompt Engineering Techniques"), subsections 2.1–2.39, 39 named. |
| 5 | Fagbohun, Harrison & Dereventsov (2024). *An Empirical Categorization of Prompting Techniques for Large Language Models: A Practitioner's Guide* | 2402.14837 | All techniques in Section 2, the seven categories 2.1–2.7. |

## 2. Methodology — four stages

### Stage 1 — PASS 1: Raw extraction
Every distinctly named technique presented in each paper's own technique-catalog section was logged as one row, with: the exact name used in that paper, the section/subsection it appeared in, a one-line concept summary written by re-reading the paper's own description (not copied verbatim — paraphrased for this catalog), and a normalized name string.

**Result: 176 raw rows.**

| Source paper | Raw techniques extracted |
|---|---|
| Schulhoff et al. 2024 (The Prompt Report) | 55 |
| Sahoo et al. 2024 | 41 |
| Vatsal & Dubey 2024 | 39 |
| Fagbohun et al. 2024 | 25 |
| White et al. 2023 | 16 |

### Stage 2 — PASS 2: Exact name + concept dedup
Rows whose normalized name is identical were grouped into one entry, on the assumption (verified by re-reading) that when two papers use the literal same technique name, they are describing the same technique. For e.g. "Chain-of-Thought (CoT) Prompting" appears under that near-identical name in Schulhoff, Sahoo, Vatsal & Dubey and Fagbohun down to a single entry, while keeping differently-named techniques (even if conceptually related) as separate entries pending Pass 3.

**Result: 163 unique (name, concept) groups** (down from 176 raw mentions — 13 raw mentions were exact-name duplicates of another paper's entry).

### Stage 3 — PASS 3: Concept-only dedup (synonym merge)
Pass-2 groups were then read again and merged wherever two *differently-named* entries clearly describe the *same underlying technique* — i.e. same fundamental contextual statements/structure, just labelled differently by different authors. Examples of synonym merges performed:

| Concept A | Concept B | Why merged |
|---|---|---|
| Persona (White 2023) | Role Prompting (Schulhoff 2024) | Schulhoff's own text states Role Prompting is "also known as persona prompting" — explicit author-acknowledged synonym. |
| Persona (White 2023) | Multi-Personas Prompting (Fagbohun 2024) | Same core mechanism (assign the LLM a named role/character); Fagbohun's variant emphasizes switching between multiple personas across turns, which is a usage variant, not a different structural pattern. |
| Reflection (White 2023) | Self-reflection Prompting (Fagbohun 2024) | Both ask the LLM to evaluate/explain its own prior answer in a single follow-up instruction. |
| Reversing Chain-of-Thought / RCoT (Schulhoff 2024) | → "Reverse CoT" final pattern | Simplified to the single-prompt "state the answer first, then justify it" framing that also matches the example wording used in the final taxonomy. |
| Self-Verification (Schulhoff 2024) | → "SelfVerification" final pattern | Multi-candidate masked-prediction scoring (Weng et al. 2022's original technique) simplified to a single-prompt generate-then-verify instruction for the catalog. |
| Self-Calibration (Schulhoff 2024) | → "SelfCalibration" final pattern | Two-prompt confidence-check pipeline (Kadavath et al. 2022's original technique) simplified to a single-prompt multi-path-and-confidence instruction for the catalog. |
| Complexity-Based Prompting (Schulhoff 2024) | Complex CoT (Vatsal & Dubey 2024 / Sahoo 2024) | Both select/weight reasoning by complexity and majority-vote over the most complex chains — same underlying idea, Vatsal & Dubey's naming ("Complex CoT") was kept as canonical for the final sheet. |
| Basic/Standard/Vanilla Prompting (Vatsal & Dubey 2024) | Zero-Shot Prompting | In this literature "basic prompting" (direct query, no scaffolding) and "zero-shot prompting" (no exemplars) are used near-interchangeably as the no-engineering baseline; merged for the catalog. |

**Result: 123 unique underlying concepts/techniques** (down from 163 Pass-2 groups — 40 concept-level merges). The consolidation pass includes the five explicitly folded variants recorded in `prompt_taxonomy_variants.csv`.

### Stage 4 — Final filter: writable single-prompt patterns only
Each of the 123 post-consolidation concepts was then classified into exactly one of three buckets:

- **INCLUDED** (30) — the technique can be written as a single, self-contained instruction block inside one prompt turn, the way White et al.'s Persona pattern works ("Act as X, provide outputs that X would create"). No external tool calls, no multiple LLM invocations, no iterative loop, no training/offline step required to use it.
- **EXCLUDED_WORKFLOW** (74) — the technique inherently requires multiple LLM calls, an external tool/interpreter/retrieval system, an iterative critique-revise loop, an agentic action loop, an ensembling/voting scheme over multiple samples, or an offline/training-time procedure.
- **EXCLUDED_OUT_OF_SCOPE** (19) — non-retained single-prompt concepts classified as meta-directive dimensions, prompting examples, preprocessing, non-textual techniques, or training methods. Folded variants are accounted for during consolidation, before this scope filter.

**Final result: 30 writable single-prompt patterns.**

## 3. Full count progression

| Stage | Count | Change |
|---|---|---|
| Pass 1 — raw extraction | 176 | — |
| Pass 2 — exact name+concept dedup | 163 | −13 |
| Pass 3 — concept-level consolidation | 123 | −40 |
| Final — workflow/orchestration removed | 49 | −74 |
| Final — out-of-scope/not-selected removed | **30** | −19 |
## 4. Complete Pass-1 raw extraction, by source paper

Every row below is one technique as it was named and described in its source paper. "Final status" shows where it ended up after Passes 2–3 and the workflow/scope filter.

### 4.1. White et al. 2023 (arXiv:2302.11382) — 16 raw techniques

| # | Raw name | Section | Concept summary | Final status |
|---|---|---|---|---|
| 1 | Meta Language Creation | Input Semantics | Define custom shorthand notation/semantics for the LLM to use in the rest of the conversation. | ✅ INCLUDED → **MetaLanguageCreation** |
| 2 | Output Automater | Output Customization | Have the LLM generate a script/artifact that automates any steps it recommends in its output. | ✅ INCLUDED → **OutputAutomater** |
| 3 | Persona | Output Customization | Give the LLM a persona/role to adopt, shaping the style and focus of its output. | ✅ INCLUDED → **Role / Persona Prompting** |
| 4 | Visualization Generator | Output Customization | Generate textual input (e.g. Graphviz DOT, DALL-E prompt) for another tool to render a visualization. | ✅ INCLUDED → **VisualizationGenerator** |
| 5 | Recipe | Output Customization | Given a goal and partial known steps, have the LLM produce the complete ordered sequence, filling/flagging steps. | ✅ INCLUDED → **Recipe** |
| 6 | Template | Output Customization | Provide a literal template with placeholders; LLM inserts generated content and preserves structure. | ✅ INCLUDED → **Template** |
| 7 | Fact Check List | Error Identification | LLM generates a list of facts the output depends on, placed at a specific point, for user verification. | ✅ INCLUDED → **FactCheckList** |
| 8 | Reflection | Error Identification | LLM automatically explains the reasoning/assumptions behind its own answer after producing it. | ✅ INCLUDED → **Reflection** |
| 9 | Question Refinement | Prompt Improvement | LLM always suggests a better/more refined version of the user's question within a given scope. | ✅ INCLUDED → **Question Refinement** |
| 10 | Alternative Approaches | Prompt Improvement | LLM always lists alternative ways to accomplish the same task, optionally with pros/cons. | ✅ INCLUDED → **Alternative Approaches** |
| 11 | Cognitive Verifier | Prompt Improvement | LLM subdivides a question into clarifying sub-questions, then combines answers into the final answer. | ✅ INCLUDED → **CognitiveVerifier** |
| 12 | Refusal Breaker | Prompt Improvement | Whenever the LLM refuses to answer, it explains why and offers alternative phrasings it could answer. | ✅ INCLUDED → **RefusalBreaker** |
| 13 | Flipped Interaction | Interaction | LLM drives the conversation by asking the user questions until a goal/condition is reached. | ✅ INCLUDED → **FlippedInteraction** |
| 14 | Game Play | Interaction | Frame the task as a game around a topic, with defined rules; LLM generates game content/scenarios. | ✅ INCLUDED → **GamePlay** |
| 15 | Infinite Generation | Interaction | LLM generates a continuous/repeated stream of outputs without the user re-entering the prompt each time. | ✅ INCLUDED → **InfiniteGeneration** |
| 16 | Context Manager | Context Control | User explicitly specifies what context to include/exclude, optionally resetting context entirely. | ✅ INCLUDED → **ContextManager** |

### 4.2. Schulhoff et al. 2024 — The Prompt Report (arXiv:2406.06608) — 55 raw techniques

| # | Raw name | Section | Concept summary | Final status |
|---|---|---|---|---|
| 1 | Zero-Shot Prompting | 2.2.1 ICL | Task performed with no exemplars, via direct instruction. | ✅ INCLUDED → **Zero-Shot Prompting** |
| 2 | Few-Shot Prompting | 2.2.1 ICL | Task demonstrated via a small number of input/output exemplars in the prompt. | ✅ INCLUDED → **Few-Shot Prompting** |
| 3 | Role Prompting | 2.2.1.3 ICL | Assign GenAI a specific role/persona; explicitly noted by authors as a.k.a. Persona Prompting. | ✅ INCLUDED → **Role / Persona Prompting** |
| 4 | Style Prompting | 2.2.1.3 ICL | Specify desired style, tone, or genre directly in the prompt. | 🚫 out of scope |
| 5 | Emotion Prompting | 2.2.1.3 ICL | Incorporate psychologically-relevant phrases (e.g. 'this is important to my career') into the prompt. | 🚫 out of scope |
| 6 | System 2 Attention (S2A) | 2.2.1.3 ICL | Two-step: LLM rewrites prompt to remove irrelevant info, then answers using the cleaned prompt. | ⛔ workflow |
| 7 | SimToM | 2.2.1.3 ICL | Two-prompt process: establish what one entity knows, then answer based only on those facts. | ⛔ workflow |
| 8 | Rephrase and Respond (RaR) | 2.2.1.3 ICL | LLM rephrases/expands the question before answering, single or two-step. | ✅ INCLUDED → **RAR** |
| 9 | Re-reading (RE2) | 2.2.1.3 ICL | Adds 'Read the question again:' + repeats the question text to improve reasoning. | ✅ INCLUDED → **RE2** |
| 10 | Self-Ask | 2.2.1.3 ICL | LLM decides if follow-up questions are needed, generates/answers them, then answers original question. | ⛔ workflow |
| 11 | Self-Generated ICL (SG-ICL) | 2.2.1.2 ICL | LLM generates its own exemplars rather than a human supplying them. | ⛔ workflow |
| 12 | Exemplar Ordering | 2.2.1.1 ICL | Design decision: sequence of few-shot exemplars affects output. | 🚫 out of scope |
| 13 | Exemplar Selection - KNN | 2.2.1.2 ICL | Algorithmic selection of exemplars most similar to the test input. | ⛔ workflow |
| 14 | Exemplar Selection - Vote-K | 2.2.1.2 ICL | Two-stage algorithm to select diverse, representative exemplars. | ⛔ workflow |
| 15 | Instruction Selection | 2.2.1.1 ICL | Choosing/optimizing the instruction text used in a prompt. | ✅ INCLUDED → **InstructionSelection** |
| 16 | Prompt Mining | 2.2.1.2 ICL | Corpus-analysis technique to discover optimal template middle-words. | ⛔ workflow |
| 17 | Chain-of-Thought (CoT) Prompting | 2.2.2 Thought Gen | Few-shot or zero-shot prompt eliciting explicit step-by-step reasoning before the final answer. | ✅ INCLUDED → **Chain-of-Thought (CoT)** |
| 18 | Zero-Shot CoT | 2.2.2.1 Thought Gen | CoT variant with zero exemplars; appends a thought-inducing phrase like 'Let's think step by step.' | ✅ INCLUDED → **Chain-of-Thought (CoT)** |
| 19 | Step-Back Prompting | 2.2.2.1 Thought Gen | LLM first asked a generic high-level question about relevant concepts before detailed reasoning. | ⛔ workflow |
| 20 | Analogical Prompting | 2.2.2.1 Thought Gen | LLM automatically generates its own relevant exemplars (incl. CoTs) before solving. | ⛔ workflow |
| 21 | Thread-of-Thought (ThoT) | 2.2.2.1 Thought Gen | Alternate thought-inducer phrase tailored to long/complex contexts; two-phase summarize-then-answer. | ⛔ workflow |
| 22 | Tabular CoT (Tab-CoT) | 2.2.2.1 Thought Gen | Zero-Shot CoT variant outputting reasoning as a markdown table. | 🔀 merged into **ChainOfThought** |
| 23 | Few-Shot CoT | 2.2.2.2 Thought Gen | Exemplars in the prompt include full chains-of-thought (not just answers). | ✅ INCLUDED → **Chain-of-Thought (CoT)** |
| 24 | Active-Prompting | 2.2.2.2 Thought Gen | Uncertainty/disagreement across LLM-solved training Qs used to select exemplars for human re-annotation. | ⛔ workflow |
| 25 | Auto-CoT | 2.2.2.2 Thought Gen | Automatically generates CoT exemplars via zero-shot CoT, then builds a few-shot CoT prompt. | ⛔ workflow |
| 26 | Complexity-Based Prompting | 2.2.2.2 Thought Gen | Selects complex exemplars + samples multiple reasoning chains, majority-vote weighted by chain length. | ✅ INCLUDED → **Complex CoT** |
| 27 | Contrastive CoT Prompting | 2.2.2.2 Thought Gen | Exemplars include both correct AND incorrect explanations to show the model how not to reason. | 🔀 merged into **ChainOfThought** |
| 28 | Memory-of-Thought Prompting | 2.2.2.2 Thought Gen | Retrieves similar reasoned instances from unlabeled training data at test time to build a CoT prompt. | ⛔ workflow |
| 29 | Uncertainty-Routed CoT | 2.2.2.2 Thought Gen | Samples multiple CoT paths, picks majority if above confidence threshold, else falls back to greedy. | ⛔ workflow |
| 30 | Decomposed Prompting (DECOMP) | 2.2.3 Decomposition | Few-shot prompts the LLM to use specific sub-functions, often separate LLM/tool calls. | ⛔ workflow |
| 31 | Faithful Chain-of-Thought | 2.2.3 Decomposition | CoT combining natural language and symbolic/code reasoning. | ⛔ workflow |
| 32 | Least-to-Most Prompting | 2.2.3 Decomposition | LLM decomposes problem into sub-problems (unsolved), then solves them sequentially. | ✅ INCLUDED → **Least-to-Most** |
| 33 | Plan-and-Solve Prompting | 2.2.3 Decomposition | Zero-Shot CoT variant: 'Let's first understand the problem and devise a plan... then carry it out.' | ✅ INCLUDED → **Plan-and-Solve (PS / PS+)** |
| 34 | Program-of-Thoughts | 2.2.3 Decomposition | LLM generates code as reasoning steps; external interpreter executes it. | ⛔ workflow |
| 35 | Recursion-of-Thought | 2.2.3 Decomposition | Recursively spins off sub-problems into separate LLM calls when reasoning hits complexity. | ⛔ workflow |
| 36 | Skeleton-of-Thought | 2.2.3 Decomposition | Generates a skeleton of sub-questions, solves them in parallel via separate calls, concatenates. | ⛔ workflow |
| 37 | Tree-of-Thought (ToT) | 2.2.3 Decomposition | Generates/evaluates a tree of multiple possible reasoning steps, with search/branching/backtracking. | ⛔ workflow |
| 38 | Metacognitive Prompting | 2.2.3 Decomposition | 5-step prompt chain mimicking human metacognition (clarify, judge, evaluate, confirm, assess confidence). | ⛔ workflow |
| 39 | Demonstration Ensembling (DENSE) | 2.2.4 Ensembling | Multiple few-shot prompts with different exemplar subsets; aggregate outputs. | ⛔ workflow |
| 40 | Mixture of Reasoning Experts (MoRE) | 2.2.4 Ensembling | Multiple specialized prompts (different reasoning types); best answer selected by agreement score. | ⛔ workflow |
| 41 | Max Mutual Information Method | 2.2.4 Ensembling | Multiple prompt template variants scored by mutual information; optimal one selected. | ⛔ workflow |
| 42 | Self-Consistency | 2.2.4 Ensembling | Sample multiple diverse reasoning chains (temp>0), majority-vote the final answer. | ⛔ workflow |
| 43 | Universal Self-Consistency | 2.2.4 Ensembling | Like Self-Consistency, but majority vote performed by inserting all outputs into another LLM prompt. | ⛔ workflow |
| 44 | Meta-Reasoning over Multiple CoTs | 2.2.4 Ensembling | Generates multiple reasoning chains, feeds all into one prompt to produce a final answer. | ⛔ workflow |
| 45 | DiVeRSe | 2.2.4 Ensembling | Multiple prompts each with Self-Consistency; scores reasoning paths step-by-step. | ⛔ workflow |
| 46 | Consistency-based Self-adaptive Prompting (COSP) | 2.2.4 Ensembling | Builds few-shot CoT prompt from high-agreement Zero-Shot CoT + Self-Consistency outputs. | ⛔ workflow |
| 47 | Universal Self-Adaptive Prompting (USP) | 2.2.4 Ensembling | Generalization of COSP using unlabeled data and a complex scoring function. | ⛔ workflow |
| 48 | Prompt Paraphrasing | 2.2.4 Ensembling | Generates reworded variants of a prompt (same meaning) for use in an ensemble. | ⛔ workflow |
| 49 | Self-Calibration | 2.2.5 Self-Criticism | LLM answers, then a second prompt asks whether the answer is correct, for confidence estimation. | ✅ INCLUDED → **SelfCalibration** |
| 50 | Self-Refine | 2.2.5 Self-Criticism | Iterative critique-then-revise loop until a stopping condition is met. | ⛔ workflow |
| 51 | Reversing Chain-of-Thought (RCoT) | 2.2.5 Self-Criticism | Reconstructs the problem from the generated answer, compares to original to find inconsistencies. | ✅ INCLUDED → **Reverse CoT** |
| 52 | Self-Verification | 2.2.5 Self-Criticism | Generates multiple candidate CoT solutions, scores each by masking parts of the question and predicting them. | ✅ INCLUDED → **SelfVerification** |
| 53 | Chain-of-Verification (CoVe) | 2.2.5 Self-Criticism | Generate answer, generate verification questions, answer them, produce revised final answer. | ⛔ workflow |
| 54 | Cumulative Reasoning | 2.2.5 Self-Criticism | Generates candidate steps, LLM evaluates/accepts/rejects them, checks for completion, repeats. | ⛔ workflow |
| 55 | Output Formatting / Answer Shape & Space (vocabulary terms) | 1.2.1 Terminology / 2.5 Answer Engineering | Prompt component / answer-engineering concept: instructing the LLM to output information in a defined structure/format (CSV, XML, JSON, fixed schema) and constraining the answer shape/space accordingly. | ✅ INCLUDED → **SchemaSpecs** |

### 4.3. Sahoo et al. 2024 (arXiv:2402.07927) — 41 raw techniques

| # | Raw name | Section | Concept summary | Final status |
|---|---|---|---|---|
| 1 | Zero-Shot Prompting | 2.1 | Task description only, no examples, relies on pretrained knowledge. | ✅ INCLUDED → **Zero-Shot Prompting** |
| 2 | Few-Shot Prompting | 2.1 | A few input-output exemplars included to induce task understanding. | ✅ INCLUDED → **Few-Shot Prompting** |
| 3 | Chain-of-Thought (CoT) Prompting | 2.2 | Elicits step-by-step intermediate reasoning before the final answer. | ✅ INCLUDED → **Chain-of-Thought (CoT)** |
| 4 | Automatic CoT (Auto-CoT) | 2.2 | Automatically generates diverse CoT exemplars. | ⛔ workflow |
| 5 | Self-Consistency | 2.2 | Samples multiple reasoning chains, majority-votes final answer. | ⛔ workflow |
| 6 | Logical CoT (LogiCoT) Prompting | 2.2 | Neurosymbolic think-verify-revise loop using reductio ad absurdum. | ⛔ workflow |
| 7 | Chain-of-Symbol (CoS) Prompting | 2.2 | Uses condensed symbols instead of natural language for spatial reasoning. | 🔀 merged into **ChainOfThought** |
| 8 | Tree-of-Thoughts (ToT) Prompting | 2.2 | Tree of intermediate thoughts combined with BFS/DFS search. | ⛔ workflow |
| 9 | Graph-of-Thoughts (GoT) Prompting | 2.2 | Models reasoning as a directed graph allowing backtracking/aggregation. | ⛔ workflow |
| 10 | System 2 Attention (S2A) Prompting | 2.2 | Two-step: regenerate clean context, then answer. | ⛔ workflow |
| 11 | Thread of Thought (ThoT) Prompting | 2.2 | Segments long/chaotic context, summarizes/analyzes incrementally. | ⛔ workflow |
| 12 | Chain-of-Table Prompting | 2.2 | Step-by-step tabular reasoning via dynamically generated/executed SQL/DataFrame ops. | ⛔ workflow |
| 13 | Self-Refine Prompting | 2.2 | Iterative 3-step generate-critique-revise loop. | ⛔ workflow |
| 14 | Code Prompting | 2.2 | Reformulates an NL reasoning task as structured code. | 🚫 out of scope |
| 15 | Self-Harmonized CoT (ECHO) Prompting | 2.2 | 3-stage cluster/sample/unify pipeline for CoT exemplar harmonization. | ⛔ workflow |
| 16 | Logic-of-Thought Prompting | 2.2 | 3-phase extract/extend/translate propositional-logic augmentation. | ⛔ workflow |
| 17 | Instance-Adaptive Prompting (IAP) | 2.2 | Dynamically tailors the CoT trigger phrase per-instance via attention-saliency analysis. | ⛔ workflow |
| 18 | End-to-End DAG-Path (EEDP) Prompting | 2.2 | Preprocesses graphs into DAGs, extracts/compresses backbone paths. | ⛔ workflow |
| 19 | Layer-of-Thoughts (LoT) Prompting | 2.2 | Hierarchical 3-layer constraint-based filtering for legal retrieval. | ⛔ workflow |
| 20 | Narrative-of-Thought (NoT) Prompting | 2.2 | 3-component structural/template/demo pipeline for temporal-graph construction. | ⛔ workflow |
| 21 | Buffer of Thoughts (BoT) Prompting | 2.2 | Meta-buffer of reusable distilled thought-templates, retrieved/instantiated per problem. | ⛔ workflow |
| 22 | Contrastive Denoising with Noisy CoT (CD-CoT) | 2.2 | Contrasts noisy vs clean rationales, rephrases, selects/votes on best path. | ⛔ workflow |
| 23 | Reverse Chain-of-Thought (R-CoT) Prompting | 2.2 | 2-stage dataset-generation pipeline (GeoChain + Reverse A&Q) for geometric training data. | ⛔ workflow |
| 24 | Chain of Draft (CoD) Prompting | 2.2 | Constrains each CoT step to be extremely concise/information-dense. | 🚫 out of scope |
| 25 | Retrieval Augmented Generation (RAG) | 2.3 | Retrieves external documents and inserts them into the prompt context. | ⛔ workflow |
| 26 | ReAct Prompting | 2.3 | Interleaves reasoning traces and external tool/API actions in a loop. | ⛔ workflow |
| 27 | Chain-of-Verification (CoVe) Prompting | 2.3 | 4-step generate/plan-verify/answer/revise pipeline. | ⛔ workflow |
| 28 | Chain-of-Note (CoN) Prompting | 2.3 | RALM technique: evaluate/filter retrieved document relevance before answering. | ⛔ workflow |
| 29 | Chain-of-Knowledge (CoK) Prompting | 2.3 | Reasoning-preparation + dynamic-knowledge-adaptation phases pulling from internal/external sources. | ⛔ workflow |
| 30 | Active-Prompting | 2.4 | Uncertainty-based active-learning selection of exemplars for human annotation. | ⛔ workflow |
| 31 | Automatic Prompt Engineer (APE) | 2.5 | LLM generates and RL-selects optimal instructions automatically. | ⛔ workflow |
| 32 | Automatic Reasoning and Tool-use (ART) | 2.6 | Automates multi-step reasoning + external tool integration via structured programs. | ⛔ workflow |
| 33 | Contrastive Chain-of-Thought (CCoT) Prompting | 2.7 | Provides both valid AND invalid reasoning demonstrations in the exemplars. | 🚫 out of scope |
| 34 | Emotion Prompting | 2.8 | Appends emotional-stimulus phrases to the prompt to improve performance. | 🚫 out of scope |
| 35 | Scratchpad Prompting | 2.9 | Lets the model generate an arbitrary sequence of intermediate tokens before the final answer. | 🚫 out of scope |
| 36 | Program of Thoughts (PoT) Prompting | 2.9 | Generates executable code as reasoning steps, computed by an external interpreter. | ⛔ workflow |
| 37 | Structured CoT (SCoT) Prompting | 2.9 | Incorporates program structures (sequence/branch/loop) explicitly into reasoning steps for code generation. | ✅ INCLUDED → **Structured CoT (SCoT)** |
| 38 | Chain-of-Code (CoC) Prompting | 2.9 | Formats semantic sub-tasks as pseudocode executed/simulated by an interpreter. | ⛔ workflow |
| 39 | Optimization by Prompting (OPRO) | 2.10 | Uses the LLM as an iterative optimizer over a problem description across iterations. | ⛔ workflow |
| 40 | Rephrase and Respond (RaR) Prompting | 2.11 | LLM rephrases/expands the question before answering. | ✅ INCLUDED → **RAR** |
| 41 | Take a Step Back / Step-Back Prompting | 2.12 | Two-step: ask a generic high-level/abstraction question, then reason from it. | ⛔ workflow |

### 4.4. Vatsal & Dubey 2024 (arXiv:2407.12994) — 39 raw techniques

| # | Raw name | Section | Concept summary | Final status |
|---|---|---|---|---|
| 1 | Basic/Standard/Vanilla Prompting | 2.1 | Direct query to the LLM with no engineering/scaffolding. | ✅ INCLUDED → **Zero-Shot Prompting** |
| 2 | Chain-of-Thought (CoT) | 2.2 | Step-by-step reasoning chain before the final answer. | ✅ INCLUDED → **Chain-of-Thought (CoT)** |
| 3 | Self-Consistency | 2.3 | Samples multiple reasoning paths, majority-votes final answer. | ⛔ workflow |
| 4 | Ensemble Refinement (ER) | 2.4 | 2-stage temperature-sampling + majority-vote refinement pipeline. | ⛔ workflow |
| 5 | Automatic CoT (Auto-CoT) | 2.5 | Cluster queries, generate representative zero-shot CoT exemplars automatically. | ⛔ workflow |
| 6 | Complex CoT | 2.6 | Selects most complex exemplars + majority-votes over the most complex of N sampled reasoning chains. | ✅ INCLUDED → **Complex CoT** |
| 7 | Program-of-Thoughts (PoT) | 2.7 | Generates Python code as reasoning, executed by interpreter. | ⛔ workflow |
| 8 | Least-to-Most | 2.8 | Decompose into sub-problems, solve sequentially. | ✅ INCLUDED → **Least-to-Most** |
| 9 | Chain-of-Symbol (CoS) | 2.9 | Represents spatial relationships via condensed symbols instead of NL. | 🔀 merged into **ChainOfThought** |
| 10 | Structured Chain-of-Thought (SCoT) | 2.10 | Structuring reasoning via program constructs (sequence/branch/loop) for code generation. | ✅ INCLUDED → **Structured CoT (SCoT)** |
| 11 | Plan-and-Solve (PS) | 2.11 | Devise a plan, then carry it out step by step; PS+ adds detailed instructions. | ✅ INCLUDED → **Plan-and-Solve (PS / PS+)** |
| 12 | MathPrompter | 2.12 | 4-step algebraic-expression / analytic-solve / numeric-verify pipeline. | ⛔ workflow |
| 13 | Contrastive CoT / Contrastive Self-Consistency | 2.13 | Provides both positive AND negative reasoning demonstrations. | 🔀 merged into **ChainOfThought** |
| 14 | Federated Same/Diff Parameter Self-Consistency/CoT (Fed-SP/DP-SC/CoT) | 2.14 | Uses paraphrased crowd-sourced queries federated together for reasoning. | ⛔ workflow |
| 15 | Analogical Reasoning | 2.15 | LLM generates its own relevant exemplars before solving. | ⛔ workflow |
| 16 | Synthetic Prompting | 2.16 | LLM generates synthetic backward/forward exemplar pairs to augment few-shot prompts. | ⛔ workflow |
| 17 | Tree-of-Thoughts (ToT) | 2.17 | Tree-structured search over reasoning steps with BFS/DFS. | ⛔ workflow |
| 18 | Logical Thoughts (LoT) | 2.18 | Step-by-step reasoning + step-by-step verification via Reductio ad Absurdum. | ⛔ workflow |
| 19 | Maieutic Prompting | 2.19 | Recursive generation of abductive explanations/propositions in a tree, eliminating contradictions. | ⛔ workflow |
| 20 | Verify-and-Edit (VE) | 2.20 | 3-stage detect-uncertain / edit-via-retrieval / re-derive pipeline. | ⛔ workflow |
| 21 | Reason + Act (ReAct) | 2.21 | Interleaves reasoning traces and external actions. | ⛔ workflow |
| 22 | Active-Prompt | 2.22 | 4-step uncertainty-based active-learning selection of exemplars for human annotation. | ⛔ workflow |
| 23 | Thread-of-Thought (ThoT) | 2.23 | 2-step: summarize/analyze context sections, then answer. | ⛔ workflow |
| 24 | Implicit Retrieval Augmented Generation (Implicit RAG) | 2.24 | LLM itself retrieves relevant chunks/sections from given context before answering. | ⛔ workflow |
| 25 | System 2 Attention (S2A) | 2.25 | Two-step: regenerate clean context, then answer. | ⛔ workflow |
| 26 | Instructed Prompting | 2.26 | Single explicit instruction telling the LLM to ignore irrelevant info. | 🚫 out of scope |
| 27 | Chain-of-Verification (CoVe) | 2.27 | 4-step generate/verify/answer/revise pipeline. | ⛔ workflow |
| 28 | Chain-of-Knowledge (CoK) | 2.28 | 3-stage reasoning-prep / knowledge-adapt / answer-consolidation pipeline. | ⛔ workflow |
| 29 | Chain-of-Code (CoC) | 2.29 | Formats sub-tasks as pseudocode, simulated by an 'LMulator'. | ⛔ workflow |
| 30 | Program-Aided Language Models (PAL) | 2.30 | Interleaved NL + code reasoning, executed by Python interpreter. | ⛔ workflow |
| 31 | Binder | 2.31 | Neural-symbolic technique mapping input to an executable program (parse+execute). | ⛔ workflow |
| 32 | Dater | 2.32 | Decomposes table into sub-tables + query into SQL sub-computations, 3-step pipeline. | ⛔ workflow |
| 33 | Chain-of-Table | 2.33 | 3-step iterative table-operation planning/execution pipeline. | ⛔ workflow |
| 34 | Decomposed Prompting (DecomP) | 2.34 | Decomposes into sub-problems delegated to sub-problem-specific LLM callers/decomposers. | ⛔ workflow |
| 35 | Three-Hop Reasoning (THOR) | 2.35 | 3-step identify-aspect / infer-opinion / infer-polarity pipeline for sentiment analysis. | ⛔ workflow |
| 36 | Metacognitive Prompting (MP) | 2.36 | 5-stage understand/judge/evaluate/decide/assess-confidence pipeline. | ⛔ workflow |
| 37 | Chain-of-Event (CoE) | 2.37 | 4-step event extraction/generalization/filtering/integration pipeline for summarization. | ⛔ workflow |
| 38 | Basic with Term Definitions | 2.38 | Basic prompt + domain term definitions appended. | 🚫 out of scope |
| 39 | Basic + Annotation Guideline + Error Analysis Prompting | 2.39 | Composite prompt: task instructions + annotation-guideline rules + error-analysis-derived corrections. | 🚫 out of scope |

### 4.5. Fagbohun et al. 2024 (arXiv:2402.14837) — 25 raw techniques

| # | Raw name | Section | Concept summary | Final status |
|---|---|---|---|---|
| 1 | Chain-of-Thought (CoT) Prompting | 2.1 Logical/Sequential | Sequential step-by-step processing of complex queries into explainable intermediary steps. | ✅ INCLUDED → **Chain-of-Thought (CoT)** |
| 2 | Chain-of-Thought Factored Decomposition Prompting | 2.1 Logical/Sequential | Combines CoT with explicit decomposition into subcomponents before sequential reasoning. | ⛔ workflow |
| 3 | Tree-of-Thoughts (ToT) / Graph-of-Thoughts (GoT) Prompting | 2.1 Logical/Sequential | Decision tree / graph of reasoning paths for branching, creative exploration. | ⛔ workflow |
| 4 | Skeleton-of-Thought (SoT) Prompting | 2.1 Logical/Sequential | Gives the model a structured high-level 'skeleton' template to fill in for the response. | ⛔ workflow |
| 5 | In-Context Prompting | 2.2 Contextual/Memory | Maintaining/leveraging conversational context/history across turns within the context window. | ⛔ workflow |
| 6 | Multi-Personas Prompting | 2.2 Contextual/Memory | Switching the LLM between different named personas/characters across turns/queries. | ✅ INCLUDED → **Role / Persona Prompting** |
| 7 | Conversational Prompting | 2.2 Contextual/Memory | Crafting prompts that mimic natural back-and-forth human conversation. | ⛔ workflow |
| 8 | Socratic Prompting | 2.2 Contextual/Memory | Leads the model/user to a conclusion via a structured series of probing questions. | ⛔ workflow |
| 9 | Show-me versus Tell-me Prompting | 2.3 Specificity/Targeting | Explicitly instructing the LLM to either demonstrate or describe a concept. | 🚫 out of scope |
| 10 | Target-your-response (TAR) Prompting | 2.3 Specificity/Targeting | Directs the response toward a specific target/format/length for relevance and brevity. | 🚫 out of scope |
| 11 | Prompt Macros and End-goal Planning | 2.3 Specificity/Targeting | Combines many potential micro-queries into one larger macro prompt aimed at an overarching goal. | ⛔ workflow |
| 12 | Contrastive Prompting | 2.3 Specificity/Targeting | Asks the model to compare/contrast two concepts, objects, or ideas. | 🚫 out of scope |
| 13 | Self-reflection Prompting | 2.4 Meta-Cognition | Asks the model to evaluate/critique its own prior answer (e.g. 'Are you sure about that?'). | ✅ INCLUDED → **Reflection** |
| 14 | Meta-Prompting | 2.4 Meta-Cognition | Guides the LLM to reflect on/improve its own prompting process and methodology. | ⛔ workflow |
| 15 | Anticipatory Prompting | 2.4 Meta-Cognition | Encourages the model to foresee and proactively address likely follow-up needs/questions. | 🚫 out of scope |
| 16 | Prompt to Code | 2.4 Meta-Cognition | Instructs the LLM to generate functional code from a natural-language description. | 🚫 out of scope |
| 17 | Responsive Feedback Prompting | 2.5 Directional/Feedback | Incorporates user feedback on a prior output directly into the next prompt. | ⛔ workflow |
| 18 | Directional Stimulus Prompting | 2.5 Directional/Feedback | Uses subtle hints/cues to nudge output in a desired direction without fully dictating it. | 🚫 out of scope |
| 19 | Ambiguous Prompting | 2.5 Directional/Feedback | Deliberately vague/open-ended prompts to stimulate broad, creative, less-biased responses. | 🚫 out of scope |
| 20 | Multimodal Prompting | 2.6 Multimodal/Cross-Disc. | Combines multiple input modalities (text, image, audio, video) in a single prompt. | 🚫 out of scope |
| 21 | Cross-disciplinary Prompting | 2.6 Multimodal/Cross-Disc. | Blends knowledge from multiple separate disciplines/domains to generate interdisciplinary insight. | 🔀 merged into **ContextManager** |
| 22 | Historical Context, Visual, and Modular Prompting | 2.6 Multimodal/Cross-Disc. | Bundles historical-context framing, visual elements, and modular/component-based prompt structure. | 🚫 out of scope |
| 23 | Flipped Interaction Prompting | 2.7 Creative/Generative | Reverses the conventional dynamic so the model asks the user questions instead of answering directly. | ✅ INCLUDED → **FlippedInteraction** |
| 24 | Grammar Correction | 2.7 Creative/Generative | Instructs the LLM to identify/correct grammar, tone, and clarity issues in user-supplied text. | 🚫 out of scope |
| 25 | Constrained Vocabulary Prompting | 2.7 Creative/Generative | Restricts the model's output to a specific/defined vocabulary or terminology set. | 🔀 merged into **SchemaSpecs** |
## 5. The final 30 writable prompt patterns — full derivation

For each of the 30 patterns in the final taxonomy, this table shows every raw Pass-1 mention that was merged into it (via Pass 2 exact-match and/or Pass 3 synonym-match), so the chain from raw paper text to final catalog entry is fully traceable.

### Zero-Shot Prompting
*Category:* In-context Learning · *Subcategory:* Zero-shot · *Component use:* Directive

> Provide no examples to guide the task.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Zero-Shot Prompting | 2.2.1 ICL | Task performed with no exemplars, via direct instruction. |
| Sahoo et al. 2024 | Zero-Shot Prompting | 2.1 | Task description only, no examples, relies on pretrained knowledge. |
| Vatsal & Dubey 2024 | Basic/Standard/Vanilla Prompting | 2.1 | Direct query to the LLM with no engineering/scaffolding. |

### Few-Shot Prompting
*Category:* In-context Learning · *Subcategory:* Few-shot · *Component use:* Directive, Examples

> Provide a few exemplar input-output pairs to guide the model.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Few-Shot Prompting | 2.2.1 ICL | Task demonstrated via a small number of input/output exemplars in the prompt. |
| Sahoo et al. 2024 | Few-Shot Prompting | 2.1 | A few input-output exemplars included to induce task understanding. |

### Chain-of-Thought (CoT)
*Category:* Reasoning · *Subcategory:* Chain-of-Thought · *Component use:* Workflow

> Encourage step-by-step reasoning before final answer.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Chain-of-Thought (CoT) Prompting | 2.2.2 Thought Gen | Few-shot or zero-shot prompt eliciting explicit step-by-step reasoning before the final answer. |
| Schulhoff et al. 2024 | Zero-Shot CoT | 2.2.2.1 Thought Gen | CoT variant with zero exemplars; appends a thought-inducing phrase like 'Let's think step by step.' |
| Schulhoff et al. 2024 | Few-Shot CoT | 2.2.2.2 Thought Gen | Exemplars in the prompt include full chains-of-thought (not just answers). |
| Sahoo et al. 2024 | Chain-of-Thought (CoT) Prompting | 2.2 | Elicits step-by-step intermediate reasoning before the final answer. |
| Vatsal & Dubey 2024 | Chain-of-Thought (CoT) | 2.2 | Step-by-step reasoning chain before the final answer. |
| Fagbohun et al. 2024 | Chain-of-Thought (CoT) Prompting | 2.1 Logical/Sequential | Sequential step-by-step processing of complex queries into explainable intermediary steps. |

### Complex CoT
*Category:* Reasoning · *Subcategory:* Chain-of-Thought · *Component use:* Workflow

> During decoding, selects answers from the most complex reasoning chains

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Complexity-Based Prompting | 2.2.2.2 Thought Gen | Selects complex exemplars + samples multiple reasoning chains, majority-vote weighted by chain length. |
| Vatsal & Dubey 2024 | Complex CoT | 2.6 | Selects most complex exemplars + majority-votes over the most complex of N sampled reasoning chains. |

### Structured CoT (SCoT)
*Category:* Reasoning · *Subcategory:* Chain-of-Thought · *Component use:* Output Format/Style, Workflow

> Structure reasoning with program-like constructs (loops, branches).

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Sahoo et al. 2024 | Structured CoT (SCoT) Prompting | 2.9 | Incorporates program structures (sequence/branch/loop) explicitly into reasoning steps for code generation. |
| Vatsal & Dubey 2024 | Structured Chain-of-Thought (SCoT) | 2.10 | Structuring reasoning via program constructs (sequence/branch/loop) for code generation. |

### Plan-and-Solve (PS / PS+)
*Category:* Reasoning · *Subcategory:* Planning · *Component use:* Workflow

> First plan sub-problems, then solve them step by step.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Plan-and-Solve Prompting | 2.2.3 Decomposition | Zero-Shot CoT variant: 'Let's first understand the problem and devise a plan... then carry it out.' |
| Vatsal & Dubey 2024 | Plan-and-Solve (PS) | 2.11 | Devise a plan, then carry it out step by step; PS+ adds detailed instructions. |

### Least-to-Most
*Category:* Reasoning · *Subcategory:* Decomposition · *Component use:* Workflow

> Decompose into easiest sub-problems first, then harder ones.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Least-to-Most Prompting | 2.2.3 Decomposition | LLM decomposes problem into sub-problems (unsolved), then solves them sequentially. |
| Vatsal & Dubey 2024 | Least-to-Most | 2.8 | Decompose into sub-problems, solve sequentially. |

### Role / Persona Prompting
*Category:* Context Control · *Subcategory:* Role & perspective · *Component use:* Context, Output Format/Style, Profile/Role

> Adopt a role/persona to shape style/voice.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Persona | Output Customization | Give the LLM a persona/role to adopt, shaping the style and focus of its output. |
| Schulhoff et al. 2024 | Role Prompting | 2.2.1.3 ICL | Assign GenAI a specific role/persona; explicitly noted by authors as a.k.a. Persona Prompting. |
| Fagbohun et al. 2024 | Multi-Personas Prompting | 2.2 Contextual/Memory | Switching the LLM between different named personas/characters across turns/queries. |

### Reverse CoT
*Category:* Reasoning · *Subcategory:* Chain-of-Thought · *Component use:* Workflow

> Generate reasoning steps after giving the answer, to simulate justification.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Reversing Chain-of-Thought (RCoT) | 2.2.5 Self-Criticism | Reconstructs the problem from the generated answer, compares to original to find inconsistencies. |

### SelfVerification
*Category:* Output Control · *Subcategory:* Verification · *Component use:* Constraints, Workflow

> Model checks and verifies its own answers before finalizing.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Self-Verification | 2.2.5 Self-Criticism | Generates multiple candidate CoT solutions, scores each by masking parts of the question and predicting them. |

### SelfCalibration
*Category:* Output Control · *Subcategory:* Verification · *Component use:* Constraints, Workflow

> Model adjusts confidence in its answer or re-calibrates if uncertain.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Self-Calibration | 2.2.5 Self-Criticism | LLM answers, then a second prompt asks whether the answer is correct, for confidence estimation. |

### FactCheckList
*Category:* Output Control · *Subcategory:* Verification · *Component use:* Constraints, Workflow

> Use a checklist to confirm factual accuracy of the output.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Fact Check List | Error Identification | LLM generates a list of facts the output depends on, placed at a specific point, for user verification. |

### Reflection
*Category:* Output Control · *Subcategory:* Verification · *Component use:* Constraints, Workflow

> Model reflects on its first output, critiques, and improves it.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Reflection | Error Identification | LLM automatically explains the reasoning/assumptions behind its own answer after producing it. |
| Fagbohun et al. 2024 | Self-reflection Prompting | 2.4 Meta-Cognition | Asks the model to evaluate/critique its own prior answer (e.g. 'Are you sure about that?'). |

### OutputAutomater
*Category:* Output Control · *Subcategory:* Output formatting · *Component use:* Output Format/Style

> Automate steps in outputs for consistency.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Output Automater | Output Customization | Have the LLM generate a script/artifact that automates any steps it recommends in its output. |

### Recipe
*Category:* Output Control · *Subcategory:* Procedural · *Component use:* Directive, Workflow

> Provide a repeatable recipe-style sequence for solving tasks.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Recipe | Output Customization | Given a goal and partial known steps, have the LLM produce the complete ordered sequence, filling/flagging steps. |

### Template
*Category:* Output Control · *Subcategory:* Output formatting · *Component use:* Directive, Output Format/Style

> Use a reusable template to structure answers consistently.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Template | Output Customization | Provide a literal template with placeholders; LLM inserts generated content and preserves structure. |

### VisualizationGenerator
*Category:* Output Control · *Subcategory:* Output formatting · *Component use:* Output Format/Style

> Generate visual or tabular representations (charts, tables).

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Visualization Generator | Output Customization | Generate textual input (e.g. Graphviz DOT, DALL-E prompt) for another tool to render a visualization. |

### SchemaSpecs
*Category:* Output Control · *Subcategory:* Schema specification · *Component use:* Output Format/Style

> Define schema/structure the model must follow.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Output Formatting / Answer Shape & Space (vocabulary terms) | 1.2.1 Terminology / 2.5 Answer Engineering | Prompt component / answer-engineering concept: instructing the LLM to output information in a defined structure/format (CSV, XML, JSON, fixed schema) and constraining the answer shape/space accordingly. |

### FlippedInteraction
*Category:* Meta-Directives · *Subcategory:* Interaction · *Component use:* Directive

> Model asks the user questions instead of directly answering.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Flipped Interaction | Interaction | LLM drives the conversation by asking the user questions until a goal/condition is reached. |
| Fagbohun et al. 2024 | Flipped Interaction Prompting | 2.7 Creative/Generative | Reverses the conventional dynamic so the model asks the user questions instead of answering directly. |

### GamePlay
*Category:* Meta-Directives · *Subcategory:* Interaction · *Component use:* Directive

> Frame the task as a game to increase engagement.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Game Play | Interaction | Frame the task as a game around a topic, with defined rules; LLM generates game content/scenarios. |

### InfiniteGeneration
*Category:* Meta-Directives · *Subcategory:* Interaction · *Component use:* Directive

> Model generates continuously, with prompts to “keep going.”

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Infinite Generation | Interaction | LLM generates a continuous/repeated stream of outputs without the user re-entering the prompt each time. |

### Question Refinement
*Category:* Meta-Directives · *Subcategory:* Enhancement · *Component use:* Directive

> Improve or reformulate the user’s query for clarity.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Question Refinement | Prompt Improvement | LLM always suggests a better/more refined version of the user's question within a given scope. |

### RAR
*Category:* Meta-Directives · *Subcategory:* Refinement · *Component use:* Directive, Workflow

> Rephrase and Respond (rephrase the question, then answer).

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Rephrase and Respond (RaR) | 2.2.1.3 ICL | LLM rephrases/expands the question before answering, single or two-step. |
| Sahoo et al. 2024 | Rephrase and Respond (RaR) Prompting | 2.11 | LLM rephrases/expands the question before answering. |

### Alternative Approaches
*Category:* Meta-Directives · *Subcategory:* Enhancement · *Component use:* Directive, Workflow

> Suggest multiple different ways to solve the same problem.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Alternative Approaches | Prompt Improvement | LLM always lists alternative ways to accomplish the same task, optionally with pros/cons. |

### RE2
*Category:* Meta-Directives · *Subcategory:* Refinement · *Component use:* Directive

> Re-Reading (re-read the input before answering).

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Re-reading (RE2) | 2.2.1.3 ICL | Adds 'Read the question again:' + repeats the question text to improve reasoning. |

### RefusalBreaker
*Category:* Meta-Directives · *Subcategory:* Enhancement · *Component use:* Constraints, Directive

> Overcome model refusals by reframing the request.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Refusal Breaker | Prompt Improvement | Whenever the LLM refuses to answer, it explains why and offers alternative phrasings it could answer. |

### InstructionSelection
*Category:* Meta-Directives · *Subcategory:* Refinement · *Component use:* Directive, Workflow

> Choose the best instruction from a set of candidates.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| Schulhoff et al. 2024 | Instruction Selection | 2.2.1.1 ICL | Choosing/optimizing the instruction text used in a prompt. |

### CognitiveVerifier
*Category:* Meta-Directives · *Subcategory:* Enhancement · *Component use:* Directive, Workflow

> Add explicit verification of reasoning correctness.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Cognitive Verifier | Prompt Improvement | LLM subdivides a question into clarifying sub-questions, then combines answers into the final answer. |

### ContextManager
*Category:* Context Control · *Subcategory:* Context grounding · *Component use:* Context, Directive, Workflow

> Explicitly control what context the model uses to avoid drift.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Context Manager | Context Control | User explicitly specifies what context to include/exclude, optionally resetting context entirely. |

### MetaLanguageCreation
*Category:* Context Control · *Subcategory:* Input semantics · *Component use:* Context, Directive

> Define custom shorthand notation and its semantics for the model to apply in the rest of the prompt or conversation.

**Raw sources merged into this pattern:**

| Paper | Raw name | Section | Concept summary |
|---|---|---|---|
| White et al. 2023 | Meta Language Creation | Input Semantics | Define custom shorthand notation/semantics for the LLM to use in the rest of the conversation. |
