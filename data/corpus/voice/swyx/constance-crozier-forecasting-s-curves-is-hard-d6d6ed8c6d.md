---
source: swyx
source_slug: swyx
kind: voice
content_type: essay
url: https://www.swyx.io/scurves
title: Constance Crozier: Forecasting s-curves is hard
published: Fri, 27 Feb 2026 01:54:50 GMT
---

Constance Crozier: Forecasting s-curves is hard Whoa, we're halfway there? Whoa-ah, living in an S-curve swyx 2026-02-27 There was a famous Covid era chart

that I always struggle to find, showing how hard it is to estimate an S curve while living through it. in the early days it seems that everything is exploding as an exponential and you always get hypey essays about how YOU, YOU DUMB DUMB, DONT UNDERSTAND EXPONENTIALS LET ME EXPLAIN. and then as things hit invisible asymptotes those same loud voices who write viral essays have curiously moved on to other things.

anyway, the following tweet image is not going to do this justice, you should watch the video version:

https://vimeo.com/408599958 or https://x.com/clcrozier/status/1251148890595708938 The author is Constance Crozier, and she had a blogpost to go with it. Here it is in full for googlebots: Forecasting s-curves is hard

S-curves (or sigmoid functions) are commonly used to model the evolution of social or biological systems over time [1]. These functions start with exponential growth, then increase linearly, and finally level off (therefore end up looking like a wonky s). Many things that we think of as exponential functions will actually follow an s-curve (otherwise the system would reach infinity). One famous example is the adoption of a new technology. The graph below shows the percentage of US adults who own a smartphone over time, with a best-fit s-curve imposed on the top. In this case the exponential growth occurs because of the way publicity and supply are rolled out. However, there are only a limited number of potential consumers (some of whom will never get a smartphone) and so the growth gradually slows to zero.

US smartphone ownership [2]

Another example, and the reason that these curves have been back in the news, is the propagation of disease. In this case the exponential growth occurs when the virus is new, such that most people encountering it will not have developed immunity. The level-off occurs because the virus is no longer encountering people without immunity (either due to ‘herd immunity’ or isolation of those infected). The graph below shows the number of deaths in China from the SARS outbreak in 2003, again with a best-fit s-curve.

Deaths due to SARS in China [3]

S-curves have only three parameters, and so it is perhaps impressive that they fit a variety of systems so well. Broadly, the three parameters describe the initial growth rate, the level-off rate, and the value at which it levels-off. Therefore, if you can estimate these three numbers, then you have the trend curve. Many of us will have learnt in school that if there are three parameters to be found, you need three data points to define the function. This would suggest that you could perfectly predict the level-off point based on only three observations (spoiler: you can’t).

In reality, while we can say that the overall trend of the data is likely to fit to some s-curve, the individual points will not all lie along it. This can be seen in both of the previous examples. This discrepancy is often described as ‘modelling error’, which comprises both errors in the measurement of the data, and the fact that the s-curve model is fundamentally wrong. To quote George Box “all models are wrong, but some are useful”.

Intuitively, it makes sense that it should not be possible to forecast the curve from the early data; to assume this, means believing that we can’t affect the outcome. However, in my experience “intuition” and “mathematics” can often be hard to reconcile. Therefore, I decided to investigate how much the “best fit s-curve” changes as more data becomes available. Below is a s-curve that I chose at random. The points shown are “noisy observations” – which is the maths-y way of saying ‘points from the curve with a random amount of error applied’.

In this case, the s-curve model is a perfect fit – I have literally generated the data from an s-curve. This means that if there was zero error then we would only need three points to find the curve. All this to say, that this example is idealistic – in reality there is unlikely to be a curve that fits the data so well. Below is an animation showing the best fit s-curve (found using a least squares optimisation) as more data becomes available.

It may not be surprising that in the exponential growth phase the estimate is very bad, but even in the linear phase (when 40+ points are available) the correct curve has not been found. In fact, it is only once the data starts to level-off that the correct s-curve is found. This is especially unhelpful when you consider that it can be quite hard to tell which part of the curve you on; hindsight is 20-20.

This is not to say that it is impossible to model or predict s-curves. Only that, contextual information about the system you are modelling is likely required. For biological systems, are there physical parameters which govern the initial growth rate? For technological changes, can the final level-off be reasonably estimated? This information is application specific. In other words, data enthusiasts (such as myself) should leave the modelling up to the professionals.

R eferences

[1] Nieto et. al, “Performance analysis of technology using the S curve model: the case for digital signal procession technologies” 1998.

[2] Comscore Whitepaper: ‘The 2016 U.S. Mobile App Report”, September 13, 2016 [3] World Health Organisation https://www.who.int/csr/sars/country/en/ I referenced this 4 years ago in https://www.latent.space/p/ok-foomer and recently strugglled to find it for https://www.latent.space/p/wtf2025 . Per my Three Strikes rule

, it’s time to blog about it, particularly because her website is not loading right now.