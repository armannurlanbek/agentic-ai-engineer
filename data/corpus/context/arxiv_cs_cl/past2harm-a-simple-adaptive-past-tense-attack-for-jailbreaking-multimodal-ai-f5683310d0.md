---
source: arXiv cs.CL (latest)
source_slug: arxiv_cs_cl
kind: context
content_type: research
url: https://arxiv.org/abs/2605.27545
title: PAST2HARM: A Simple Adaptive Past Tense Attack for Jailbreaking Multimodal AI
published: Thu, 28 May 2026 00:00:00 -0400
---

Computer Science > Computation and Language arXiv:2605.27545 (cs) [Submitted on 26 May 2026] Title: PAST2HARM: A Simple Adaptive Past Tense Attack for Jailbreaking Multimodal AI Authors: Snehasis Mukhopadhyay

View a PDF of the paper titled PAST2HARM: A Simple Adaptive Past Tense Attack for Jailbreaking Multimodal AI, by Snehasis Mukhopadhyay

View PDF Abstract:

Jailbreak attacks on multimodal AI systems remain underexplored, even though unsafe image generation can have more severe consequences than unsafe text and current defenses are relatively immature. We introduce PAST2HARM, a simple yet effective adaptive jailbreak framework that bypasses refusal training in state of the art multimodal text to image models. Building on prior findings that past tense reformulations can evade safeguards, PAST2HARM systematically exploits this vulnerability in multimodal generative AI.

We characterize the attack along two dimensions. First, breadth: through temporal deepening, the framework incrementally strengthens historical anchoring and archival cues, eroding refusal boundaries across models with varying alignment strength. Second, depth: via iterative escalation after initial compliance, we probe the upper bound of harmful generation, measuring severity using a scalar severity jailbreak metric evaluated by a language model acting as a judge. We find that mid conversation turns form peak vulnerability windows, where harmfulness increases before plateauing and eventually undergoing semantic inversion.

We evaluate PAST2HARM on three models Gemini Nano Banana Pro, GPT Image 2, and SD XL achieving attack success rates of 83 percent, 67 percent, and 100 percent in a black box, gradient free setting. Adversarial prompts also transfer across models, with cross model success rates above 50 percent. The attack elicits diverse harmful outputs, including explicit sexual content, political disinformation, historical denial narratives, hate speech, and self harm glorification. We further release a curated benchmark of prompts, reformulations, and outputs as a resource for red teaming and alignment. Our results expose fundamental brittleness in current safeguards and highlight the need for stronger multimodal safety training.

Subjects: Computation and Language (cs.CL) Cite as: arXiv:2605.27545 [cs.CL] (or arXiv:2605.27545v1 [cs.CL] for this version) https://doi.org/10.48550/arXiv.2605.27545 Focus to learn more arXiv-issued DOI via DataCite (pending registration) Submission history From: Snehasis Mukhopadhyay [ view email ] [v1] Tue, 26 May 2026 18:16:22 UTC (10,876 KB) Full-text links: Access Paper:

View a PDF of the paper titled PAST2HARM: A Simple Adaptive Past Tense Attack for Jailbreaking Multimodal AI, by Snehasis Mukhopadhyay

View PDF TeX Source view license Current browse context: cs.CL < prev | next > new | recent | 2026-05 Change to browse by: cs References & Citations NASA ADS Google Scholar Semantic Scholar export BibTeX citation Loading... BibTeX formatted citation × loading... Data provided by: Bookmark Bibliographic Tools Bibliographic and Citation Tools Bibliographic Explorer Toggle Bibliographic Explorer ( What is the Explorer? ) Connected Papers Toggle Connected Papers ( What is Connected Papers? ) Litmaps Toggle Litmaps ( What is Litmaps? ) scite.ai Toggle scite Smart Citations ( What are Smart Citations? ) Code, Data, Media Code, Data and Media Associated with this Article alphaXiv Toggle alphaXiv ( What is alphaXiv? ) Links to Code Toggle CatalyzeX Code Finder for Papers ( What is CatalyzeX? ) DagsHub Toggle DagsHub ( What is DagsHub? ) GotitPub Toggle Gotit.pub ( What is GotitPub? ) Huggingface Toggle Hugging Face ( What is Huggingface? ) ScienceCast Toggle ScienceCast ( What is ScienceCast? ) Demos Demos Replicate Toggle Replicate ( What is Replicate? ) Spaces Toggle Hugging Face Spaces ( What is Spaces? ) Spaces Toggle TXYZ.AI ( What is TXYZ.AI? ) Related Papers Recommenders and Search Tools Link to Influence Flower Influence Flower ( What are Influence Flowers? ) Core recommender toggle CORE Recommender ( What is CORE? ) Author Venue Institution Topic About arXivLabs arXivLabs: experimental projects with community collaborators

arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.

Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.

Have an idea for a project that will add value for arXiv's community? Learn more about arXivLabs . Which authors of this paper are endorsers? | Disable MathJax ( What is MathJax? )