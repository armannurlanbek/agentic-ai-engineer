---
source: Simon Willison
source_slug: simonw
kind: voice
content_type: blog_post
url: https://simonwillison.net/2026/May/23/on-the-dl/#atom-everything
title: On the <dl>
published: 2026-05-23T20:24:48+00:00
---

23rd May 2026 - Link Blog On the <dl> ( via ) I learned a few new-to-me things about the <dl> element from this article by Ben Meyer: A <dt> can be followed by multiple <dd> You can optionally group the <dt> and <dd> elements in a <div> for styling - but only a <div> . You can label them using ARIA. They've been called "description lists", not "definition lists", since an HTML5 draft in 2008 . So this is valid: < h2 id =" credits " > Credits </ h2 > < dl aria-labelledby =" credits " > < div > < dt > Author </ dt > < dd > Jeffrey Zeldman </ dd > < dd > Ethan Marcotte </ dd > </ div > </ dl > Here's a useful note from Adrian Roselli on screen reader support for description lists . Posted 23rd May 2026 at 8:24 pm