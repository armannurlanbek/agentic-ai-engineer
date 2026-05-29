---
source: arXiv cs.AI (latest)
source_slug: arxiv_cs_ai
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27569
title: RULER: Representation-Level Verification of Machine Unlearning
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Artificial Intelligence arXiv:2605.27569 (cs) [Submitted on 26 May 2026] Title: RULER: Representation-Level Verification of Machine Unlearning Authors: Georgina Cosma , Axel Finke

View a PDF of the paper titled RULER: Representation-Level Verification of Machine Unlearning, by Georgina Cosma and Axel Finke

View PDF HTML (experimental) Abstract:

Machine unlearning aims to remove the influence of specific training records from a deployed model without retraining from scratch. Current protocols verify this at the output level through membership inference, retain accuracy, and forget-set accuracy, but a model can satisfy all three whilst still encoding forgotten records in its intermediate representations. We introduce RULER, a set of representation-level verification metrics. The oracle-comparative metric M2 measures whether forget-set records occupy the same representational position as in a model retrained without them. The oracle-free metric M4 detects residuals from the unlearned model's internal similarity structure alone, without retraining. Four approximate unlearning methods all pass output-level evaluation, yet under a linear mixed-effects model M2 detects significant residuals in 10 of 12 conditions (p<0.05), with effect sizes growing as the forget fraction increases. A fifth method, Bad Teacher, shows the same residuals despite a different forgetting mechanism. M4 acts as a pre-unlearning diagnostic across tabular, image, clinical text, and face-identity settings: it detects identity-level memorisation in face recognition models where no tested method fully erases the signal.

Subjects: Artificial Intelligence (cs.AI) Cite as: arXiv:2605.27569 [cs.AI] (or arXiv:2605.27569v1 [cs.AI] for this version) https://doi.org/10.48550/arXiv.2605.27569 Focus to learn more arXiv-issued DOI via DataCite (pending registration) Submission history From: Georgina Cosma Professor [ view email ] [v1] Tue, 26 May 2026 18:41:48 UTC (253 KB) Full-text links: Access Paper:

View a PDF of the paper titled RULER: Representation-Level Verification of Machine Unlearning, by Georgina Cosma and Axel Finke

View PDF HTML (experimental) TeX Source view license Current browse context: cs.AI < prev | next > new | recent | 2026-05 Change to browse by: cs References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )