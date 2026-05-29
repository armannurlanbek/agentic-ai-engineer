---
source: Simon Willison
source_slug: simonw
kind: voice
content_type: blog_post
url: https://simonwillison.net/2026/May/26/copilot-cowork-exfiltrates-files/#atom-everything
title: Microsoft Copilot Cowork Exfiltrates Files
published: 2026-05-26T15:36:48+00:00
---

26th May 2026 - Link Blog Microsoft Copilot Cowork Exfiltrates Files ( via

) The biggest challenge in designing agentic systems continues to be preventing them from enabling attackers to exfiltrate data.

In this case Microsoft Copilot Cowork (yes, that's a real product name

) was allowing agents to send emails to the user's own inbox without approval... but those messages were then displayed in a way that could leak data to an attacker via rendered images:

Because these messages can contain external images that trigger network requests to external websites, data can be exfiltrated when a user opens a compromised message sent by the agent.

Since OneDrive can create pre-authenticated download links, a successful prompt injection could cause those links to be leaked, allowing files to be downloaded by the attacker.

Posted 26th May 2026 at 3:36 pm