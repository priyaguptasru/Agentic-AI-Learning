# Module-5 — Production-Style RAG Application

## Overview

Module-5 extends the document retrieval capabilities developed in Module-4 into a complete **Retrieval-Augmented Generation (RAG)** application.

The main objective is to build a RAG pipeline that can:

- Understand the user's query
- Detect the user's intent
- Handle greetings separately
- Maintain conversation context
- Detect follow-up questions
- Use semantic caching
- Generate context-aware search queries
- Retrieve relevant documents using Hybrid Search
- Validate retrieval confidence
- Build a structured prompt
- Generate answers using an LLM
- Store conversation history
- Store responses in semantic cache
- Return the final answer with source information

---

# Architecture

```text
                         User Query
                              |
                              v
                      Intent Detection
                              |
                              v
                       Greeting Check
                              |
                              v
                       Semantic Cache
                              |
                    +---------+---------+
                    |                   |
                  Found              Not Found
                    |                   |
                    v                   v
              Cached Answer     Conversation Memory
                                        |
                                        v
                              Context-Aware Query
                                        |
                                        v
                                  Hybrid Search
                                        |
                         +--------------+--------------+
                         |                             |
                         v                             v
                  Semantic Search               Keyword Search
                         |                             |
                         +--------------+--------------+
                                        |
                                        v
                                Merge / Ranking
                                        |
                                        v
                              Retrieval Validation
                                        |
                                        v
                                Prompt Builder
                                        |
                                        v
                                      LLM
                                        |
                                        v
                                  Final Answer
                                        |
                         +--------------+--------------+
                         |                             |
                         v                             v
                 Conversation Memory          Semantic Cache
```
