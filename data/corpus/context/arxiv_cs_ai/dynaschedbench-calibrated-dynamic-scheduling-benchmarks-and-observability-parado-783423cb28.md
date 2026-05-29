---
source: arXiv cs.AI (latest)
source_slug: arxiv_cs_ai
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27566
title: DynaSchedBench: Calibrated Dynamic Scheduling Benchmarks and Observability Paradox in LLM-based Scheduling Agents
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Artificial Intelligence arXiv:2605.27566 (cs) [Submitted on 26 May 2026] Title:

DynaSchedBench: Calibrated Dynamic Scheduling Benchmarks and Observability Paradox in LLM-based Scheduling Agents

Authors: Shijie Cao , Yuan Yuan , Jing Liu

View a PDF of the paper titled DynaSchedBench: Calibrated Dynamic Scheduling Benchmarks and Observability Paradox in LLM-based Scheduling Agents, by Shijie Cao and 2 other authors

View PDF HTML (experimental) Abstract:

Progress in neural combinatorial optimization for Dynamic Flexible Job Shop Scheduling Problem (DFJSP) is currently hindered by a methodological tension: static benchmarks encourage benchmark overfitting, while uncalibrated generators obscure algorithmic capability with stochastic noise. To resolve this, we introduce \textbf{DynaSchedBench}, a diagnostic framework for DFJSP that rigorously controls the instance-generation process. Instead of relying on parameter sampling, our approach utilizes Sequential Event-Space Calibrator (SESC) that computes a novel Schedule Stress Index (SSI) to stratify instances by difficulty. We demonstrate that SESC is substantially more computationally efficient than evolutionary baselines while converging reliably to the target metrics. The framework integrates modular components for instance generation, snapshot-based simulation, agents, evaluation, and visualization, thereby enabling rigorous testing of reactive and lookahead-based policies. Leveraging this calibrated environment, we identify key limitations of LLM-based scheduling agents. Specifically, in step-wise online decision-making for dynamic scheduling, we identify an ``Observability Paradox'': providing agents with oracle access to full structural information can degrade policy performance, underperforming concise information. Furthermore, despite substantial token overhead, tool-augmented and refinement strategies fail to reliably improve performance, and most LLM agents fail to consistently surpass strong dispatching baselines-behaving more like robust heuristic approximators than superior optimizers.

Subjects: Artificial Intelligence (cs.AI) Cite as: arXiv:2605.27566 [cs.AI] (or arXiv:2605.27566v1 [cs.AI] for this version) https://doi.org/10.48550/arXiv.2605.27566 Focus to learn more arXiv-issued DOI via DataCite (pending registration) Submission history From: Shijie Cao [ view email ] [v1] Tue, 26 May 2026 18:36:54 UTC (730 KB) Full-text links: Access Paper:

View a PDF of the paper titled DynaSchedBench: Calibrated Dynamic Scheduling Benchmarks and Observability Paradox in LLM-based Scheduling Agents, by Shijie Cao and 2 other authors

View PDF HTML (experimental) TeX Source view license Current browse context: cs.AI < prev | next > new | recent | 2026-05 Change to browse by: cs References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )