---
source: arXiv cs.AI (latest)
source_slug: arxiv_cs_ai
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27570
title: LaneRoPE: Positional Encoding for Collaborative Parallel Reasoning and Generation
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Artificial Intelligence arXiv:2605.27570 (cs) [Submitted on 26 May 2026] Title:

LaneRoPE: Positional Encoding for Collaborative Parallel Reasoning and Generation

Authors: Gabriele Cesa , Thomas Hehn , Aleix Torres-Camps , Àlex Batlle Casellas , Jordi Ros-Giralt , Arash Behboodi , Tribhuvanesh Orekondy

View a PDF of the paper titled LaneRoPE: Positional Encoding for Collaborative Parallel Reasoning and Generation, by Gabriele Cesa and 5 other authors

View PDF HTML (experimental) Abstract:

Parallel LLM test-time scaling techniques (e.g., best-of-$N$) require drawing $N>1$ sequences conditioned on the same input prompt. These methods boost accuracy while exploiting the computational efficiency of batching $N$ generations. However, each sequence in the batch is traditionally generated independently and hence does not reuse intermediate generations, computations, or observations from other sequences. In this paper, we propose LaneRoPE to enable coordination and collaboration among $N>1$ sequences at generation time. LaneRoPE involves two key ideas: (a) an inter-sequence attention mask to make sampling of sequences dependent on one another; and (b) a RoPE extension that injects positional information that captures relative positions between tokens, both within and outside a particular sequence. We evaluate our approach on mathematical reasoning tasks and find promising results: LaneRoPE enables collaboration among sequences, yielding additional accuracy gains under limited generated sequence length. Importantly, since LaneRoPE enables coordination with minimal changes to the underlying LLM architecture and introduces a negligible overhead at inference time, it is appealing to rapidly incorporate parallel reasoning into existing LLM inference pipelines.

Subjects: Artificial Intelligence (cs.AI) Cite as: arXiv:2605.27570 [cs.AI] (or arXiv:2605.27570v1 [cs.AI] for this version) https://doi.org/10.48550/arXiv.2605.27570 Focus to learn more arXiv-issued DOI via DataCite (pending registration) Submission history From: Gabriele Cesa [ view email ] [v1] Tue, 26 May 2026 18:43:15 UTC (631 KB) Full-text links: Access Paper:

View a PDF of the paper titled LaneRoPE: Positional Encoding for Collaborative Parallel Reasoning and Generation, by Gabriele Cesa and 5 other authors

View PDF HTML (experimental) TeX Source view license Current browse context: cs.AI < prev | next > new | recent | 2026-05 Change to browse by: cs References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )