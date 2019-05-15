# policial-ads-scraper

The goal of this work is to improve access to information about political advertissement on digital platforms.

Currently it focuses on political advertissement on Facebook. This repository contains a scraper using the facebook Graph API to harvest data about policital advertissement and a backend to serve this data.

## Harveting the Facebook API

Facebook provides access to the list of political advertissements appearing on the platform, from its Graph API. However, this access suffers from a few shortcomings that this work aims at mitigating:
* Access to the ads archive requires a validated app and an account with a confirmed identity. Part of our goal is to deliver a free access to the same data.
* The documentation of the API is currently very terse concerning information about advertisement. We wish that this implementation provides a starting point for other actors.
* The data exposed by the API seems incomplete as of now. For example, the API reports only 2900 political ads on Great Britain while [corresponding report](https://www.facebook.com/ads/library/report/?source=archive-landing-page&country=GB) lists 49000 ads. The scope of the data available using the API is undocumented and tracking this data may improve the shared understanding of that scope.
* Integrity of the data is not guaranteed. Preservation of data enhances its integrity.
