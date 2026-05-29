---
source: arXiv cs.AI (latest)
source_slug: arxiv_cs_ai
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27712
title: Prefix-Safe Bayesian Belief Tracking for LLM Reasoning Reliability:Separating Calibration from Ranking
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Artificial Intelligence arXiv:2605.27712 (cs) [Submitted on 26 May 2026] Title:

Prefix-Safe Bayesian Belief Tracking for LLM Reasoning Reliability:Separating Calibration from Ranking

Authors: Zhenghan Song , Yunyi Li , Yulong Liu

View a PDF of the paper titled Prefix-Safe Bayesian Belief Tracking for LLM Reasoning Reliability:Separating Calibration from Ranking, by Zhenghan Song and 2 other authors

View PDF HTML (experimental) Abstract:

Long reasoning traces need reliability estimates before final answers are known. We study prefix-conditioned eventual-success estimation, $P(y=1 \mid o_{1:t})$, using prefix-safe observations. Sequential Bayesian Belief Tracking (SBBT) calibrates observation likelihoods and recursively updates a two-state belief, providing a common tracker for scalar scores, text and self-verification markers, hidden clusters, token-pooling probes, and latent-trajectory features. Across generated open-weight traces on MATH-500, GSM8K, AIME 2025, and RIMO-N, probability quality and ranking separate: score-only SBBT often improves Brier, while AUROC gains require structure-aware evidence beyond strong prefix-safe baselines. In the strongest hard math setting, structure-aware observations reach +0.110 AUROC against standard prefix-safe baselines. Under a same-prefix classifier audit, MATH-500 text markers and RIMO-N self-verification signals remain positive. Together, these findings support SBBT as a calibration-aware online inference framework and expose an evidence regime: scalar scores mainly support probability quality, while structure-aware prefix signals support ranking only when strong prefix-safe baselines have not already absorbed the rank evidence.

Subjects: Artificial Intelligence (cs.AI) Cite as: arXiv:2605.27712 [cs.AI] (or arXiv:2605.27712v1 [cs.AI] for this version) https://doi.org/10.48550/arXiv.2605.27712 Focus to learn more arXiv-issued DOI via DataCite (pending registration) Submission history From: Zhenghan Song [ view email ] [v1] Tue, 26 May 2026 21:37:20 UTC (10,795 KB) Full-text links: Access Paper:

View a PDF of the paper titled Prefix-Safe Bayesian Belief Tracking for LLM Reasoning Reliability:Separating Calibration from Ranking, by Zhenghan Song and 2 other authors

View PDF HTML (experimental) TeX Source view license Current browse context: cs.AI < prev | next > new | recent | 2026-05 Change to browse by: cs References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )