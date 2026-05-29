---
source: arXiv cs.CL (latest)
source_slug: arxiv_cs_cl
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27390
title: EvoSpec: Evolving Speculative Decoding via Real-Time Vocabulary and Parameter AdaptationTarget
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Computation and Language arXiv:2605.27390 (cs) [Submitted on 17 Apr 2026] Title:

EvoSpec: Evolving Speculative Decoding via Real-Time Vocabulary and Parameter AdaptationTarget

Authors: Shuyu Zhang , Lingfeng Pan , Qicheng Wang , Yaqi Shi , Yueyang Tan , Ruyu Yan , Jiaqi Chen , Lixing Du , Lu Wang

View a PDF of the paper titled EvoSpec: Evolving Speculative Decoding via Real-Time Vocabulary and Parameter AdaptationTarget, by Shuyu Zhang and 8 other authors

View PDF HTML (experimental) Abstract:

Speculative decoding accelerates Large Language Model inference via a draft-then-verify paradigm, yet the output projection layer becomes a bottleneck as vocabulary sizes scale. While existing static pruning methods effectively reduce this overhead, they suffer from precipitous drops in acceptance rate in specialized domains or topic-switching scenarios due to their inability to capture dynamic distribution shifts. To address this, we introduce EvoSpec, a framework that enables real-time evolution of the draft model through dynamic vocabulary and parameter adaptation. Unlike static or purely retrieval-based approaches, EvoSpec employs a context-aware mechanism that retrieves critical long-tail tokens via efficient semantic and statistical indexing. Furthermore, we propose a lightweight online alignment strategy utilizing curriculum learning to continually minimize the distributional gap between the draft and target models. Extensive evaluations across specialized domains (coding, law, and medicine) confirm that EvoSpec overcomes the limitations of static baselines. On EAGLE-3, it achieves a 1.13x speedup in these settings over the state-of-the-art static baseline FR-Spec, with 27\% lower memory overhead than standard online adaptation.

Subjects: Computation and Language (cs.CL) ; Artificial Intelligence (cs.AI) Cite as: arXiv:2605.27390 [cs.CL] (or arXiv:2605.27390v1 [cs.CL] for this version) https://doi.org/10.48550/arXiv.2605.27390 Focus to learn more arXiv-issued DOI via DataCite Submission history From: Shuyu Zhang [ view email ] [v1] Fri, 17 Apr 2026 06:16:58 UTC (304 KB) Full-text links: Access Paper:

View a PDF of the paper titled EvoSpec: Evolving Speculative Decoding via Real-Time Vocabulary and Parameter AdaptationTarget, by Shuyu Zhang and 8 other authors

View PDF HTML (experimental) TeX Source view license Current browse context: cs.CL < prev | next > new | recent | 2026-05 Change to browse by: cs cs.AI References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )