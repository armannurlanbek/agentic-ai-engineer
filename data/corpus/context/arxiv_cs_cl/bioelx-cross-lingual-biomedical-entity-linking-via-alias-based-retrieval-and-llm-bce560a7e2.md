---
source: arXiv cs.CL (latest)
source_slug: arxiv_cs_cl
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27380
title: BioELX: Cross-lingual Biomedical Entity Linking via Alias-based Retrieval and LLM Ranking
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Computation and Language arXiv:2605.27380 (cs) [Submitted on 9 Apr 2026] Title:

BioELX: Cross-lingual Biomedical Entity Linking via Alias-based Retrieval and LLM Ranking

Authors: Yi Wang , Corina Dima , Liangyu Zhong , Steffen Staab

View a PDF of the paper titled BioELX: Cross-lingual Biomedical Entity Linking via Alias-based Retrieval and LLM Ranking, by Yi Wang and 3 other authors

View PDF HTML (experimental) Abstract:

Cross-lingual biomedical entity linking (BEL) maps mentions in any language to unique identifiers in a biomedical knowledge base (KB), supporting clinical and biomedical NLP applications. However, expert-annotated training data for BEL are costly, especially for low-resource languages. Moreover, many cross-lingual BEL systems rely on SapBERT-based retrievers trained on predominantly English aliases in the KB, leading to poor generalization to unseen non-English mentions and limited context-aware disambiguation. We propose BioELX, a two-stage cross-lingual BEL framework that requires no task-specific annotated training corpora. In Stage~1, we enrich SapBERT training with Wikidata-derived multilingual aliases and use the resulting retriever to improve cross-lingual candidate retrieval. In Stage~2, we perform context-aware disambiguation with a pre-trained LLM ranker that jointly considers the mention context and candidate, eliminating the need for supervised training. Experiments on five benchmarks (XL-BEL, EMEA, Patent, WikiMed-DE, and MedMentions) show that BioELX achieves new state-of-the-art performance. It improves average Recall@1 on XL-BEL by +19.2, with especially large gains for low-resource languages, e.g., +21.6 on Turkish, +22.1 on Korean, +30.8 on Thai, and delivers consistent improvements on EMEA (+6.2), Patent (+5.4), and WikiMed-DE (+12.8). Code and resources will be released upon publication.

Comments: 12 pages, 3 figures Subjects: Computation and Language (cs.CL) ; Artificial Intelligence (cs.AI) Cite as: arXiv:2605.27380 [cs.CL] (or arXiv:2605.27380v1 [cs.CL] for this version) https://doi.org/10.48550/arXiv.2605.27380 Focus to learn more arXiv-issued DOI via DataCite Submission history From: Yi Wang [ view email ] [v1] Thu, 9 Apr 2026 20:07:20 UTC (347 KB) Full-text links: Access Paper:

View a PDF of the paper titled BioELX: Cross-lingual Biomedical Entity Linking via Alias-based Retrieval and LLM Ranking, by Yi Wang and 3 other authors

View PDF HTML (experimental) TeX Source view license Current browse context: cs.CL < prev | next > new | recent | 2026-05 Change to browse by: cs cs.AI References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )