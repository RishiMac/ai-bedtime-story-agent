# Hippocratic AI Bedtime Story Generator

This project implements a lightweight agent-based system that generates high-quality bedtime stories for children ages 5 to 10 using structured prompting, safety validation, and an LLM-based evaluation loop.

The system transforms a simple user request into a safe, engaging, and developmentally appropriate story by combining generation, evaluation, selection, and optional refinement.

---

## Overview

The goal of this system is not just to generate a story, but to ensure **quality, safety, and consistency** through a multi-step pipeline.

Key features:
- Safety pre-check to ensure child-appropriate inputs  
- Structured prompt design for controlled story generation  
- Multi-candidate generation with best-of selection  
- LLM-based judge to evaluate output quality  
- Automatic revision loop if quality thresholds are not met  
- Optional user-driven refinement for iterative improvements  

---

## System Architecture

    User
     |
     v
    Safety Pre-Check
     |
     v
    Story Request Analyzer
     |
     v
    Tailored Story Prompt Builder
     |
     v
    Storyteller LLM (3 candidates)
     |
     v
    LLM Judge (evaluate each)
     |
     v
    Best Candidate Selection
     |
     v
    Revision Step (if needed)
     |
     v
    Final Bedtime Story
     |
     v
    Optional User Refinement Loop

---

## How It Works

### 1. Safety Pre-Check
The system first evaluates whether the user input is appropriate for children ages 5 to 10.

It classifies the request as:
- safe  
- needs_softening  
- unsafe  

If necessary, the request is rewritten into a safe, child-friendly version before generation.

---

### 2. Request Analysis
The system extracts structured attributes from the request:
- theme  
- characters  
- setting  
- tone  
- lesson  
- safety considerations  

This improves generation quality and consistency.

---

### 3. Multi-Candidate Story Generation
Instead of generating a single story, the system generates **three distinct candidate stories** using controlled prompting.

Each candidate:
- follows the same structure  
- varies in wording, imagery, and creative details  

---

### 4. LLM Judge Evaluation
Each candidate story is evaluated using a separate LLM across:

- age appropriateness  
- bedtime tone  
- creativity  
- clarity  
- request alignment  
- safety  

The judge returns:
- numerical scores  
- pass/fail decision  
- feedback  

---

### 5. Best Candidate Selection
The system selects the **highest-scoring story** from the candidate pool.

This mirrors real-world AI systems that generate multiple outputs and choose the best one based on evaluation.

---

### 6. Revision Loop
If the selected story does not meet quality thresholds:
- the system revises the story using judge feedback  
- re-evaluates the improved version  

---

### 7. User Refinement (Optional)
After the final story is generated, the user can request changes such as:
- "make it shorter"  
- "make it funnier"  
- "make it cozier"  

This demonstrates a simple human-in-the-loop agent interaction.

---

## Prompting Strategy

The system uses three distinct prompt roles:

### Analyzer Prompt
Transforms unstructured input into structured story attributes.

### Storyteller Prompt
Guides generation with:
- explicit structure  
- safety constraints  
- creativity enhancements  

### Judge Prompt
Acts as an evaluator that enforces:
- quality standards  
- safety guarantees  
- bedtime appropriateness  

This separation mirrors real-world agent architectures where generation and evaluation are decoupled.

---

## Example Run

Input:
A calm bedtime story about a young girl who travels to the moon and meets a gentle moon rabbit who teaches her about kindness

System Behavior:
- Ran a safety pre-check and marked the request as safe  
- Generated 3 candidate stories  
- Evaluated each candidate using an LLM judge  
- Selected the highest-scoring story (9.8/10)  
- Supported user refinement request:  
  "Make it shorter, cozier, and a little funnier"  

---

## Setup

### 1. Install dependencies

pip install -r requirements.txt

### 2. Set your API key

Create a `.env` file:

OPENAI_API_KEY=your_key_here

### 3. Run the program

python main.py

---

## Design Decisions

- Added a safety pre-check to enforce child-appropriate inputs  
- Used multi-candidate generation to improve output quality  
- Used LLM-as-a-judge to evaluate and select the best story  
- Kept model fixed to gpt-3.5-turbo per assignment constraints  
- Used structured prompting to reduce randomness  
- Included optional refinement loop to simulate interactive agents  

---

## Future Improvements

If given more time, I would:

- Generate more candidates and use ranking-based selection strategies  
- Add stronger adversarial safety testing  
- Introduce memory for personalization across sessions  
- Build a simple UI for parents and children  
- Add evaluation logs for observability and debugging  

---

## Notes

- API keys are never stored in the repository  
- `.env` is excluded via `.gitignore`  
- System is designed to be simple, extensible, and production-aligned  