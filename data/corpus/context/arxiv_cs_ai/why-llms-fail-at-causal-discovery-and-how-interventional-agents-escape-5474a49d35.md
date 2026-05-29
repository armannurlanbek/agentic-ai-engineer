---
source: arXiv cs.AI (latest)
source_slug: arxiv_cs_ai
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27567
title: Why LLMs Fail at Causal Discovery and How Interventional Agents Escape
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Artificial Intelligence arXiv:2605.27567 (cs) [Submitted on 26 May 2026] Title: Why LLMs Fail at Causal Discovery and How Interventional Agents Escape Authors: Amartya Roy , Sonali Parbhoo

View a PDF of the paper titled Why LLMs Fail at Causal Discovery and How Interventional Agents Escape, by Amartya Roy and 1 other authors

View PDF HTML (experimental) Abstract:

Causal discovery is a cornerstone of scientific reasoning, yet whether large language models can perform it reliably remains an open question. Recent benchmarks show that even fine-tuned models plateau on simple causal graphs and degrade as complexity grows, but why they fail has not been established. We prove the failure is fundamental: supervised fine-tuning, direct preference optimization, and in-context learning all produce predictors that cannot distinguish between causal graphs generating similar observational data, and any attempt to do so requires the model's internal representations to grow unboundedly, violating the very conditions under which these methods work. We formalize this as a kernel obstruction theorem, establishing that the limitation is intrinsic to the learning paradigm, \emph{not any particular model or dataset}. We propose Agentic Causal Bayesian Optimization (A-CBO), wherein a frozen language model serves as an interventional oracle answering targeted queries about intervention effects, while an external Bayesian loop concentrates beliefs over candidate graphs in logarithmically many rounds. Because the decision operates outside the space where the obstruction applies, A-CBO provably converges while the underlying model remains unchanged. On Corr2Cause, A-CBO matches fine-tuned baselines without any training. On Extended Corr2Cause, a new benchmark scaling to 24 variables with 18K test samples, A-CBO significantly outperforms both fine-tuning and preference optimization, with the advantage growing

Comments: 9 pages, 3 figures Subjects: Artificial Intelligence (cs.AI) ; Computation and Language (cs.CL) Cite as: arXiv:2605.27567 [cs.AI] (or arXiv:2605.27567v1 [cs.AI] for this version) https://doi.org/10.48550/arXiv.2605.27567 Focus to learn more arXiv-issued DOI via DataCite (pending registration) Submission history From: Amartya Roy [ view email ] [v1] Tue, 26 May 2026 18:37:03 UTC (191 KB) Full-text links: Access Paper:

View a PDF of the paper titled Why LLMs Fail at Causal Discovery and How Interventional Agents Escape, by Amartya Roy and 1 other authors

View PDF HTML (experimental) TeX Source view license Current browse context: cs.AI < prev | next > new | recent | 2026-05 Change to browse by: cs cs.CL References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )