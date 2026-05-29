---
source: arXiv cs.AI (latest)
source_slug: arxiv_cs_ai
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27703
title: Hierarchical Prompt-Domain Control and Learning for Resource-Constrained Agentic Language Models
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Artificial Intelligence arXiv:2605.27703 (cs) [Submitted on 26 May 2026] Title:

Hierarchical Prompt-Domain Control and Learning for Resource-Constrained Agentic Language Models

Authors: Joan Vendrell Gallart , Russell Bent , Michael Grosskopf

View a PDF of the paper titled Hierarchical Prompt-Domain Control and Learning for Resource-Constrained Agentic Language Models, by Joan Vendrell Gallart and 1 other authors

View PDF Abstract:

Large Language Models are increasingly deployed inside agentic systems, where they must follow structured protocols, adapt to evolving states, and operate under memory, latency, and cost constraints. In such regimes, prompt extension is unreliable: growing contexts can push compact models outside their effective prompt domain, while deployment-time fine-tuning remains limited by scarce data and compute. We propose a hierarchical control-and-learning framework in which a compact model is first distilled to learn the required output schema, then supervised online by an oracle-controller loop. The controller monitors protocol validity and semantic performance, projects accumulated histories into a feasible prompt domain, and triggers lightweight oracle-supervised fine-tuning under drift. This separates schema learning for communication compatibility from semantic adaptation for task-level correction. We formalize prompt-domain feasibility and attention-induced saturation, motivating control of the effective prompt state rather than reliance on nominal context length. Using Multi-Fidelity Bayesian Optimization as a controlled sequential testbed, we characterize a core deployment failure mode and show improved reliability and cost-efficiency over non-hierarchical, distillation-only, and non-distilled baselines.

Subjects: Artificial Intelligence (cs.AI) Cite as: arXiv:2605.27703 [cs.AI] (or arXiv:2605.27703v1 [cs.AI] for this version) https://doi.org/10.48550/arXiv.2605.27703 Focus to learn more arXiv-issued DOI via DataCite (pending registration) Submission history From: Joan Vendrell Gallart [ view email ] [v1] Tue, 26 May 2026 21:23:30 UTC (13,639 KB) Full-text links: Access Paper:

View a PDF of the paper titled Hierarchical Prompt-Domain Control and Learning for Resource-Constrained Agentic Language Models, by Joan Vendrell Gallart and 1 other authors

View PDF TeX Source view license Current browse context: cs.AI < prev | next > new | recent | 2026-05 Change to browse by: cs References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )