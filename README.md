The goal of this work is to improve access to information about political advertisement on digital platforms.

Currently it focuses on political advertisement on Facebook. This repository contains a scraper using the Facebook Graph API to harvest data from Facebook's [Ads Library](https://www.facebook.com/ads/library/) and a backend to serve this data.

## Harvesting the Facebook API

Facebook [provides API access](https://www.facebook.com/ads/library/api) to the list of political and issue-based advertisements appearing on the platform. However, this access suffers from a few shortcomings that this work aims at mitigating:
* Access to the Ads Archive API requires a validated app and an account with a confirmed identity. Part of our goal is to deliver a free access to the same data: we believe that all citizens should be able to learn about paid political ads, no matter if they have an ID-verified Facebook account or not.
* The documentation of the API is currently very terse concerning information about advertisement. We hope that this implementation saves other actors the time we spent figuring out how it works.
* Integrity of the data is not guaranteed if only one actor serves it. By preserving this data, we can ensure its integrity.

### Relationship with Library reports

For some countries (as of writing US, UK and Brazil), a [public report](https://www.facebook.com/ads/library/report/?source=archive-landing-page&country=GB) is available. Such reports make ads explorable through a web interface, and offer a CSV database as well. Facebook opened their Library for all EU countries mid-April. However, the public report is not available for most. This harvesting and re-exposure of data is thus currently the only way for people without a Facebook account to access the data. This work might thus not be as necessary when such reports are opened for all other countries.

However, we can also say that the data exposed by the API seems incomplete as of now. Indeed, the API reports only 2.900 political ads on Great Britain while the [corresponding report](https://www.facebook.com/ads/library/report/?source=archive-landing-page&country=GB) lists 49.000 ads. The scope of the data available using the API is undocumented and tracking this data may improve the shared understanding of that scope.

### Check the code with flake8

To run flake8 use tox :

```sh
tox
```
